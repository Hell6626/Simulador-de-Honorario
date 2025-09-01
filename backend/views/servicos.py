"""
Views para gerenciamento de serviços
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from typing import List
from sqlalchemy import or_

from config import db
from models.servicos import Servico, ServicoRegime
from models.tributario import RegimeTributario, TipoAtividade, AtividadeRegime
from .utils import handle_api_errors, validate_required_fields, paginate_query, build_search_filters

servicos_bp = Blueprint('servicos', __name__)


@servicos_bp.route('/', methods=['GET'])
@jwt_required()
@handle_api_errors
def get_servicos():
    """Busca serviços com filtros e paginação"""
    # Parâmetros de busca
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    categoria = request.args.get('categoria')
    search = request.args.get('search')
    ativo = request.args.get('ativo', 'true').lower() == 'true'
    
    # Query base
    query = Servico.query
    
    # Filtros
    if ativo is not None:
        query = query.filter(Servico.ativo == ativo)
    
    if categoria:
        query = query.filter(Servico.categoria == categoria)
    
    if search:
        search_filters = build_search_filters(Servico, search, ['nome', 'descricao', 'codigo'])
        if search_filters:
            query = query.filter(or_(*search_filters))
    
    # Paginação
    paginated = paginate_query(query, page, per_page)
    
    return jsonify({
        'items': [servico.to_json() for servico in paginated.items],
        'total': paginated.total,
        'pages': paginated.pages,
        'current_page': paginated.page,
        'per_page': paginated.per_page
    })


@servicos_bp.route('/por-regime/<int:regime_id>', methods=['GET'])
@jwt_required()
@handle_api_errors
def get_servicos_por_regime(regime_id: int):
    """Busca serviços compatíveis com o regime tributário"""
    
    regime = RegimeTributario.query.get_or_404(regime_id)
    
    # Aplicar lógica de filtros por regime
    servicos_filtrados = aplicar_filtros_servicos_por_regime(regime.codigo)
    
    return jsonify({
        'regime': {
            'id': regime.id,
            'codigo': regime.codigo,
            'nome': regime.nome
        },
        'items': [servico.to_json() for servico in servicos_filtrados],
        'total': len(servicos_filtrados)
    })


@servicos_bp.route('/para-proposta', methods=['POST'])
@jwt_required()
@handle_api_errors
def get_servicos_para_proposta():
    """
    Retorna serviços disponíveis baseado nas configurações da proposta
    """
    data = request.get_json() or {}
    
    tipo_atividade_id = data.get('tipo_atividade_id')
    regime_tributario_id = data.get('regime_tributario_id')
    
    if not tipo_atividade_id or not regime_tributario_id:
        raise ValueError('tipo_atividade_id e regime_tributario_id são obrigatórios')
    
    # Buscar dados dos relacionamentos
    tipo_atividade = TipoAtividade.query.get_or_404(tipo_atividade_id)
    regime_tributario = RegimeTributario.query.get_or_404(regime_tributario_id)
    
    # Validar se a combinação é válida
    combinacao_valida = AtividadeRegime.query.filter_by(
        tipo_atividade_id=tipo_atividade_id,
        regime_tributario_id=regime_tributario_id,
        ativo=True
    ).first()
    
    if not combinacao_valida:
        return jsonify({
            'error': f'Combinação inválida: {tipo_atividade.nome} com {regime_tributario.nome}',
            'items': [],
            'total': 0
        }), 400
    
    # Filtrar serviços por regime
    servicos_filtrados = aplicar_filtros_servicos_por_regime(regime_tributario.codigo)
    
    # Filtrar adicionalmente por tipo de pessoa se necessário
    if tipo_atividade.aplicavel_pf:
        servicos_filtrados = filtrar_servicos_pessoa_fisica(servicos_filtrados)
    elif tipo_atividade.aplicavel_pj:
        servicos_filtrados = filtrar_servicos_pessoa_juridica(servicos_filtrados)
    
    return jsonify({
        'tipo_atividade': tipo_atividade.to_json(),
        'regime_tributario': regime_tributario.to_json(),
        'items': [servico.to_json() for servico in servicos_filtrados],
        'total': len(servicos_filtrados)
    })


@servicos_bp.route('/<int:servico_id>', methods=['GET'])
@jwt_required()
@handle_api_errors
def get_servico(servico_id: int):
    """Busca um serviço específico"""
    servico = Servico.query.get_or_404(servico_id)
    return jsonify(servico.to_json())


@servicos_bp.route('/', methods=['POST'])
@jwt_required()
@handle_api_errors
def create_servico():
    """Cria um novo serviço"""
    data = request.get_json()
    
    # Validar campos obrigatórios
    required_fields = ['nome', 'categoria', 'valor_base']
    validate_required_fields(data, required_fields)
    
    # Gerar código automaticamente
    codigo = gerar_codigo_servico(data['nome'])
    
    # Criar novo serviço
    servico = Servico(
        codigo=codigo,
        nome=data['nome'],
        categoria=data['categoria'],
        tipo_cobranca=data.get('tipo_cobranca', 'MENSAL'),
        valor_base=data['valor_base'],
        descricao=data.get('descricao'),
        tipo_atividade_id=data.get('tipo_atividade_id'),
        ativo=True
    )
    
    db.session.add(servico)
    db.session.flush()  # Para obter o ID do serviço
    
    # Vincular regimes tributários se fornecidos
    if 'regimes_tributarios' in data and data['regimes_tributarios']:
        for regime_id in data['regimes_tributarios']:
            # Verificar se o regime existe
            regime = RegimeTributario.query.get(regime_id)
            if regime:
                servico_regime = ServicoRegime(
                    servico_id=servico.id,
                    regime_tributario_id=regime_id,
                    ativo=True
                )
                db.session.add(servico_regime)
    
    db.session.commit()
    
    return jsonify(servico.to_json()), 201


@servicos_bp.route('/<int:servico_id>', methods=['PUT'])
@jwt_required()
@handle_api_errors
def update_servico(servico_id: int):
    """Atualiza um serviço existente"""
    servico = Servico.query.get_or_404(servico_id)
    data = request.get_json()
    
    # Atualizar campos
    if 'nome' in data:
        servico.nome = data['nome']
    if 'categoria' in data:
        servico.categoria = data['categoria']
    if 'tipo_cobranca' in data:
        servico.tipo_cobranca = data['tipo_cobranca']
    if 'valor_base' in data:
        servico.valor_base = data['valor_base']
    if 'descricao' in data:
        servico.descricao = data['descricao']
    if 'tipo_atividade_id' in data:
        servico.tipo_atividade_id = data['tipo_atividade_id']
    if 'ativo' in data:
        servico.ativo = data['ativo']
    
    # Atualizar regimes tributários se fornecidos
    if 'regimes_tributarios' in data:
        # Remover vínculos existentes
        ServicoRegime.query.filter_by(servico_id=servico_id).delete()
        
        # Adicionar novos vínculos
        if data['regimes_tributarios']:
            for regime_id in data['regimes_tributarios']:
                # Verificar se o regime existe
                regime = RegimeTributario.query.get(regime_id)
                if regime:
                    servico_regime = ServicoRegime(
                        servico_id=servico_id,
                        regime_tributario_id=regime_id,
                        ativo=True
                    )
                    db.session.add(servico_regime)
    
    db.session.commit()
    
    return jsonify(servico.to_json())


@servicos_bp.route('/regimes-tributarios', methods=['GET'])
@jwt_required()
@handle_api_errors
def get_regimes_tributarios():
    """Retorna regimes tributários filtrados por tipo de atividade"""
    tipo_atividade_id = request.args.get('tipo_atividade_id', type=int)
    
    if not tipo_atividade_id:
        return jsonify({'error': 'tipo_atividade_id é obrigatório'}), 400
    
    try:
        # Buscar regimes tributários que são aplicáveis ao tipo de atividade
        from models.tributario import AtividadeRegime
        
        regimes = db.session.query(RegimeTributario).join(
            AtividadeRegime, 
            AtividadeRegime.regime_tributario_id == RegimeTributario.id
        ).filter(
            AtividadeRegime.tipo_atividade_id == tipo_atividade_id,
            RegimeTributario.ativo == True,
            AtividadeRegime.ativo == True
        ).order_by(RegimeTributario.nome).all()
        
        return jsonify([regime.to_json() for regime in regimes])
        
    except Exception as e:
        current_app.logger.error(f"Erro ao buscar regimes por tipo de atividade: {e}")
        return jsonify({'error': 'Erro interno do servidor'}), 500


@servicos_bp.route('/<int:servico_id>/impacto-exclusao', methods=['GET'])
@jwt_required()
@handle_api_errors
def verificar_impacto_exclusao(servico_id: int):
    """Verifica o impacto da exclusão de um serviço nas propostas"""
    from models.propostas import Proposta, ItemProposta
    
    servico = Servico.query.get_or_404(servico_id)
    
    # Buscar propostas afetadas
    propostas_afetadas = db.session.query(Proposta).join(ItemProposta).filter(
        ItemProposta.servico_id == servico_id,
        Proposta.ativo == True
    ).distinct().all()
    
    propostas_info = []
    for proposta in propostas_afetadas:
        # Calcular valor total do serviço na proposta
        itens_servico = ItemProposta.query.filter_by(
            proposta_id=proposta.id,
            servico_id=servico_id,
            ativo=True
        ).all()
        
        valor_total_servico = sum(item.valor_total for item in itens_servico)
        
        propostas_info.append({
            'id': proposta.id,
            'numero': proposta.numero,
            'cliente_nome': proposta.cliente.nome if proposta.cliente else 'Cliente não encontrado',
            'valor_servico': float(valor_total_servico),
            'quantidade_itens': len(itens_servico)
        })
    
    return jsonify({
        'servico': servico.to_json(),
        'propostas_afetadas': propostas_info,
        'total_propostas': len(propostas_info)
    })


@servicos_bp.route('/<int:servico_id>', methods=['DELETE'])
@jwt_required()
@handle_api_errors
def delete_servico(servico_id: int):
    """Exclui um serviço e remove de todas as propostas"""
    from models.propostas import Proposta, ItemProposta, PropostaLog
    from flask_jwt_extended import get_jwt_identity
    
    servico = Servico.query.get_or_404(servico_id)
    
    # Buscar propostas afetadas
    propostas_afetadas = db.session.query(Proposta).join(ItemProposta).filter(
        ItemProposta.servico_id == servico_id,
        Proposta.ativo == True
    ).distinct().all()
    
    total_propostas_afetadas = len(propostas_afetadas)
    
    # Remover serviço de todas as propostas
    for proposta in propostas_afetadas:
        # Buscar itens do serviço na proposta
        itens_removidos = ItemProposta.query.filter_by(
            proposta_id=proposta.id,
            servico_id=servico_id,
            ativo=True
        ).all()
        
        valor_removido = sum(item.valor_total for item in itens_removidos)
        valor_anterior = proposta.valor_total
        
        # Desativar itens (soft delete)
        for item in itens_removidos:
            item.ativo = False
        
        # Recalcular valor total da proposta
        proposta.valor_total = proposta.valor_total - valor_removido
        
        # Criar log da alteração
        try:
            log = PropostaLog(
                proposta_id=proposta.id,
                funcionario_id=get_jwt_identity(),
                acao='SERVICO_REMOVIDO',
                detalhes=f'Serviço "{servico.nome}" (ID: {servico.id}) removido automaticamente devido à exclusão do serviço do sistema. Valor removido: R$ {valor_removido:.2f}. Itens removidos: {len(itens_removidos)}',
                valor_anterior=valor_anterior,
                valor_atual=proposta.valor_total
            )
            db.session.add(log)
        except Exception as e:
            # Se não conseguir criar o log, continua o processo
            print(f"Erro ao criar log para proposta {proposta.id}: {e}")
    
    # Desativar serviço (soft delete)
    servico.ativo = False
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': f'Serviço "{servico.nome}" excluído com sucesso. {total_propostas_afetadas} proposta(s) foram atualizadas.',
        'propostas_afetadas': total_propostas_afetadas
    }), 200


def gerar_codigo_servico(nome: str) -> str:
    """Gera código único para o serviço baseado no nome"""
    import re
    from datetime import datetime
    
    # Pegar as 3 primeiras letras do nome, apenas letras
    nome_limpo = re.sub(r'[^a-zA-Z]', '', nome.upper())
    prefixo = nome_limpo[:3].ljust(3, 'X')  # Garantir 3 caracteres
    
    # Adicionar timestamp para unicidade
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')[-6:]  # Últimos 6 dígitos
    
    return f"{prefixo}{timestamp}"


def aplicar_filtros_servicos_por_regime(codigo_regime: str) -> List[Servico]:
    """
    Aplica filtros de serviços baseado no código do regime tributário
    Usa a tabela servico_regime para determinar compatibilidade
    
    Args:
        codigo_regime: Código do regime (MEI, SN, LP, LR, PR, Aut, DOM, CAT)
    
    Returns:
        List[Servico]: Lista de serviços compatíveis
    """
    # ⚠️ BUSCAR: Regime pelo código
    regime = RegimeTributario.query.filter_by(codigo=codigo_regime).first()
    if not regime:
        return []
    
    # ⚠️ BUSCAR: Serviços através da tabela servico_regime
    servicos_regime = ServicoRegime.query.filter_by(
        regime_tributario_id=regime.id,
        ativo=True
    ).all()
    
    # ⚠️ EXTRAIR: IDs dos serviços compatíveis
    servicos_ids = [sr.servico_id for sr in servicos_regime]
    
    # ⚠️ BUSCAR: Serviços ativos
    if servicos_ids:
        servicos = Servico.query.filter(
            Servico.id.in_(servicos_ids),
            Servico.ativo == True
        ).all()
    else:
        servicos = []
    
    return servicos


# ⚠️ REMOVIDO: Funções de filtro antigas - agora usando tabela servico_regime


def filtrar_servicos_pessoa_fisica(servicos: List[Servico]) -> List[Servico]:
    """Filtrar serviços aplicáveis para Pessoa Física"""
    # PF: Remover serviços exclusivos de PJ
    return [s for s in servicos if s.categoria not in ['SOCIETARIO']]


def filtrar_servicos_pessoa_juridica(servicos: List[Servico]) -> List[Servico]:
    """Filtrar serviços aplicáveis para Pessoa Jurídica"""
    # PJ: Todos os serviços são aplicáveis
    return servicos

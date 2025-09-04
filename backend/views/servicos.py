"""
Views para gerenciamento de serviços
"""

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required

from sqlalchemy import or_

from config import db
from models.servicos import Servico, ServicoRegime
from models.tributario import RegimeTributario
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
    """Retorna serviços disponíveis para um regime tributário específico"""
    
    # Verificar se o regime existe
    regime = RegimeTributario.query.get_or_404(regime_id)
    
    # ✅ IMPLEMENTAR: Query para buscar serviços vinculados ao regime
    # Assumindo que existe uma tabela de relacionamento servico_regime
    servicos = db.session.query(Servico)\
        .join(ServicoRegime)\
        .filter(
            ServicoRegime.regime_tributario_id == regime_id,
            ServicoRegime.ativo == True,
            Servico.ativo == True
        )\
        .order_by(Servico.categoria, Servico.nome)\
        .all()
    
    current_app.logger.info(f"Encontrados {len(servicos)} serviços para regime {regime.codigo}")
    
    return jsonify({
        'regime': regime.to_json(),
        'servicos': [s.to_json() for s in servicos],
        'total': len(servicos)
    })


@servicos_bp.route('/para-proposta', methods=['POST'])
@jwt_required()
@handle_api_errors
def get_servicos_para_proposta():
    """
    Retorna todos os serviços ativos (simplificado)
    """
    # Retornar todos os serviços ativos
    servicos = Servico.query.filter(Servico.ativo == True).all()
    
    return jsonify({
        'items': [servico.to_json() for servico in servicos],
        'total': len(servicos)
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
    """Atualiza um serviço existente com versionamento"""
    from datetime import datetime
    
    servico_atual = Servico.query.get_or_404(servico_id)
    data = request.get_json()
    
    try:
        # ✅ IMPLEMENTAR: Sistema de versionamento
        # 1. Desativar o serviço atual
        servico_atual.ativo = False
        servico_atual.data_desativacao = datetime.utcnow()
        
        # 2. Criar novo serviço com dados atualizados
        novo_servico = Servico(
            codigo=servico_atual.codigo,  # Manter mesmo código
            nome=data.get('nome', servico_atual.nome),
            categoria=data.get('categoria', servico_atual.categoria),
            valor_base=data.get('valor_base', servico_atual.valor_base),
            descricao=data.get('descricao', servico_atual.descricao),
            tipo_cobranca=data.get('tipo_cobranca', servico_atual.tipo_cobranca),
            versao_anterior_id=servico_atual.id,  # ✅ Referência ao serviço anterior
            ativo=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        db.session.add(novo_servico)
        db.session.flush()  # Para obter o ID do novo serviço
        
        # 3. Atualizar relacionamentos de regimes tributários
        if 'regimes_tributarios' in data:
            # Remover vínculos existentes do serviço atual
            ServicoRegime.query.filter_by(servico_id=servico_id).delete()
            
            # Adicionar novos vínculos para o novo serviço
            if data['regimes_tributarios']:
                for regime_id in data['regimes_tributarios']:
                    # Verificar se o regime existe
                    regime = RegimeTributario.query.get(regime_id)
                    if regime:
                        servico_regime = ServicoRegime(
                            servico_id=novo_servico.id,
                            regime_tributario_id=regime_id,
                            ativo=True
                        )
                        db.session.add(servico_regime)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Serviço atualizado com sucesso',
            'servico': novo_servico.to_json(),
            'versao_anterior': servico_atual.to_json()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        raise ValueError(f'Erro ao atualizar serviço: {str(e)}')


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




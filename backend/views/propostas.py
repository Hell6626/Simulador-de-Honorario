"""
Views relacionadas às propostas.
"""

from flask import Blueprint, request, jsonify, current_app
from sqlalchemy import or_
from datetime import datetime
from flask_jwt_extended import jwt_required, get_jwt_identity
import json

from config import db
from models import Proposta, Funcionario, Cliente, ItemProposta, Servico, PropostaLog, RegimeTributario
from .utils import handle_api_errors, validate_required_fields, paginate_query

propostas_bp = Blueprint('propostas', __name__)

def calcular_taxa_abertura_empresa(cliente_abertura: bool, regime_codigo: str) -> float:
    """
    Calcula taxa de abertura de empresa
    
    Args:
        cliente_abertura: Se o cliente é abertura de empresa (tabela cliente.abertura_empresa)
        regime_codigo: Código do regime tributário
        
    Returns:
        float: Valor da taxa (MEI: R$ 300, Outros: R$ 1.000, Cliente existente: R$ 0)
    """
    if not cliente_abertura:
        return 0.0
    
    # ⚠️ REGRA CORRIGIDA: MEI = R$ 300, outros = R$ 1.000
    if regime_codigo and regime_codigo.upper() == 'MEI':
        return 300.0
    else:
        return 1000.0


def obter_dados_completos_proposta(proposta_id: int) -> dict:
    """Obtém dados completos da proposta para cálculos"""
    proposta = Proposta.query.get_or_404(proposta_id)
    
    # ⚠️ BUSCAR: Dados necessários com relacionamentos
    cliente = proposta.cliente
    regime = proposta.regime_tributario
    
    # ⚠️ CALCULAR: Valor dos serviços
    valor_servicos = sum(float(item.valor_total) for item in proposta.itens if item.ativo)
    
    # ⚠️ CALCULAR: Taxa de abertura
    taxa_abertura = calcular_taxa_abertura_empresa(
        cliente.abertura_empresa if cliente else False,
        regime.codigo if regime else ''
    )
    
    # ⚠️ VALOR BASE: Serviços + Taxa de abertura
    valor_base = valor_servicos + taxa_abertura
    
    # ⚠️ CALCULAR: Desconto real (Base - Valor Final)
    valor_final = float(proposta.valor_total)
    desconto_valor = valor_base - valor_final
    desconto_percentual = (desconto_valor / valor_base * 100) if valor_base > 0 else 0
    
    return {
        'proposta': proposta,
        'cliente_abertura': cliente.abertura_empresa if cliente else False,
        'regime_codigo': regime.codigo if regime else '',
        'valor_servicos': valor_servicos,
        'taxa_abertura': taxa_abertura,
        'valor_base': valor_base,
        'valor_final': valor_final,
        'desconto_valor': desconto_valor,
        'desconto_percentual': desconto_percentual
    }


@propostas_bp.route('/', methods=['GET'])
@handle_api_errors
def get_propostas():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    status = request.args.get('status')
    cliente_id = request.args.get('cliente_id', type=int)
    funcionario_id = request.args.get('funcionario_id', type=int)
    search = request.args.get('search', '').strip()

    query = Proposta.query.filter(Proposta.ativo == True)

    if status:
        query = query.filter(Proposta.status == status.upper())
    if cliente_id:
        query = query.filter(Proposta.cliente_id == cliente_id)
    if funcionario_id:
        query = query.filter(Proposta.funcionario_responsavel_id == funcionario_id)
    if search:
        query = query.filter(
            or_(
                Proposta.numero.ilike(f'%{search}%'),
                Proposta.observacoes.ilike(f'%{search}%')
            )
        )

    propostas = paginate_query(query.order_by(Proposta.created_at.desc()), page, per_page)

    data = [p.to_json() for p in propostas.items]
    return jsonify({
        'items': data,
        'propostas': data,
        'total': propostas.total,
        'pages': propostas.pages,
        'current_page': page,
        'per_page': per_page
    })

@propostas_bp.route('/<int:proposta_id>', methods=['GET'])
@handle_api_errors  
def get_proposta(proposta_id: int):
    """Busca uma proposta específica com dados completos"""
    
    # ⚠️ BUSCAR: Dados completos com cálculos corretos
    dados_completos = obter_dados_completos_proposta(proposta_id)
    proposta = dados_completos['proposta']
    
    # ⚠️ PREPARAR: Resposta com dados enriquecidos
    resposta = proposta.to_json()
    
    # ⚠️ ADICIONAR: Informações de taxa de abertura
    resposta['taxa_abertura'] = {
        'aplicavel': dados_completos['cliente_abertura'],
        'valor': dados_completos['taxa_abertura'],
        'motivo': (
            f"Taxa de abertura MEI (R$ 300)" if dados_completos['regime_codigo'].upper() == 'MEI'
            else f"Taxa de abertura empresa (R$ 1.000)"
        ) if dados_completos['cliente_abertura'] else None
    }
    
    # ⚠️ ADICIONAR: Resumo financeiro completo
    resposta['resumo_financeiro'] = {
        'valor_servicos': dados_completos['valor_servicos'],
        'taxa_abertura': dados_completos['taxa_abertura'],
        'valor_base': dados_completos['valor_base'],  # Serviços + Taxa
        'valor_final': dados_completos['valor_final'],
        'desconto_valor': dados_completos['desconto_valor'],
        'desconto_percentual': dados_completos['desconto_percentual'],
        'desconto_tipo': (
            'desconto' if dados_completos['desconto_valor'] > 0 else
            'acrescimo' if dados_completos['desconto_valor'] < 0 else 'sem_desconto'
        )
    }
    
    current_app.logger.info(
        f"Proposta {proposta_id} consultada - "
        f"Serviços: R$ {dados_completos['valor_servicos']:.2f}, "
        f"Taxa abertura: R$ {dados_completos['taxa_abertura']:.2f}, "
        f"Base: R$ {dados_completos['valor_base']:.2f}, "
        f"Final: R$ {dados_completos['valor_final']:.2f}, "
        f"Desconto: R$ {dados_completos['desconto_valor']:.2f}"
    )
    
    return jsonify(resposta)

@propostas_bp.route('/', methods=['POST'])
@jwt_required()
@handle_api_errors
def create_proposta():
    data = request.get_json() or {}
    funcionario_id = int(get_jwt_identity())

    # Validação de campos obrigatórios
    validation_error = validate_required_fields(data, ['cliente_id', 'tipo_atividade_id', 'regime_tributario_id'])
    if validation_error:
        return validation_error
    
    # Verificar se funcionário existe e está ativo
    funcionario = Funcionario.query.get(funcionario_id)
    if not funcionario or not funcionario.ativo:
        raise ValueError('Funcionário não encontrado')

    # Verificar se cliente existe e está ativo
    cliente = Cliente.query.get(data['cliente_id'])
    if not cliente:
        raise ValueError('Cliente não encontrado')
    if not cliente.ativo:
        raise ValueError('Cliente está inativo')

    # Gerar número da proposta
    numero_proposta = data.get('numero', f"PROP-{datetime.now().strftime('%Y%m%d%H%M%S')}")

    # Criar proposta
    proposta = Proposta(
        numero=numero_proposta,
        cliente_id=data['cliente_id'],
        funcionario_responsavel_id=funcionario_id,
        tipo_atividade_id=data['tipo_atividade_id'],
        regime_tributario_id=data['regime_tributario_id'],
        faixa_faturamento_id=data.get('faixa_faturamento_id'),
        valor_total=data.get('valor_total', 0),
        data_validade=datetime.fromisoformat(data.get('data_validade')) if data.get('data_validade') else datetime.now(),
        status=data.get('status', 'RASCUNHO'),
        observacoes=(data.get('observacoes') or '').strip() or None,
    )
    db.session.add(proposta)
    db.session.flush()  # Para obter o ID da proposta

    # Criar itens da proposta se fornecidos
    if 'itens' in data and isinstance(data['itens'], list):
        for item_data in data['itens']:
            # Verificar se o serviço existe
            servico = Servico.query.get(item_data['servico_id'])
            if not servico:
                raise ValueError(f'Serviço com ID {item_data["servico_id"]} não encontrado')
            
            item = ItemProposta(
                proposta_id=proposta.id,
                servico_id=item_data['servico_id'],
                quantidade=item_data.get('quantidade', 1),
                valor_unitario=item_data['valor_unitario'],
                valor_total=item_data['valor_total'],
                descricao_personalizada=item_data.get('descricao_personalizada')
            )
            db.session.add(item)

    db.session.commit()

    current_app.logger.info(
        f"Proposta criada: #{proposta.numero} "
        f"(ID: {proposta.id}, Cliente: {cliente.nome})"
    )
    return jsonify(proposta.to_json()), 201

@propostas_bp.route('/<int:proposta_id>', methods=['PUT'])
@jwt_required()
@handle_api_errors
def update_proposta(proposta_id: int):
    proposta = Proposta.query.get_or_404(proposta_id)
    data = request.get_json() or {}
    funcionario_id = int(get_jwt_identity())
    
    # ⚠️ CAPTURAR: Dados antigos para comparação
    dados_antigos = capturar_dados_atuais(proposta)
    
    # ⚠️ APLICAR: Alterações na proposta
    alteracoes_realizadas = []
    
    # Status
    if 'status' in data and data['status'] != proposta.status:
        old_status = proposta.status
        proposta.status = data['status'].upper()
        alteracoes_realizadas.append({
            'campo': 'status',
            'valor_anterior': old_status,
            'valor_novo': proposta.status
        })
    
    # Configurações tributárias
    if 'tipo_atividade_id' in data and data['tipo_atividade_id'] != proposta.tipo_atividade_id:
        alteracoes_realizadas.append({
            'campo': 'tipo_atividade_id',
            'valor_anterior': proposta.tipo_atividade_id,
            'valor_novo': data['tipo_atividade_id']
        })
        proposta.tipo_atividade_id = data['tipo_atividade_id']
    
    if 'regime_tributario_id' in data and data['regime_tributario_id'] != proposta.regime_tributario_id:
        alteracoes_realizadas.append({
            'campo': 'regime_tributario_id',
            'valor_anterior': proposta.regime_tributario_id,
            'valor_novo': data['regime_tributario_id']
        })
        proposta.regime_tributario_id = data['regime_tributario_id']
    
    if 'faixa_faturamento_id' in data and data['faixa_faturamento_id'] != proposta.faixa_faturamento_id:
        alteracoes_realizadas.append({
            'campo': 'faixa_faturamento_id',
            'valor_anterior': proposta.faixa_faturamento_id,
            'valor_novo': data['faixa_faturamento_id']
        })
        proposta.faixa_faturamento_id = data['faixa_faturamento_id']
    
    # Valor total
    if 'valor_total' in data and float(data['valor_total']) != float(proposta.valor_total):
        alteracoes_realizadas.append({
            'campo': 'valor_total',
            'valor_anterior': float(proposta.valor_total),
            'valor_novo': float(data['valor_total'])
        })
        proposta.valor_total = data['valor_total']
    
    # Observações
    if 'observacoes' in data:
        obs_nova = (data['observacoes'] or '').strip() or None
        if obs_nova != proposta.observacoes:
            alteracoes_realizadas.append({
                'campo': 'observacoes',
                'valor_anterior': proposta.observacoes or '',
                'valor_novo': obs_nova or ''
            })
            proposta.observacoes = obs_nova
    
    # Data de validade
    if 'data_validade' in data:
        nova_validade = datetime.fromisoformat(data['data_validade']) if data['data_validade'] else None
        if nova_validade != proposta.data_validade:
            alteracoes_realizadas.append({
                'campo': 'data_validade',
                'valor_anterior': proposta.data_validade.isoformat() if proposta.data_validade else None,
                'valor_novo': nova_validade.isoformat() if nova_validade else None
            })
            proposta.data_validade = nova_validade
    
    # ⚠️ ITENS: Comparar e atualizar serviços
    itens_alterados = False
    if 'itens' in data:
        itens_alterados = processar_itens_proposta(proposta, data['itens'], alteracoes_realizadas)
    
    # ⚠️ SALVAR: Alterações no banco
    try:
        db.session.commit()
        current_app.logger.info(f"Proposta {proposta_id} salva com sucesso")
        
        # ⚠️ CRIAR: Logs das alterações
        if alteracoes_realizadas:
            criar_logs_alteracoes(proposta.id, funcionario_id, alteracoes_realizadas)
            current_app.logger.info(f"Criados {len(alteracoes_realizadas)} logs de alteração")
        
        # ⚠️ LOG: Especial para finalização
        if data.get('status') == 'REALIZADA':
            criar_log_especifico(
                proposta.id, 
                funcionario_id, 
                'PROPOSTA_FINALIZADA',
                f'Proposta finalizada com valor total de R$ {float(proposta.valor_total):.2f}'
            )
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Erro ao salvar proposta {proposta_id}: {str(e)}")
        raise e
    
    # ⚠️ RETORNAR: Proposta atualizada com cálculos corretos
    dados_atualizados = obter_dados_completos_proposta(proposta_id)
    resposta = proposta.to_json()
    
    # ⚠️ INCLUIR: Dados financeiros calculados
    resposta['taxa_abertura'] = {
        'aplicavel': dados_atualizados['cliente_abertura'],
        'valor': dados_atualizados['taxa_abertura'],
        'motivo': (
            f"Taxa de abertura MEI (R$ 300)" if dados_atualizados['regime_codigo'].upper() == 'MEI'
            else f"Taxa de abertura empresa (R$ 1.000)"
        ) if dados_atualizados['cliente_abertura'] else None
    }
    
    resposta['resumo_financeiro'] = {
        'valor_servicos': dados_atualizados['valor_servicos'],
        'taxa_abertura': dados_atualizados['taxa_abertura'],
        'valor_base': dados_atualizados['valor_base'],
        'valor_final': dados_atualizados['valor_final'],
        'desconto_valor': dados_atualizados['desconto_valor'],
        'desconto_percentual': dados_atualizados['desconto_percentual'],
        'desconto_tipo': (
            'desconto' if dados_atualizados['desconto_valor'] > 0 else
            'acrescimo' if dados_atualizados['desconto_valor'] < 0 else 'sem_desconto'
        )
    }
    
    current_app.logger.info(
        f"Proposta {proposta_id} atualizada - "
        f"Taxa: R$ {dados_atualizados['taxa_abertura']:.2f}, "
        f"Base: R$ {dados_atualizados['valor_base']:.2f}, "
        f"Final: R$ {dados_atualizados['valor_final']:.2f}"
    )
    
    return jsonify(resposta)

def capturar_dados_atuais(proposta: Proposta) -> dict:
    """Captura o estado atual da proposta para comparação"""
    return {
        'status': proposta.status,
        'tipo_atividade_id': proposta.tipo_atividade_id,
        'regime_tributario_id': proposta.regime_tributario_id,
        'faixa_faturamento_id': proposta.faixa_faturamento_id,
        'valor_total': float(proposta.valor_total),
        'observacoes': proposta.observacoes,
        'data_validade': proposta.data_validade.isoformat() if proposta.data_validade else None,
        'itens': [(item.servico_id, item.quantidade, float(item.valor_unitario), float(item.valor_total)) 
                  for item in proposta.itens if item.ativo]
    }

def atualizar_itens_proposta(proposta: Proposta, novos_itens: list, alteracoes_realizadas: list) -> bool:
    """Atualiza os itens da proposta e registra alterações"""
    # ⚠️ CAPTURAR: Itens atuais
    itens_atuais = {item.servico_id: item for item in proposta.itens if item.ativo}
    novos_itens_dict = {item['servico_id']: item for item in novos_itens if item['servico_id'] > 0}
    
    alteracoes_itens = {
        'itens_removidos': [],
        'itens_adicionados': [],
        'itens_alterados': []
    }
    
    # ⚠️ VERIFICAR: Itens removidos
    for servico_id, item_atual in itens_atuais.items():
        if servico_id not in novos_itens_dict:
            item_atual.ativo = False  # Soft delete
            alteracoes_itens['itens_removidos'].append({
                'servico_id': servico_id,
                'nome': item_atual.servico.nome if hasattr(item_atual, 'servico') else f'Serviço {servico_id}',
                'quantidade': float(item_atual.quantidade),
                'valor_total': float(item_atual.valor_total)
            })
    
    # ⚠️ VERIFICAR: Itens novos e alterados
    for servico_id, novo_item in novos_itens_dict.items():
        if servico_id in itens_atuais:
            # Item existente - verificar alterações
            item_atual = itens_atuais[servico_id]
            alteracoes_item = {}
            
            if float(novo_item['quantidade']) != float(item_atual.quantidade):
                alteracoes_item['quantidade'] = {
                    'anterior': float(item_atual.quantidade),
                    'novo': float(novo_item['quantidade'])
                }
                item_atual.quantidade = novo_item['quantidade']
            
            if float(novo_item['valor_unitario']) != float(item_atual.valor_unitario):
                alteracoes_item['valor_unitario'] = {
                    'anterior': float(item_atual.valor_unitario),
                    'novo': float(novo_item['valor_unitario'])
                }
                item_atual.valor_unitario = novo_item['valor_unitario']
            
            if float(novo_item['valor_total']) != float(item_atual.valor_total):
                alteracoes_item['valor_total'] = {
                    'anterior': float(item_atual.valor_total),
                    'novo': float(novo_item['valor_total'])
                }
                item_atual.valor_total = novo_item['valor_total']
            
            if novo_item.get('descricao_personalizada') != item_atual.descricao_personalizada:
                alteracoes_item['descricao_personalizada'] = {
                    'anterior': item_atual.descricao_personalizada or '',
                    'novo': novo_item.get('descricao_personalizada') or ''
                }
                item_atual.descricao_personalizada = novo_item.get('descricao_personalizada')
            
            if alteracoes_item:
                alteracoes_itens['itens_alterados'].append({
                    'servico_id': servico_id,
                    'nome': item_atual.servico.nome if hasattr(item_atual, 'servico') else f'Serviço {servico_id}',
                    'alteracoes': alteracoes_item
                })
        else:
            # Item novo
            novo_item_obj = ItemProposta(
                proposta_id=proposta.id,
                servico_id=novo_item['servico_id'],
                quantidade=novo_item['quantidade'],
                valor_unitario=novo_item['valor_unitario'],
                valor_total=novo_item['valor_total'],
                descricao_personalizada=novo_item.get('descricao_personalizada')
            )
            db.session.add(novo_item_obj)
            
            alteracoes_itens['itens_adicionados'].append({
                'servico_id': servico_id,
                'quantidade': float(novo_item['quantidade']),
                'valor_unitario': float(novo_item['valor_unitario']),
                'valor_total': float(novo_item['valor_total'])
            })
    
    # ⚠️ REGISTRAR: Alterações nos itens se houver
    if any([alteracoes_itens['itens_removidos'], alteracoes_itens['itens_adicionados'], alteracoes_itens['itens_alterados']]):
        alteracoes_realizadas.append({
            'campo': 'itens_proposta',
            'detalhes': alteracoes_itens
        })
        return True
    
    return False

def criar_logs_alteracoes(proposta_id: int, funcionario_id: int, alteracoes: list):
    """Cria logs detalhados das alterações realizadas"""
    
    # ⚠️ LOG: Geral da edição
    detalhes_gerais = {
        'total_alteracoes': len(alteracoes),
        'campos_alterados': [alt['campo'] for alt in alteracoes],
        'timestamp': datetime.now().isoformat()
    }
    
    log_geral = PropostaLog(
        proposta_id=proposta_id,
        funcionario_id=funcionario_id,
        acao='PROPOSTA_EDITADA',
        detalhes=json.dumps(detalhes_gerais, ensure_ascii=False)
    )
    db.session.add(log_geral)
    
    # ⚠️ LOGS: Específicos por tipo de alteração
    for alteracao in alteracoes:
        if alteracao['campo'] == 'status':
            criar_log_especifico(
                proposta_id, funcionario_id, 'STATUS_ALTERADO',
                f"Status alterado de '{alteracao['valor_anterior']}' para '{alteracao['valor_novo']}'"
            )
        
        elif alteracao['campo'] in ['tipo_atividade_id', 'regime_tributario_id', 'faixa_faturamento_id']:
            criar_log_especifico(
                proposta_id, funcionario_id, 'CONFIGURACOES_ALTERADAS',
                json.dumps({
                    'campo': alteracao['campo'],
                    'valor_anterior': alteracao['valor_anterior'],
                    'valor_novo': alteracao['valor_novo']
                }, ensure_ascii=False)
            )
        
        elif alteracao['campo'] == 'valor_total':
            # Identificar se é alteração de desconto
            diferenca = alteracao['valor_novo'] - alteracao['valor_anterior']
            criar_log_especifico(
                proposta_id, funcionario_id, 'DESCONTO_ALTERADO',
                f"Valor total alterado de R$ {alteracao['valor_anterior']:.2f} para R$ {alteracao['valor_novo']:.2f} (diferença: R$ {diferenca:.2f})"
            )
        
        elif alteracao['campo'] == 'itens_proposta':
            criar_log_especifico(
                proposta_id, funcionario_id, 'SERVICOS_ALTERADOS',
                json.dumps(alteracao['detalhes'], ensure_ascii=False)
            )
        
        elif alteracao['campo'] == 'observacoes':
            criar_log_especifico(
                proposta_id, funcionario_id, 'OBSERVACOES_ALTERADAS',
                f"Observações atualizadas (tamanho: {len(alteracao['valor_anterior'])} → {len(alteracao['valor_novo'])} caracteres)"
            )
    
    db.session.commit()

def criar_log_especifico(proposta_id: int, funcionario_id: int, acao: str, detalhes: str):
    """Cria um log específico"""
    
    log = PropostaLog(
        proposta_id=proposta_id,
        funcionario_id=funcionario_id,
        acao=acao,
        detalhes=detalhes
    )
    db.session.add(log)

@propostas_bp.route('/<int:proposta_id>/logs', methods=['GET'])
@handle_api_errors
def get_logs_proposta(proposta_id: int):
    """Busca o histórico de logs de uma proposta"""
    proposta = Proposta.query.get_or_404(proposta_id)
    
    logs = PropostaLog.query.filter_by(proposta_id=proposta_id)\
                            .order_by(PropostaLog.created_at.desc())\
                            .all()
    
    logs_formatados = []
    for log in logs:
        log_data = log.to_json()
        
        # ⚠️ ENRIQUECER: Dados do funcionário
        funcionario = Funcionario.query.get(log.funcionario_id)
        if funcionario:
            log_data['funcionario'] = {
                'id': funcionario.id,
                'nome': funcionario.nome,
                'email': funcionario.email
            }
        
        # ⚠️ FORMATAR: Detalhes se for JSON
        try:
            if log.detalhes and log.detalhes.startswith('{'):
                log_data['detalhes_formatados'] = json.loads(log.detalhes)
            else:
                log_data['detalhes_formatados'] = log.detalhes
        except json.JSONDecodeError:
            log_data['detalhes_formatados'] = log.detalhes
        
        logs_formatados.append(log_data)
    
    return jsonify({
        'proposta_id': proposta_id,
        'proposta_numero': proposta.numero,
        'total_logs': len(logs_formatados),
        'logs': logs_formatados
    })

@propostas_bp.route('/<int:proposta_id>/calcular-servicos', methods=['POST'])
@handle_api_errors
def calcular_servicos_proposta(proposta_id: int):
    proposta = Proposta.query.get_or_404(proposta_id)
    # TODO: Implementar cálculo de serviços automáticos
    current_app.logger.info(f"Serviços calculados para proposta #{proposta.numero}")
    return jsonify({'message': 'Serviços calculados com sucesso', 'proposta': proposta.to_json()})

@propostas_bp.route('/<int:proposta_id>/finalizar', methods=['POST'])
@handle_api_errors
def finalizar_proposta(proposta_id: int):
    """Finaliza uma proposta sem requerer autenticação JWT"""
    current_app.logger.info(f"Recebida requisição para finalizar proposta {proposta_id}")
    current_app.logger.info(f"Headers: {dict(request.headers)}")
    current_app.logger.info(f"Data: {request.get_json()}")
    
    proposta = Proposta.query.get(proposta_id)
    
    # Se a proposta não existir, retornar erro 404
    if not proposta:
        current_app.logger.error(f"Proposta {proposta_id} não encontrada")
        return jsonify({'error': 'Proposta não encontrada'}), 404
    
    data = request.get_json() or {}

    try:
        # ⚠️ VERIFICAR: Se a proposta já está finalizada
        if proposta.status in ['REALIZADA', 'APROVADA']:
            current_app.logger.warning(f"Proposta {proposta_id} já está finalizada com status: {proposta.status}")
            return jsonify({
                'error': 'Proposta já está finalizada',
                'status_atual': proposta.status
            }), 409
        
        # Atualizar campos da proposta
        alteracoes = []
        
        if 'valor_total' in data and float(data['valor_total']) != float(proposta.valor_total):
            alteracoes.append(f"valor_total: {proposta.valor_total} -> {data['valor_total']}")
            proposta.valor_total = data['valor_total']
            
        if 'status' in data and data['status'] != proposta.status:
            alteracoes.append(f"status: {proposta.status} -> {data['status']}")
            proposta.status = data['status']
            
        if 'observacoes' in data:
            obs_nova = (data['observacoes'] or '').strip() or None
            if obs_nova != proposta.observacoes:
                alteracoes.append("observacoes atualizadas")
                proposta.observacoes = obs_nova

        # ⚠️ SALVAR: Apenas se houve alterações
        if alteracoes:
            db.session.commit()
            current_app.logger.info(
                f"Proposta finalizada: #{proposta.numero} "
                f"(ID: {proposta.id}, Status: {proposta.status}, Alterações: {', '.join(alteracoes)})"
            )
        else:
            current_app.logger.info(
                f"Proposta {proposta_id} finalizada sem alterações - status atual: {proposta.status}"
            )
        
        return jsonify(proposta.to_json())
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Erro ao finalizar proposta {proposta_id}: {str(e)}")
        return jsonify({'error': f'Erro interno ao finalizar proposta: {str(e)}'}), 500

@propostas_bp.route('/<int:proposta_id>', methods=['DELETE'])
@jwt_required()
@handle_api_errors
def delete_proposta(proposta_id: int):
    """Soft delete de uma proposta - marca como inativa"""
    proposta = Proposta.query.get_or_404(proposta_id)
    funcionario_id = int(get_jwt_identity())

    # Verificar se funcionário existe e está ativo
    funcionario = Funcionario.query.get(funcionario_id)
    if not funcionario or not funcionario.ativo:
        raise ValueError('Funcionário não encontrado')

    # Soft delete - marcar como inativa
    proposta.ativo = False
    db.session.commit()

    current_app.logger.info(
        f"Proposta marcada como inativa: #{proposta.numero} "
        f"(ID: {proposta.id}, Funcionário: {funcionario.nome})"
    )
    return jsonify({'message': 'Proposta excluída com sucesso'})


def processar_itens_proposta(proposta: Proposta, novos_itens: list, alteracoes_realizadas: list) -> bool:
    """Processa a atualização dos itens da proposta"""
    from models.propostas import ItemProposta
    
    current_app.logger.info(f"Processando {len(novos_itens)} itens para proposta {proposta.id}")
    
    # ⚠️ DESATIVAR: Todos os itens atuais (soft delete)
    itens_atuais = ItemProposta.query.filter_by(proposta_id=proposta.id, ativo=True).all()
    for item in itens_atuais:
        item.ativo = False
        current_app.logger.info(f"Item {item.id} desativado")
    
    # ⚠️ CRIAR: Novos itens
    itens_criados = []
    valor_total_itens = 0
    
    for item_data in novos_itens:
        if not item_data.get('servico_id') or item_data['servico_id'] <= 0:
            current_app.logger.warning(f"Item ignorado - servico_id inválido: {item_data}")
            continue
            
        try:
            novo_item = ItemProposta(
                proposta_id=proposta.id,
                servico_id=item_data['servico_id'],
                quantidade=float(item_data.get('quantidade', 1)),
                valor_unitario=float(item_data.get('valor_unitario', 0)),
                valor_total=float(item_data.get('valor_total', 0)),
                descricao_personalizada=item_data.get('descricao_personalizada'),
                ativo=True
            )
            
            db.session.add(novo_item)
            itens_criados.append(novo_item)
            valor_total_itens += novo_item.valor_total
            
            current_app.logger.info(
                f"Item criado: Serviço {novo_item.servico_id}, "
                f"Qtd: {novo_item.quantidade}, "
                f"Valor: {novo_item.valor_total}"
            )
            
        except Exception as e:
            current_app.logger.error(f"Erro ao criar item: {item_data} - {str(e)}")
            continue
    
    # ⚠️ REGISTRAR: Alteração dos itens
    if itens_criados:
        alteracoes_realizadas.append({
            'campo': 'itens_proposta',
            'detalhes': {
                'total_itens_antigos': len(itens_atuais),
                'total_itens_novos': len(itens_criados),
                'valor_total_itens': valor_total_itens,
                'itens_criados': [
                    {
                        'servico_id': item.servico_id,
                        'quantidade': float(item.quantidade),
                        'valor_unitario': float(item.valor_unitario),
                        'valor_total': float(item.valor_total)
                    } for item in itens_criados
                ]
            }
        })
        
        current_app.logger.info(f"Registrada alteração dos itens: {len(itens_criados)} novos itens")
    
    return len(itens_criados) > 0

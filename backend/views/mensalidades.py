"""
Views para mensalidades automáticas.
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from config import db
from models.tributario import MensalidadeAutomatica, TipoAtividade, RegimeTributario, FaixaFaturamento
from models.clientes import Cliente
from models.propostas import Proposta
from views.utils import validate_required_fields

mensalidades_bp = Blueprint('mensalidades', __name__)


@mensalidades_bp.route('/buscar', methods=['POST'])
@jwt_required()
def buscar_mensalidade():
    """
    Busca a mensalidade automática baseada na configuração tributária.
    
    Body:
    {
        "tipo_atividade_id": int,
        "regime_tributario_id": int,
        "faixa_faturamento_id": int (opcional),
        "faturamento_anual": float (opcional - para busca automática de faixa)
    }
    """
    try:
        data = request.get_json()
        
        # Validação dos dados obrigatórios
        validation_error = validate_required_fields(data, ['tipo_atividade_id', 'regime_tributario_id'])
        if validation_error:
            return validation_error
        
        tipo_atividade_id = data.get('tipo_atividade_id')
        regime_tributario_id = data.get('regime_tributario_id')
        faixa_faturamento_id = data.get('faixa_faturamento_id')  # Opcional
        faturamento_anual = data.get('faturamento_anual')  # Opcional
        
        # Se faturamento_anual foi fornecido, buscar faixa automaticamente
        if faturamento_anual and not faixa_faturamento_id:
            faixa = FaixaFaturamento.query.filter(
                FaixaFaturamento.valor_minimo <= faturamento_anual,
                FaixaFaturamento.valor_maximo >= faturamento_anual
            ).first()
            
            if faixa:
                faixa_faturamento_id = faixa.id
            else:
                # Se não encontrou faixa específica, buscar a maior faixa disponível
                faixa = FaixaFaturamento.query.filter(
                    FaixaFaturamento.valor_minimo <= faturamento_anual
                ).order_by(FaixaFaturamento.valor_minimo.desc()).first()
                
                if faixa:
                    faixa_faturamento_id = faixa.id
        
        # Buscar mensalidade automática
        query = MensalidadeAutomatica.query.filter_by(
            tipo_atividade_id=tipo_atividade_id,
            regime_tributario_id=regime_tributario_id,
            ativo=True
        )
        
        # Se faixa_faturamento_id foi fornecida, incluir na busca
        if faixa_faturamento_id:
            query = query.filter_by(faixa_faturamento_id=faixa_faturamento_id)
        else:
            # Se não foi fornecida, buscar onde faixa_faturamento_id é NULL
            query = query.filter(MensalidadeAutomatica.faixa_faturamento_id.is_(None))
        
        mensalidade = query.first()
        
        if not mensalidade:
            return jsonify({
                'success': False,
                'message': 'Mensalidade automática não encontrada para esta configuração',
                'data': None
            }), 404
        
        # Preparar resposta com informações adicionais
        mensalidade_data = mensalidade.to_json()
        
        # Adicionar informações sobre "A combinar"
        if mensalidade.valor_mensal == 0:
            mensalidade_data['a_combinar'] = True
            mensalidade_data['mensagem'] = 'Valor a combinar - entre em contato para negociação'
        else:
            mensalidade_data['a_combinar'] = False
            mensalidade_data['mensagem'] = 'Valor automático encontrado'
        
        # Adicionar informações da faixa de faturamento
        if mensalidade.faixa_faturamento:
            mensalidade_data['faixa_info'] = {
                'descricao': mensalidade.faixa_faturamento.descricao,
                'valor_minimo': mensalidade.faixa_faturamento.valor_minimo,
                'valor_maximo': mensalidade.faixa_faturamento.valor_maximo
            }
        
        return jsonify({
            'success': True,
            'message': 'Mensalidade automática encontrada',
            'data': mensalidade_data
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao buscar mensalidade: {str(e)}',
            'data': None
        }), 500


@mensalidades_bp.route('/api/mensalidades/buscar-por-proposta/<int:proposta_id>', methods=['GET'])
@jwt_required()
def buscar_mensalidade_por_proposta(proposta_id):
    """
    Busca a mensalidade automática baseada na configuração de uma proposta específica.
    """
    try:
        # Buscar proposta
        proposta = Proposta.query.get(proposta_id)
        if not proposta:
            return jsonify({
                'success': False,
                'message': 'Proposta não encontrada',
                'data': None
            }), 404
        
        # Verificar se a proposta tem configuração tributária completa
        if not proposta.tipo_atividade_id or not proposta.regime_tributario_id or not proposta.faixa_faturamento_id:
            return jsonify({
                'success': False,
                'message': 'Proposta não possui configuração tributária completa',
                'data': None
            }), 400
        
        # Buscar mensalidade automática
        mensalidade = MensalidadeAutomatica.query.filter_by(
            tipo_atividade_id=proposta.tipo_atividade_id,
            regime_tributario_id=proposta.regime_tributario_id,
            faixa_faturamento_id=proposta.faixa_faturamento_id,
            ativo=True
        ).first()
        
        if not mensalidade:
            return jsonify({
                'success': False,
                'message': 'Mensalidade automática não encontrada para esta configuração',
                'data': None
            }), 404
        
        return jsonify({
            'success': True,
            'message': 'Mensalidade automática encontrada',
            'data': mensalidade.to_json()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao buscar mensalidade: {str(e)}',
            'data': None
        }), 500


@mensalidades_bp.route('/api/mensalidades/listar', methods=['GET'])
@jwt_required()
def listar_mensalidades():
    """
    Lista todas as mensalidades automáticas cadastradas.
    """
    try:
        mensalidades = MensalidadeAutomatica.query.filter_by(ativo=True).all()
        
        return jsonify({
            'success': True,
            'message': f'{len(mensalidades)} mensalidades encontradas',
            'data': [mensalidade.to_json() for mensalidade in mensalidades]
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao listar mensalidades: {str(e)}',
            'data': None
        }), 500


@mensalidades_bp.route('/api/mensalidades/calcular-total', methods=['POST'])
@jwt_required()
def calcular_total_com_mensalidade():
    """
    Calcula o total de uma proposta incluindo a mensalidade automática.
    
    Body:
    {
        "tipo_atividade_id": int,
        "regime_tributario_id": int,
        "faixa_faturamento_id": int,
        "valor_servicos": float
    }
    """
    try:
        data = request.get_json()
        
        # Validação dos dados
        validation_error = validate_required_fields(data, ['tipo_atividade_id', 'regime_tributario_id', 'faixa_faturamento_id', 'valor_servicos'])
        if validation_error:
            return validation_error
        
        tipo_atividade_id = data.get('tipo_atividade_id')
        regime_tributario_id = data.get('regime_tributario_id')
        faixa_faturamento_id = data.get('faixa_faturamento_id')
        valor_servicos = float(data.get('valor_servicos', 0))
        
        # Buscar mensalidade automática
        mensalidade = MensalidadeAutomatica.query.filter_by(
            tipo_atividade_id=tipo_atividade_id,
            regime_tributario_id=regime_tributario_id,
            faixa_faturamento_id=faixa_faturamento_id,
            ativo=True
        ).first()
        
        valor_mensalidade = 0.0
        mensalidade_info = None
        
        if mensalidade:
            valor_mensalidade = float(mensalidade.valor_mensalidade)
            mensalidade_info = mensalidade.to_json()
        
        valor_total = valor_servicos + valor_mensalidade
        
        return jsonify({
            'success': True,
            'message': 'Cálculo realizado com sucesso',
            'data': {
                'valor_servicos': valor_servicos,
                'valor_mensalidade': valor_mensalidade,
                'valor_total': valor_total,
                'mensalidade_info': mensalidade_info
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao calcular total: {str(e)}',
            'data': None
        }), 500


@mensalidades_bp.route('/configuracoes-validas', methods=['GET'])
@jwt_required()
def listar_configuracoes_validas():
    """
    Lista todas as configurações válidas de mensalidades automáticas.
    Útil para popular dropdowns e validar combinações.
    """
    try:
        # Buscar todas as mensalidades ativas com relacionamentos
        mensalidades = MensalidadeAutomatica.query.join(RegimeTributario).join(TipoAtividade).join(FaixaFaturamento).filter(
            MensalidadeAutomatica.ativo == True
        ).all()
        
        # Agrupar por regime tributário
        configuracoes = {}
        for mensalidade in mensalidades:
            regime_codigo = mensalidade.regime_tributario.codigo
            regime_nome = mensalidade.regime_tributario.nome
            
            if regime_codigo not in configuracoes:
                configuracoes[regime_codigo] = {
                    'regime_id': mensalidade.regime_tributario.id,
                    'regime_codigo': regime_codigo,
                    'regime_nome': regime_nome,
                    'tipos_atividade': {}
                }
            
            tipo_codigo = mensalidade.tipo_atividade.codigo
            tipo_nome = mensalidade.tipo_atividade.nome
            
            if tipo_codigo not in configuracoes[regime_codigo]['tipos_atividade']:
                configuracoes[regime_codigo]['tipos_atividade'][tipo_codigo] = {
                    'tipo_id': mensalidade.tipo_atividade.id,
                    'tipo_codigo': tipo_codigo,
                    'tipo_nome': tipo_nome,
                    'faixas_faturamento': []
                }
            
            # Adicionar faixa de faturamento
            faixa_info = {
                'faixa_id': mensalidade.faixa_faturamento.id,
                'descricao': mensalidade.faixa_faturamento.descricao,
                'valor_minimo': mensalidade.faixa_faturamento.valor_minimo,
                'valor_maximo': mensalidade.faixa_faturamento.valor_maximo,
                'valor_mensal': mensalidade.valor_mensal,
                'a_combinar': mensalidade.valor_mensal == 0
            }
            
            configuracoes[regime_codigo]['tipos_atividade'][tipo_codigo]['faixas_faturamento'].append(faixa_info)
        
        # Ordenar faixas por valor mínimo
        for regime in configuracoes.values():
            for tipo in regime['tipos_atividade'].values():
                tipo['faixas_faturamento'].sort(key=lambda x: x['valor_minimo'])
        
        return jsonify({
            'success': True,
            'message': 'Configurações válidas encontradas',
            'data': {
                'configuracoes': list(configuracoes.values()),
                'total_regimes': len(configuracoes),
                'total_mensalidades': len(mensalidades)
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao listar configurações: {str(e)}',
            'data': None
        }), 500


@mensalidades_bp.route('/validar-combinacao', methods=['POST'])
@jwt_required()
def validar_combinacao():
    """
    Valida se uma combinação de regime + tipo + faixa é válida.
    
    Body:
    {
        "regime_tributario_id": int,
        "tipo_atividade_id": int,
        "faixa_faturamento_id": int
    }
    """
    try:
        data = request.get_json()
        
        # Validação dos dados obrigatórios
        validation_error = validate_required_fields(data, ['regime_tributario_id', 'tipo_atividade_id', 'faixa_faturamento_id'])
        if validation_error:
            return validation_error
        
        regime_id = data.get('regime_tributario_id')
        tipo_id = data.get('tipo_atividade_id')
        faixa_id = data.get('faixa_faturamento_id')
        
        # Buscar mensalidade
        mensalidade = MensalidadeAutomatica.query.filter_by(
            regime_tributario_id=regime_id,
            tipo_atividade_id=tipo_id,
            faixa_faturamento_id=faixa_id,
            ativo=True
        ).first()
        
        if not mensalidade:
            return jsonify({
                'success': False,
                'message': 'Combinação inválida - mensalidade não encontrada',
                'data': {
                    'valida': False,
                    'mensalidade': None
                }
            }), 404
        
        return jsonify({
            'success': True,
            'message': 'Combinação válida',
            'data': {
                'valida': True,
                'mensalidade': mensalidade.to_json()
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao validar combinação: {str(e)}',
            'data': None
        }), 500

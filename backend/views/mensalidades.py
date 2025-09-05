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


@mensalidades_bp.route('/api/mensalidades/buscar', methods=['POST'])
@jwt_required()
def buscar_mensalidade():
    """
    Busca a mensalidade automática baseada na configuração tributária.
    
    Body:
    {
        "tipo_atividade_id": int,
        "regime_tributario_id": int,
        "faixa_faturamento_id": int
    }
    """
    try:
        data = request.get_json()
        
        # Validação dos dados
        validation_error = validate_required_fields(data, ['tipo_atividade_id', 'regime_tributario_id', 'faixa_faturamento_id'])
        if validation_error:
            return validation_error
        
        tipo_atividade_id = data.get('tipo_atividade_id')
        regime_tributario_id = data.get('regime_tributario_id')
        faixa_faturamento_id = data.get('faixa_faturamento_id')
        
        # Buscar mensalidade automática
        mensalidade = MensalidadeAutomatica.query.filter_by(
            tipo_atividade_id=tipo_atividade_id,
            regime_tributario_id=regime_tributario_id,
            faixa_faturamento_id=faixa_faturamento_id,
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

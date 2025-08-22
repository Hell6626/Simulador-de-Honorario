"""
Views relacionadas às faixas de faturamento.
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required

from config import db
from models import FaixaFaturamento
from .utils import handle_api_errors

faixas_faturamento_bp = Blueprint('faixas_faturamento', __name__)

@faixas_faturamento_bp.route('/', methods=['GET'])
@handle_api_errors
def get_faixas_faturamento():
    """Lista faixas de faturamento, opcionalmente filtradas por regime tributário"""
    try:
        regime_tributario_id = request.args.get('regime_tributario_id', type=int)
        
        query = FaixaFaturamento.query.filter_by(ativo=True)
        
        if regime_tributario_id:
            query = query.filter_by(regime_tributario_id=regime_tributario_id)
        
        faixas = query.order_by(FaixaFaturamento.valor_inicial).all()
        result = []
        
        for faixa in faixas:
            result.append(faixa.to_json())
        
        return jsonify(result)
    except Exception as e:
        print(f"Erro geral: {e}")
        return jsonify({"error": f"Erro: {str(e)}"}), 500

@faixas_faturamento_bp.route('/<int:faixa_id>', methods=['GET'])
@handle_api_errors
def get_faixa_faturamento(faixa_id: int):
    """Busca uma faixa de faturamento específica"""
    faixa = FaixaFaturamento.query.get_or_404(faixa_id)
    return jsonify(faixa.to_json())

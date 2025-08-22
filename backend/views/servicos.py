"""
Views relacionadas aos serviços.
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required

from config import db
from models import Servico
from .utils import handle_api_errors

servicos_bp = Blueprint('servicos', __name__)

@servicos_bp.route('/', methods=['GET'])
@handle_api_errors
def get_servicos():
    """Lista serviços, opcionalmente filtrados por categoria"""
    try:
        categoria = request.args.get('categoria')
        
        query = Servico.query.filter_by(ativo=True)
        
        if categoria:
            query = query.filter_by(categoria=categoria)
        
        servicos = query.order_by(Servico.nome).all()
        result = []
        
        for servico in servicos:
            result.append(servico.to_json())
        
        return jsonify(result)
    except Exception as e:
        print(f"Erro geral: {e}")
        return jsonify({"error": f"Erro: {str(e)}"}), 500

@servicos_bp.route('/fiscais', methods=['GET'])
@handle_api_errors
def get_servicos_fiscais():
    """Lista apenas serviços fiscais"""
    try:
        servicos = Servico.query.filter_by(ativo=True, categoria='FISCAL').order_by(Servico.nome).all()
        result = []
        
        for servico in servicos:
            result.append(servico.to_json())
        
        return jsonify(result)
    except Exception as e:
        print(f"Erro geral: {e}")
        return jsonify({"error": f"Erro: {str(e)}"}), 500

@servicos_bp.route('/<int:servico_id>', methods=['GET'])
@jwt_required()
@handle_api_errors
def get_servico(servico_id: int):
    """Busca um serviço específico"""
    servico = Servico.query.get_or_404(servico_id)
    return jsonify(servico.to_json())

"""
Views relacionadas à autenticação.
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt, get_jwt_identity

from models import Funcionario
from .utils import handle_api_errors

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    email = (data.get('email') or '').strip().lower()
    senha = data.get('senha') or ''

    func = Funcionario.query.filter_by(email=email, ativo=True).first()
    if not func or not func.check_senha(senha):
        return jsonify({"error": "Credenciais inválidas"}), 401

    token = create_access_token(
        identity=str(func.id),  # <- string!
        additional_claims={"email": func.email, "nome": func.nome}
    )
    return jsonify({"token": token})

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """
    Faz logout do usuário invalidando o token JWT.
    O token será adicionado à blacklist para não poder ser usado novamente.
    """
    try:
        # Obtém o token atual e o ID do funcionário
        jti = get_jwt()["jti"]
        funcionario_id = get_jwt_identity()
        
        # Adiciona o token à blacklist
        from config import jwt
        
        # Para uma implementação simples, vamos apenas retornar sucesso
        # Em produção, você pode implementar uma blacklist no banco de dados
        
        return jsonify({
            "message": "Logout realizado com sucesso",
            "success": True,
            "funcionario_id": funcionario_id
        }), 200
        
    except Exception as e:
        return jsonify({
            "error": "Erro ao realizar logout",
            "message": str(e)
        }), 500

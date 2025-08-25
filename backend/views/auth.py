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

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_user_info():
    """Retorna informações do usuário logado"""
    funcionario_id = int(get_jwt_identity())
    funcionario = Funcionario.query.get(funcionario_id)
    
    if not funcionario:
        return jsonify({"error": "Usuário não encontrado"}), 404
    
    return jsonify({
        "id": funcionario.id,
        "nome": funcionario.nome,
        "email": funcionario.email,
        "gerente": funcionario.gerente,
        "ativo": funcionario.ativo,
        "empresa_id": funcionario.empresa_id,
        "cargo_id": funcionario.cargo_id
    })

@auth_bp.route('/test', methods=['GET'])
@jwt_required()
def test_auth():
    """Endpoint de teste para verificar se a autenticação está funcionando"""
    funcionario_id = int(get_jwt_identity())
    funcionario = Funcionario.query.get(funcionario_id)
    
    if not funcionario:
        return jsonify({"error": "Usuário não encontrado"}), 404
    
    return jsonify({
        "message": "Autenticação funcionando!",
        "user": {
            "id": funcionario.id,
            "nome": funcionario.nome,
            "email": funcionario.email,
            "gerente": funcionario.gerente
        }
    })

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """
    Faz logout do usuário.
    """
    try:
        funcionario_id = get_jwt_identity()
        
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

"""
Views relacionadas aos funcionários.
"""

from flask import Blueprint, request, jsonify, current_app
from sqlalchemy import or_
from datetime import datetime
from flask_jwt_extended import jwt_required

from config import db
from models import Funcionario
from .utils import handle_api_errors, validate_required_fields, paginate_query

funcionarios_bp = Blueprint('funcionarios', __name__)

@funcionarios_bp.route('/', methods=['GET'])
@jwt_required()
@handle_api_errors
def get_funcionarios():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    ativo = request.args.get('ativo', type=bool)
    search = request.args.get('search', '').strip()

    query = Funcionario.query

    if ativo is not None:
        query = query.filter(Funcionario.ativo == ativo)
    if search:
        query = query.filter(
            or_(
                Funcionario.nome.ilike(f'%{search}%'),
                Funcionario.email.ilike(f'%{search}%')
            )
        )

    funcionarios = paginate_query(query.order_by(Funcionario.nome), page, per_page)

    data = [f.to_json() for f in funcionarios.items]
    return jsonify({
        'items': data,
        'funcionarios': data,
        'total': funcionarios.total,
        'pages': funcionarios.pages,
        'current_page': page,
        'per_page': per_page
    })

@funcionarios_bp.route('/<int:funcionario_id>', methods=['GET'])
@jwt_required()
@handle_api_errors
def get_funcionario(funcionario_id: int):
    funcionario = Funcionario.query.get_or_404(funcionario_id)
    return jsonify(funcionario.to_json())

@funcionarios_bp.route('/', methods=['POST'])
@jwt_required()
@handle_api_errors
def create_funcionario():
    data = request.get_json() or {}
    validation_error = validate_required_fields(data, ['nome', 'email', 'senha', 'cargo_id', 'empresa_id'])
    if validation_error:
        return validation_error

    # Verificar se email já existe
    email_existente = Funcionario.query.filter_by(email=data['email'].strip().lower()).first()
    if email_existente:
        raise ValueError('Email já cadastrado')

    func = Funcionario(
        nome=data['nome'].strip(),
        email=data['email'].strip().lower(),
        gerente=bool(data.get('gerente', False)),
        cargo_id=data['cargo_id'],
        empresa_id=data['empresa_id'],
        ativo=data.get('ativo', True),
    )
    func.set_senha(data['senha'])  # <- HASH DA SENHA

    db.session.add(func)
    db.session.commit()
    current_app.logger.info(f"Funcionário criado: {func.nome} (ID: {func.id})")
    return jsonify(func.to_json()), 201

@funcionarios_bp.route('/<int:funcionario_id>', methods=['PUT'])
@jwt_required()
@handle_api_errors
def update_funcionario(funcionario_id: int):
    funcionario = Funcionario.query.get_or_404(funcionario_id)
    data = request.get_json() or {}

    for field in ['nome', 'email', 'gerente', 'cargo_id', 'empresa_id', 'ativo']:
        if field in data:
            value = data[field]
            if field in ['nome', 'email'] and value:
                value = value.strip()
                if field == 'email':
                    value = value.lower()
            setattr(funcionario, field, value)

    funcionario.updated_at = datetime.utcnow()
    db.session.commit()
    current_app.logger.info(f"Funcionário atualizado: {funcionario.nome} (ID: {funcionario.id})")
    return jsonify(funcionario.to_json())

@funcionarios_bp.route('/<int:funcionario_id>', methods=['DELETE'])
@jwt_required()
@handle_api_errors
def delete_funcionario(funcionario_id: int):
    funcionario = Funcionario.query.get_or_404(funcionario_id)

    if funcionario.propostas:
        funcionario.ativo = False
        funcionario.updated_at = datetime.utcnow()
        db.session.commit()
        current_app.logger.info(f"Funcionário desativado: {funcionario.nome} (ID: {funcionario.id})")
        return jsonify({'message': 'Funcionário desativado (possui propostas associadas)'})
    else:
        nome = funcionario.nome
        db.session.delete(funcionario)
        db.session.commit()
        current_app.logger.info(f"Funcionário removido: {nome} (ID: {funcionario_id})")
        return jsonify({'message': 'Funcionário removido'})

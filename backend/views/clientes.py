"""
Views relacionadas aos clientes.
"""

from flask import Blueprint, request, jsonify, current_app
from sqlalchemy import or_
from datetime import datetime
from flask_jwt_extended import jwt_required

from config import db
from models import Cliente
from .utils import handle_api_errors, validate_required_fields, paginate_query

clientes_bp = Blueprint('clientes', __name__)

@clientes_bp.route('/', methods=['GET'])
@jwt_required()
@handle_api_errors
def get_clientes():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    ativo = request.args.get('ativo', type=bool)
    search = request.args.get('search', '').strip()

    query = Cliente.query

    if ativo is not None:
        query = query.filter(Cliente.ativo == ativo)
    if search:
        query = query.filter(
            or_(
                Cliente.nome.ilike(f'%{search}%'),
                Cliente.cpf.ilike(f'%{search}%'),
                Cliente.email.ilike(f'%{search}%')
            )
        )

    clientes = paginate_query(
        query.order_by(Cliente.nome.asc()),
        page, per_page
    )

    data = [c.to_json() for c in clientes.items]
    return jsonify({
        'items': data,
        'clientes': data,
        'total': clientes.total,
        'pages': clientes.pages,
        'current_page': page,
        'per_page': per_page
    })

@clientes_bp.route('/<int:cliente_id>', methods=['GET'])
@jwt_required()
@handle_api_errors
def get_cliente(cliente_id: int):
    cliente = Cliente.query.get_or_404(cliente_id)
    return jsonify(cliente.to_json())

@clientes_bp.route('/', methods=['POST'])
@jwt_required()
@handle_api_errors
def create_cliente():
    data = request.get_json() or {}
    
    # Validação de campos obrigatórios
    validation_error = validate_required_fields(data, ['nome', 'cpf'])
    if validation_error:
        return validation_error

    # Verificar se CPF já existe
    cpf_existente = Cliente.query.filter_by(cpf=data['cpf'].strip()).first()
    if cpf_existente:
        raise ValueError('CPF já cadastrado')

    cliente = Cliente(
        nome=(data['nome'] or '').strip(),
        cpf=(data['cpf'] or '').strip(),
        email=(data.get('email') or '').strip().lower() or None,
        abertura_empresa=bool(data.get('abertura_empresa', False)),
        ativo=data.get('ativo', True)
    )

    db.session.add(cliente)
    db.session.commit()
    
    current_app.logger.info(f"Cliente criado: {cliente.nome} (ID: {cliente.id})")
    return jsonify(cliente.to_json()), 201

@clientes_bp.route('/<int:cliente_id>', methods=['PUT'])
@jwt_required()
@handle_api_errors
def update_cliente(cliente_id: int):
    cliente = Cliente.query.get_or_404(cliente_id)
    data = request.get_json() or {}

    # Campos que podem ser atualizados
    for field in ['nome', 'email', 'abertura_empresa', 'ativo']:
        if field in data:
            value = data[field]
            if field == 'email' and value:
                value = value.strip().lower()
            elif field == 'nome' and value:
                value = value.strip()
            setattr(cliente, field, value)

    cliente.updated_at = datetime.utcnow()
    db.session.commit()

    current_app.logger.info(f"Cliente atualizado: {cliente.nome} (ID: {cliente.id})")
    return jsonify(cliente.to_json())

@clientes_bp.route('/<int:cliente_id>', methods=['DELETE'])
@jwt_required()
@handle_api_errors
def delete_cliente(cliente_id: int):
    cliente = Cliente.query.get_or_404(cliente_id)

    if cliente.propostas:
        cliente.ativo = False
        cliente.updated_at = datetime.utcnow()
        db.session.commit()
        current_app.logger.info(f"Cliente desativado: {cliente.nome} (ID: {cliente.id})")
        return jsonify({'message': 'Cliente desativado (possui propostas associadas)'})
    else:
        nome = cliente.nome
        db.session.delete(cliente)
        db.session.commit()
        current_app.logger.info(f"Cliente removido: {nome} (ID: {cliente_id})")
        return jsonify({'message': 'Cliente removido'})

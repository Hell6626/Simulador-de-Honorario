"""
Views para gerenciamento de cargos.
"""

from flask import Blueprint, request, jsonify, current_app
from datetime import datetime
from models import Cargo
from .utils import handle_api_errors, paginate_query

cargos_bp = Blueprint('cargos', __name__)

@cargos_bp.route('/', methods=['GET'])
@handle_api_errors
def get_cargos():
    """Lista todos os cargos com paginação e filtros"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    ativo = request.args.get('ativo', type=lambda v: v.lower() == 'true')
    search = request.args.get('search', '').strip()
    empresa_id = request.args.get('empresa_id', type=int)

    query = Cargo.query

    if ativo is not None:
        query = query.filter(Cargo.ativo == ativo)

    if empresa_id:
        query = query.filter(Cargo.empresa_id == empresa_id)

    if search:
        query = query.filter(
            Cargo.nome.ilike(f'%{search}%'),
            Cargo.codigo.ilike(f'%{search}%')
        )

    cargos = paginate_query(query.order_by(Cargo.nome), page, per_page)

    data = [c.to_json() for c in cargos.items]

    return jsonify({
        'cargos': data,
        'total': cargos.total,
        'pages': cargos.pages,
        'page': page
    })

@cargos_bp.route('/<int:cargo_id>', methods=['GET'])
@handle_api_errors
def get_cargo(cargo_id: int):
    """Busca um cargo específico"""
    cargo = Cargo.query.get_or_404(cargo_id)
    return jsonify(cargo.to_json())

@cargos_bp.route('/', methods=['POST'])
@handle_api_errors
def create_cargo():
    """Cria um novo cargo"""
    data = request.get_json()

    if not data:
        return jsonify({'error': 'Dados não fornecidos'}), 400

    required_fields = ['codigo', 'nome', 'empresa_id']
    for field in required_fields:
        if field not in data or not data[field]:
            return jsonify({'error': f'Campo {field} é obrigatório'}), 400

    # Verificar se o código já existe
    codigo_existente = Cargo.query.filter_by(codigo=data['codigo'].strip().upper()).first()
    if codigo_existente:
        return jsonify({'error': 'Código de cargo já existe'}), 400

    cargo = Cargo(
        codigo=data['codigo'].strip().upper(),
        nome=data['nome'].strip(),
        descricao=data.get('descricao', '').strip(),
        nivel=data.get('nivel', '').strip(),
        empresa_id=data['empresa_id']
    )

    from config import db
    db.session.add(cargo)
    db.session.commit()

    current_app.logger.info(f"Cargo criado: {cargo.nome} (ID: {cargo.id})")
    return jsonify(cargo.to_json()), 201

@cargos_bp.route('/<int:cargo_id>', methods=['PUT'])
@handle_api_errors
def update_cargo(cargo_id: int):
    """Atualiza um cargo existente"""
    cargo = Cargo.query.get_or_404(cargo_id)
    data = request.get_json()

    if not data:
        return jsonify({'error': 'Dados não fornecidos'}), 400

    # Verificar se o código já existe (exceto para o próprio cargo)
    if 'codigo' in data and data['codigo']:
        codigo_existente = Cargo.query.filter(
            Cargo.codigo == data['codigo'].strip().upper(),
            Cargo.id != cargo_id
        ).first()
        if codigo_existente:
            return jsonify({'error': 'Código de cargo já existe'}), 400

    # Atualizar campos
    fields_to_update = ['codigo', 'nome', 'descricao', 'nivel', 'empresa_id', 'ativo']
    for field in fields_to_update:
        if field in data:
            if field in ['codigo', 'nome', 'descricao', 'nivel']:
                setattr(cargo, field, data[field].strip())
            else:
                setattr(cargo, field, data[field])

    cargo.updated_at = datetime.utcnow()

    from config import db
    db.session.commit()

    current_app.logger.info(f"Cargo atualizado: {cargo.nome} (ID: {cargo.id})")
    return jsonify(cargo.to_json())

@cargos_bp.route('/<int:cargo_id>', methods=['DELETE'])
@handle_api_errors
def delete_cargo(cargo_id: int):
    """Desativa um cargo (soft delete)"""
    cargo = Cargo.query.get_or_404(cargo_id)

    # Verificar se há funcionários vinculados
    if cargo.funcionarios:
        cargo.ativo = False
        cargo.updated_at = datetime.utcnow()
        from config import db
        db.session.commit()
        current_app.logger.info(f"Cargo desativado: {cargo.nome} (ID: {cargo.id})")
        return jsonify({'message': 'Cargo desativado com sucesso'})
    else:
        from config import db
        db.session.delete(cargo)
        db.session.commit()
        current_app.logger.info(f"Cargo excluído: {cargo.nome} (ID: {cargo.id})")
        return jsonify({'message': 'Cargo excluído com sucesso'})

"""
Views para gerenciamento de empresas.
"""

from flask import Blueprint, request, jsonify, current_app
from datetime import datetime
from models import Empresa
from .utils import handle_api_errors, paginate_query

empresas_bp = Blueprint('empresas', __name__)

@empresas_bp.route('/', methods=['GET'])
@handle_api_errors
def get_empresas():
    """Lista todas as empresas com paginação e filtros"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    ativo = request.args.get('ativo', type=lambda v: v.lower() == 'true')
    search = request.args.get('search', '').strip()

    query = Empresa.query

    if ativo is not None:
        query = query.filter(Empresa.ativo == ativo)

    if search:
        query = query.filter(
            Empresa.nome.ilike(f'%{search}%'),
            Empresa.cnpj.ilike(f'%{search}%')
        )

    empresas = paginate_query(query.order_by(Empresa.nome), page, per_page)

    data = [e.to_json() for e in empresas.items]

    return jsonify({
        'empresas': data,
        'total': empresas.total,
        'pages': empresas.pages,
        'page': page
    })

@empresas_bp.route('/<int:empresa_id>', methods=['GET'])
@handle_api_errors
def get_empresa(empresa_id: int):
    """Busca uma empresa específica"""
    empresa = Empresa.query.get_or_404(empresa_id)
    return jsonify(empresa.to_json())

@empresas_bp.route('/', methods=['POST'])
@handle_api_errors
def create_empresa():
    """Cria uma nova empresa"""
    data = request.get_json()

    if not data:
        return jsonify({'error': 'Dados não fornecidos'}), 400

    required_fields = ['nome', 'cnpj', 'endereco']
    for field in required_fields:
        if field not in data or not data[field]:
            return jsonify({'error': f'Campo {field} é obrigatório'}), 400

    # Verificar se o CNPJ já existe
    cnpj_existente = Empresa.query.filter_by(cnpj=data['cnpj'].strip()).first()
    if cnpj_existente:
        return jsonify({'error': 'CNPJ já existe'}), 400

    empresa = Empresa(
        nome=data['nome'].strip(),
        cnpj=data['cnpj'].strip(),
        endereco=data['endereco'].strip(),
        telefone=data.get('telefone', '').strip(),
        email=data.get('email', '').strip()
    )

    from config import db
    db.session.add(empresa)
    db.session.commit()

    current_app.logger.info(f"Empresa criada: {empresa.nome} (ID: {empresa.id})")
    return jsonify(empresa.to_json()), 201

@empresas_bp.route('/<int:empresa_id>', methods=['PUT'])
@handle_api_errors
def update_empresa(empresa_id: int):
    """Atualiza uma empresa existente"""
    empresa = Empresa.query.get_or_404(empresa_id)
    data = request.get_json()

    if not data:
        return jsonify({'error': 'Dados não fornecidos'}), 400

    # Verificar se o CNPJ já existe (exceto para a própria empresa)
    if 'cnpj' in data and data['cnpj']:
        cnpj_existente = Empresa.query.filter(
            Empresa.cnpj == data['cnpj'].strip(),
            Empresa.id != empresa_id
        ).first()
        if cnpj_existente:
            return jsonify({'error': 'CNPJ já existe'}), 400

    # Atualizar campos
    fields_to_update = ['nome', 'cnpj', 'endereco', 'telefone', 'email', 'ativo']
    for field in fields_to_update:
        if field in data:
            if field in ['nome', 'cnpj', 'endereco', 'telefone', 'email']:
                setattr(empresa, field, data[field].strip())
            else:
                setattr(empresa, field, data[field])

    empresa.updated_at = datetime.utcnow()

    from config import db
    db.session.commit()

    current_app.logger.info(f"Empresa atualizada: {empresa.nome} (ID: {empresa.id})")
    return jsonify(empresa.to_json())

@empresas_bp.route('/<int:empresa_id>', methods=['DELETE'])
@handle_api_errors
def delete_empresa(empresa_id: int):
    """Desativa uma empresa (soft delete)"""
    empresa = Empresa.query.get_or_404(empresa_id)

    # Verificar se há funcionários ou cargos vinculados
    if empresa.funcionarios or empresa.cargos:
        empresa.ativo = False
        empresa.updated_at = datetime.utcnow()
        from config import db
        db.session.commit()
        current_app.logger.info(f"Empresa desativada: {empresa.nome} (ID: {empresa.id})")
        return jsonify({'message': 'Empresa desativada com sucesso'})
    else:
        from config import db
        db.session.delete(empresa)
        db.session.commit()
        current_app.logger.info(f"Empresa excluída: {empresa.nome} (ID: {empresa.id})")
        return jsonify({'message': 'Empresa excluída com sucesso'})

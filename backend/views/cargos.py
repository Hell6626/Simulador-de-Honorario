"""
Views para gerenciamento de cargos.
"""

from flask import Blueprint, request, jsonify, current_app
from datetime import datetime
import random
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import Cargo, Funcionario
from .utils import handle_api_errors, paginate_query

cargos_bp = Blueprint('cargos', __name__)

def verificar_admin():
    """Verifica se o usuário logado é admin (gerente)"""
    funcionario_id = int(get_jwt_identity())
    funcionario = Funcionario.query.get(funcionario_id)
    if not funcionario or not funcionario.gerente:
        return False
    return funcionario

def gerar_codigo_cargo(nome: str) -> str:
    """Gera código automático: 3 primeiras letras do nome + 3 números aleatórios"""
    # Pegar as 3 primeiras letras do nome, converter para maiúsculo
    letras = nome[:3].upper().replace(' ', '')
    
    # Se não tiver 3 letras, completar com X
    while len(letras) < 3:
        letras += 'X'
    
    # Gerar 3 números aleatórios
    numeros = ''.join([str(random.randint(0, 9)) for _ in range(3)])
    
    return f"{letras}{numeros}"

@cargos_bp.route('/', methods=['GET'])
@jwt_required()
@handle_api_errors
def get_cargos():
    """Lista todos os cargos com paginação e filtros"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    ativo = request.args.get('ativo', type=lambda v: v.lower() == 'true')
    search = request.args.get('search', '').strip()

    query = Cargo.query

    if ativo is not None:
        query = query.filter(Cargo.ativo == ativo)

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
@jwt_required()
@handle_api_errors
def get_cargo(cargo_id: int):
    """Busca um cargo específico"""
    cargo = Cargo.query.get_or_404(cargo_id)
    return jsonify(cargo.to_json())

@cargos_bp.route('/', methods=['POST'])
@jwt_required()
@handle_api_errors
def create_cargo():
    """Cria um novo cargo - apenas admin"""
    admin = verificar_admin()
    
    if not admin:
        return jsonify({'error': 'Apenas administradores podem criar cargos'}), 403

    data = request.get_json()

    if not data:
        return jsonify({'error': 'Dados não fornecidos'}), 400

    required_fields = ['nome']
    for field in required_fields:
        if field not in data or not data[field]:
            return jsonify({'error': f'Campo {field} é obrigatório'}), 400

    # Gerar código automático
    nome_cargo = data['nome'].strip()
    codigo = gerar_codigo_cargo(nome_cargo)
    
    # Verificar se o código já existe (pode acontecer com números aleatórios)
    tentativas = 0
    while Cargo.query.filter_by(codigo=codigo).first() and tentativas < 10:
        codigo = gerar_codigo_cargo(nome_cargo)
        tentativas += 1
    
    if tentativas >= 10:
        return jsonify({'error': 'Erro ao gerar código único para o cargo'}), 500

    cargo = Cargo(
        codigo=codigo,
        nome=nome_cargo,
        descricao=data.get('descricao', '').strip(),
        nivel=data.get('nivel', '').strip(),
        empresa_id=admin.empresa_id  # Vincula automaticamente à empresa do admin
    )

    from config import db
    db.session.add(cargo)
    db.session.commit()

    return jsonify(cargo.to_json()), 201

@cargos_bp.route('/<int:cargo_id>', methods=['PUT'])
@jwt_required()
@handle_api_errors
def update_cargo(cargo_id: int):
    """Atualiza um cargo existente - apenas admin"""
    admin = verificar_admin()
    if not admin:
        return jsonify({'error': 'Apenas administradores podem atualizar cargos'}), 403

    cargo = Cargo.query.get_or_404(cargo_id)
    
    # Verificar se o cargo pertence à empresa do admin
    if cargo.empresa_id != admin.empresa_id:
        return jsonify({'error': 'Você só pode editar cargos da sua empresa'}), 403
    
    data = request.get_json()

    if not data:
        return jsonify({'error': 'Dados não fornecidos'}), 400

    # Atualizar apenas os campos permitidos: nome, descricao, nivel
    if 'nome' in data and data['nome']:
        cargo.nome = data['nome'].strip()
    if 'descricao' in data:
        cargo.descricao = data['descricao'].strip() if data['descricao'] else None
    if 'nivel' in data:
        cargo.nivel = data['nivel'].strip() if data['nivel'] else None

    cargo.updated_at = datetime.utcnow()

    from config import db
    db.session.commit()

    current_app.logger.info(f"Cargo atualizado: {cargo.nome} (ID: {cargo.id})")
    return jsonify(cargo.to_json())

@cargos_bp.route('/<int:cargo_id>', methods=['DELETE'])
@jwt_required()
@handle_api_errors
def delete_cargo(cargo_id: int):
    """Desativa um cargo (soft delete) - apenas admin"""
    admin = verificar_admin()
    if not admin:
        return jsonify({'error': 'Apenas administradores podem excluir cargos'}), 403

    cargo = Cargo.query.get_or_404(cargo_id)
    
    # Verificar se o cargo pertence à empresa do admin
    if cargo.empresa_id != admin.empresa_id:
        return jsonify({'error': 'Você só pode excluir cargos da sua empresa'}), 403

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

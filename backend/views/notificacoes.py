"""
Views relacionadas às notificações.
"""

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import or_

from config import db
from models import Notificacao, Funcionario
from .utils import handle_api_errors, paginate_query

notificacoes_bp = Blueprint('notificacoes', __name__)


@notificacoes_bp.route('/', methods=['GET'])
@jwt_required()
@handle_api_errors
def get_notificacoes():
    """Busca notificações do funcionário logado"""
    funcionario_id = int(get_jwt_identity())
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    lida = request.args.get('lida', type=str)  # 'true', 'false' ou None para todas
    tipo = request.args.get('tipo', '').strip()
    
    # Verificar se funcionário existe e está ativo
    funcionario = Funcionario.query.get(funcionario_id)
    if not funcionario or not funcionario.ativo:
        raise ValueError('Funcionário não encontrado')
    
    # Query base - filtrar apenas notificações não deletadas
    query = Notificacao.query.filter_by(para_funcionario_id=funcionario_id, ativo=True).filter(
        Notificacao.deleted_at.is_(None)  # FILTRAR NÃO DELETADAS
    )
    
    # Filtrar por lida/não lida
    if lida == 'true':
        query = query.filter(Notificacao.lida == True)
    elif lida == 'false':
        query = query.filter(Notificacao.lida == False)
    
    # Filtrar por tipo
    if tipo:
        query = query.filter(Notificacao.tipo == tipo)
    
    # Ordenar por data de criação (mais recentes primeiro)
    query = query.order_by(Notificacao.created_at.desc())
    
    # Paginar resultados
    notificacoes = paginate_query(query, page, per_page)
    
    data = [n.to_json() for n in notificacoes.items]
    return jsonify({
        'items': data,
        'total': notificacoes.total,
        'pages': notificacoes.pages,
        'current_page': page,
        'per_page': per_page
    })


@notificacoes_bp.route('/<int:notificacao_id>/ler', methods=['POST'])
@jwt_required()
@handle_api_errors
def marcar_como_lida(notificacao_id: int):
    """Marca uma notificação como lida"""
    funcionario_id = int(get_jwt_identity())
    
    # Verificar se funcionário existe e está ativo
    funcionario = Funcionario.query.get(funcionario_id)
    if not funcionario or not funcionario.ativo:
        raise ValueError('Funcionário não encontrado')
    
    # Buscar notificação
    notificacao = Notificacao.query.get_or_404(notificacao_id)
    
    # Verificar se a notificação pertence ao funcionário
    if notificacao.para_funcionario_id != funcionario_id:
        raise ValueError('Notificação não pertence ao funcionário')
    
    # Marcar como lida
    notificacao.marcar_como_lida()
    
    current_app.logger.info(
        f"Notificação {notificacao_id} marcada como lida pelo funcionário {funcionario.nome}"
    )
    
    return jsonify({
        'message': 'Notificação marcada como lida',
        'notificacao': notificacao.to_json()
    })


@notificacoes_bp.route('/ler-todas', methods=['POST'])
@jwt_required()
@handle_api_errors
def marcar_todas_como_lidas():
    """Marca todas as notificações não lidas do funcionário como lidas"""
    funcionario_id = int(get_jwt_identity())
    
    # Verificar se funcionário existe e está ativo
    funcionario = Funcionario.query.get(funcionario_id)
    if not funcionario or not funcionario.ativo:
        raise ValueError('Funcionário não encontrado')
    
    # Buscar todas as notificações não lidas e não deletadas do funcionário
    notificacoes = Notificacao.query.filter_by(
        para_funcionario_id=funcionario_id,
        lida=False,
        ativo=True
    ).filter(
        Notificacao.deleted_at.is_(None)  # SÓ PROCESSAR NÃO DELETADAS
    ).all()
    
    # Marcar todas como lidas
    for notificacao in notificacoes:
        notificacao.marcar_como_lida()
    
    current_app.logger.info(
        f"{len(notificacoes)} notificações marcadas como lidas pelo funcionário {funcionario.nome}"
    )
    
    return jsonify({
        'message': f'{len(notificacoes)} notificações marcadas como lidas'
    })


@notificacoes_bp.route('/contador', methods=['GET'])
@jwt_required()
@handle_api_errors
def get_contador_notificacoes():
    """Retorna contador de notificações não lidas"""
    funcionario_id = int(get_jwt_identity())
    
    # Verificar se funcionário existe e está ativo
    funcionario = Funcionario.query.get(funcionario_id)
    if not funcionario or not funcionario.ativo:
        raise ValueError('Funcionário não encontrado')
    
    # Contar notificações não lidas e não deletadas
    total_nao_lidas = Notificacao.query.filter_by(
        para_funcionario_id=funcionario_id,
        lida=False,
        ativo=True
    ).filter(
        Notificacao.deleted_at.is_(None)  # SÓ CONTAR NÃO DELETADAS
    ).count()
    
    # Contar notificações por tipo (não deletadas)
    aprovacao_nao_lidas = Notificacao.query.filter_by(
        para_funcionario_id=funcionario_id,
        tipo='APROVACAO_DESCONTO',
        lida=False,
        ativo=True
    ).filter(
        Notificacao.deleted_at.is_(None)  # SÓ CONTAR NÃO DELETADAS
    ).count()
    
    return jsonify({
        'total_nao_lidas': total_nao_lidas,
        'aprovacao_nao_lidas': aprovacao_nao_lidas
    })


@notificacoes_bp.route('/<int:notificacao_id>', methods=['DELETE'])
@jwt_required()
@handle_api_errors
def delete_notificacao(notificacao_id: int):
    """Soft delete de uma notificação"""
    funcionario_id = int(get_jwt_identity())
    
    # Verificar se funcionário existe e está ativo
    funcionario = Funcionario.query.get(funcionario_id)
    if not funcionario or not funcionario.ativo:
        raise ValueError('Funcionário não encontrado')
    
    # Buscar notificação
    notificacao = Notificacao.query.get_or_404(notificacao_id)
    
    # Verificar se a notificação pertence ao funcionário
    if notificacao.para_funcionario_id != funcionario_id:
        raise ValueError('Notificação não pertence ao funcionário')
    
    # Soft delete
    notificacao.ativo = False
    db.session.commit()
    
    current_app.logger.info(
        f"Notificação {notificacao_id} excluída pelo funcionário {funcionario.nome}"
    )
    
    return jsonify({'message': 'Notificação excluída com sucesso'})

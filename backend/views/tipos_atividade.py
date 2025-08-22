"""
Views relacionadas aos tipos de atividade.
"""

from flask import Blueprint, request, jsonify, current_app
from sqlalchemy import or_

from config import db
from models import TipoAtividade, AtividadeRegime
from .utils import handle_api_errors, validate_required_fields, build_search_filters

tipos_atividade_bp = Blueprint('tipos_atividade', __name__)

@tipos_atividade_bp.route('/', methods=['GET'])
@handle_api_errors
def get_tipos_atividade():
    ativo = request.args.get('ativo', type=bool)
    aplicavel_pf = request.args.get('aplicavel_pf', type=bool)
    aplicavel_pj = request.args.get('aplicavel_pj', type=bool)
    search = request.args.get('search', '').strip()

    query = TipoAtividade.query

    if ativo is not None:
        query = query.filter(TipoAtividade.ativo == ativo)
    if aplicavel_pf is not None:
        query = query.filter(TipoAtividade.aplicavel_pf == aplicavel_pf)
    if aplicavel_pj is not None:
        query = query.filter(TipoAtividade.aplicavel_pj == aplicavel_pj)
    if search:
        search_filters = build_search_filters(TipoAtividade, search, ['nome', 'codigo', 'descricao'])
        if search_filters:
            query = query.filter(or_(*search_filters))

    tipos = query.order_by(TipoAtividade.nome).all()
    return jsonify([t.to_json() for t in tipos])

@tipos_atividade_bp.route('/<int:tipo_id>', methods=['GET'])
@handle_api_errors
def get_tipo_atividade(tipo_id: int):
    tipo = TipoAtividade.query.get_or_404(tipo_id)
    return jsonify(tipo.to_json())

@tipos_atividade_bp.route('/', methods=['POST'])
@handle_api_errors
def create_tipo_atividade():
    data = request.get_json() or {}
    validation_error = validate_required_fields(data, ['nome', 'codigo'])
    if validation_error:
        return validation_error

    tipo = TipoAtividade(
        nome=data['nome'].strip(),
        codigo=data['codigo'].strip().upper(),
        descricao=(data.get('descricao') or '').strip() or None,
        aplicavel_pf=data.get('aplicavel_pf', False),
        aplicavel_pj=data.get('aplicavel_pj', False),
        ativo=data.get('ativo', True)
    )
    db.session.add(tipo)
    db.session.commit()
    current_app.logger.info(f"Tipo de atividade criado: {tipo.nome} (ID: {tipo.id})")
    return jsonify(tipo.to_json()), 201

@tipos_atividade_bp.route('/<int:tipo_id>', methods=['PUT'])
@handle_api_errors
def update_tipo_atividade(tipo_id: int):
    tipo = TipoAtividade.query.get_or_404(tipo_id)
    data = request.get_json() or {}

    for field in ['nome', 'codigo', 'descricao', 'aplicavel_pf', 'aplicavel_pj', 'ativo']:
        if field in data:
            value = data[field]
            if field in ['nome', 'codigo'] and value:
                value = value.strip()
                if field == 'codigo':
                    value = value.upper()
            elif field == 'descricao' and value:
                value = value.strip() or None
            setattr(tipo, field, value)

    db.session.commit()
    current_app.logger.info(f"Tipo de atividade atualizado: {tipo.nome} (ID: {tipo.id})")
    return jsonify(tipo.to_json())

@tipos_atividade_bp.route('/<int:tipo_id>', methods=['DELETE'])
@handle_api_errors
def delete_tipo_atividade(tipo_id: int):
    tipo = TipoAtividade.query.get_or_404(tipo_id)
    if AtividadeRegime.query.filter_by(tipo_atividade_id=tipo_id).first():
        raise ValueError('Tipo de atividade possui regimes associados')

    nome = tipo.nome
    db.session.delete(tipo)
    db.session.commit()
    current_app.logger.info(f"Tipo de atividade removido: {nome} (ID: {tipo_id})")
    return jsonify({'message': 'Tipo de atividade removido'})

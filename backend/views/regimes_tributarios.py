"""
Views relacionadas aos regimes tributários.
"""

from flask import Blueprint, request, jsonify, current_app
from sqlalchemy import or_

from config import db
from models import RegimeTributario, AtividadeRegime
from .utils import handle_api_errors, validate_required_fields, build_search_filters

regimes_tributarios_bp = Blueprint('regimes_tributarios', __name__)

@regimes_tributarios_bp.route('/', methods=['GET'])
@handle_api_errors
def get_regimes_tributarios():
    ativo = request.args.get('ativo', type=bool)
    aplicavel_pf = request.args.get('aplicavel_pf', type=bool)
    aplicavel_pj = request.args.get('aplicavel_pj', type=bool)
    atividades_ids = request.args.getlist('atividades_ids', type=int)
    search = request.args.get('search', '').strip()

    query = RegimeTributario.query

    if ativo is not None:
        query = query.filter(RegimeTributario.ativo == ativo)
    if aplicavel_pf is not None:
        query = query.filter(RegimeTributario.aplicavel_pf == aplicavel_pf)
    if aplicavel_pj is not None:
        query = query.filter(RegimeTributario.aplicavel_pj == aplicavel_pj)

    if atividades_ids:
        query = query.join(AtividadeRegime).filter(
            AtividadeRegime.tipo_atividade_id.in_(atividades_ids),
            AtividadeRegime.ativo == True
        ).distinct()

    if search:
        search_filters = build_search_filters(RegimeTributario, search, ['nome', 'codigo', 'descricao'])
        if search_filters:
            query = query.filter(or_(*search_filters))

    regimes = query.order_by(RegimeTributario.nome).all()
    return jsonify([r.to_json() for r in regimes])

@regimes_tributarios_bp.route('/<int:regime_id>', methods=['GET'])
@handle_api_errors
def get_regime_tributario(regime_id: int):
    regime = RegimeTributario.query.get_or_404(regime_id)
    return jsonify(regime.to_json())

@regimes_tributarios_bp.route('/', methods=['POST'])
@handle_api_errors
def create_regime_tributario():
    data = request.get_json() or {}
    validation_error = validate_required_fields(data, ['nome', 'codigo'])
    if validation_error:
        return validation_error

    regime = RegimeTributario(
        nome=data['nome'].strip(),
        codigo=data['codigo'].strip().upper(),
        descricao=(data.get('descricao') or '').strip() or None,
        aplicavel_pf=data.get('aplicavel_pf', False),
        aplicavel_pj=data.get('aplicavel_pj', False),
        requer_definicoes_fiscais=data.get('requer_definicoes_fiscais', False),
        ativo=data.get('ativo', True)
    )
    db.session.add(regime)
    db.session.commit()
    current_app.logger.info(f"Regime tributário criado: {regime.nome} (ID: {regime.id})")
    return jsonify(regime.to_json()), 201

"""
Views relacionadas aos regimes tributários.
"""

try:
    from flask import Blueprint, request, jsonify, current_app
    print("🔍 DEBUG BACKEND: Flask importado com sucesso")
except ImportError as e:
    print(f"🔍 DEBUG BACKEND: Erro ao importar Flask: {e}")
    raise
try:
    from sqlalchemy import or_
    print("🔍 DEBUG BACKEND: SQLAlchemy importado com sucesso")
except ImportError as e:
    print(f"🔍 DEBUG BACKEND: Erro ao importar SQLAlchemy: {e}")
    raise

try:
    from config import db
    print("🔍 DEBUG BACKEND: DB importado com sucesso")
except ImportError as e:
    print(f"🔍 DEBUG BACKEND: Erro ao importar DB: {e}")
    raise
try:
    from models import RegimeTributario, AtividadeRegime
    print("🔍 DEBUG BACKEND: Modelos importados com sucesso")
except ImportError as e:
    print(f"🔍 DEBUG BACKEND: Erro ao importar modelos: {e}")
    raise
try:
    from .utils import handle_api_errors, validate_required_fields, build_search_filters, paginate_query
    print("🔍 DEBUG BACKEND: Utilitários importados com sucesso")
except ImportError as e:
    print(f"🔍 DEBUG BACKEND: Erro ao importar utilitários: {e}")
    raise

try:
    regimes_tributarios_bp = Blueprint('regimes_tributarios', __name__)
    print("🔍 DEBUG BACKEND: Blueprint criado com sucesso")
except Exception as e:
    print(f"🔍 DEBUG BACKEND: Erro ao criar blueprint: {e}")
    raise

@regimes_tributarios_bp.route('/', methods=['GET'])
@handle_api_errors
def get_regimes_tributarios():
    """Endpoint para listar regimes tributários com filtros opcionais"""
    try:
        print("🔍 DEBUG BACKEND: Função get_regimes_tributarios chamada")
        
        # ✅ VERIFICAR: Processar parâmetros de filtro
        atividades_ids = request.args.getlist('atividades_ids')
        ativo = request.args.get('ativo')
        aplicavel_pf = request.args.get('aplicavel_pf')
        aplicavel_pj = request.args.get('aplicavel_pj')
        search = request.args.get('search')
        
        print(f"🔍 DEBUG BACKEND: Parâmetros recebidos:")
        print(f"  - atividades_ids: {atividades_ids}")
        print(f"  - ativo: {ativo}")
        print(f"  - aplicavel_pf: {aplicavel_pf}")
        print(f"  - aplicavel_pj: {aplicavel_pj}")
        print(f"  - search: {search}")
        
        # Query base
        query = RegimeTributario.query
        
        # ✅ CORREÇÃO CRÍTICA: Aplicar filtros corretamente
        if ativo is not None:
            query = query.filter(RegimeTributario.ativo == (ativo.lower() == 'true'))
        
        # ✅ CORREÇÃO CRÍTICA: Filtrar por atividades se especificado
        if atividades_ids:
            print(f"🔍 DEBUG BACKEND: Filtrando por atividades: {atividades_ids}")
            # Buscar regimes que estão relacionados às atividades especificadas
            query = query.join(AtividadeRegime).filter(
                AtividadeRegime.tipo_atividade_id.in_(atividades_ids),
                AtividadeRegime.ativo == True
            )
        
        # ✅ CORREÇÃO CRÍTICA: Aplicar filtros de PF/PJ corretamente
        if aplicavel_pf is not None:
            query = query.filter(RegimeTributario.aplicavel_pf == (aplicavel_pf.lower() == 'true'))
        
        if aplicavel_pj is not None:
            query = query.filter(RegimeTributario.aplicavel_pj == (aplicavel_pj.lower() == 'true'))
        
        if search:
            query = query.filter(
                or_(
                    RegimeTributario.nome.ilike(f'%{search}%'),
                    RegimeTributario.codigo.ilike(f'%{search}%')
                )
            )
        
        regimes = query.distinct().all()
        print(f"🔍 DEBUG BACKEND: Total de regimes encontrados após filtros: {len(regimes)}")
        
        if regimes:
            print(f"🔍 DEBUG BACKEND: Regimes: {[r.nome for r in regimes]}")
        
        # Retornar lista filtrada
        return jsonify([r.to_json() for r in regimes])

    except Exception as e:
        print(f"🔍 DEBUG BACKEND: Erro na função get_regimes_tributarios: {e}")
        import traceback
        print(f"🔍 DEBUG BACKEND: Traceback: {traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500

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

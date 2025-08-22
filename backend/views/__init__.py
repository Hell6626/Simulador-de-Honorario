"""
Módulo de views do sistema de propostas comerciais.
Organizado por domínios de negócio para melhor manutenibilidade.
"""

# =====================================================
# IMPORTS DOS UTILITÁRIOS
# =====================================================
from .utils import handle_api_errors, validate_required_fields, paginate_query, build_search_filters

# =====================================================
# IMPORTS DAS VIEWS POR DOMÍNIO
# =====================================================
from .funcionarios import funcionarios_bp
from .clientes import clientes_bp
from .tipos_atividade import tipos_atividade_bp
from .regimes_tributarios import regimes_tributarios_bp
from .faixas_faturamento import faixas_faturamento_bp
from .servicos import servicos_bp
from .propostas import propostas_bp
from .auth import auth_bp
from .health import health_bp
from .chat import chat_bp
from .error_handlers import error_handlers_bp

# =====================================================
# BLUEPRINT PRINCIPAL
# =====================================================
from flask import Blueprint

# Blueprint principal com prefixo /api
api_bp = Blueprint('api', __name__, url_prefix='/api')

# Registra todos os blueprints
def register_blueprints(app):
    """Registra todos os blueprints da aplicação"""
    api_bp.register_blueprint(funcionarios_bp, url_prefix='/funcionarios')
    api_bp.register_blueprint(clientes_bp, url_prefix='/clientes')
    api_bp.register_blueprint(tipos_atividade_bp, url_prefix='/tipos-atividade')
    api_bp.register_blueprint(regimes_tributarios_bp, url_prefix='/regimes-tributarios')
    api_bp.register_blueprint(faixas_faturamento_bp, url_prefix='/faixas-faturamento')
    api_bp.register_blueprint(servicos_bp, url_prefix='/servicos')
    api_bp.register_blueprint(propostas_bp, url_prefix='/propostas')
    api_bp.register_blueprint(auth_bp, url_prefix='/auth')
    api_bp.register_blueprint(health_bp, url_prefix='/health')
    api_bp.register_blueprint(chat_bp, url_prefix='/chat')
    
    # Registra o blueprint principal na aplicação
    app.register_blueprint(api_bp)
    
    # Registra os error handlers
    app.register_blueprint(error_handlers_bp)

# =====================================================
# EXPORTS
# =====================================================
__all__ = [
    'api_bp',
    'register_blueprints',
    'handle_api_errors',
    'validate_required_fields',
    'paginate_query',
    'build_search_filters'
]

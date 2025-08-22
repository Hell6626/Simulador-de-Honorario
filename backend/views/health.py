"""
Views relacionadas ao health check e informações da API.
"""

from flask import Blueprint, jsonify, current_app
from sqlalchemy import text
from datetime import datetime

from config import db

health_bp = Blueprint('health', __name__)

@health_bp.route('/health', methods=['GET'])
def health_check():
    try:
        db.session.execute(text('SELECT 1')).scalar()
        return jsonify({
            'status': 'OK',
            'message': 'API funcionando corretamente!',
            'timestamp': datetime.utcnow().isoformat(),
            'database': 'OK'
        })
    except Exception as e:
        current_app.logger.error(f"Erro no healthcheck: {str(e)}")
        return jsonify({
            'status': 'ERROR',
            'message': 'Problemas na API',
            'timestamp': datetime.utcnow().isoformat(),
            'database': 'ERROR',
            'error': str(e)
        }), 503

@health_bp.route('/info', methods=['GET'])
def api_info():
    return jsonify({
        'name': 'Sistema de Propostas Contábeis',
        'version': '1.0.0',
        'endpoints': {
            'funcionarios': '/api/funcionarios',
            'clientes': '/api/clientes',
            'tipos_atividade': '/api/tipos-atividade',
            'regimes_tributarios': '/api/regimes-tributarios',
            'faixas_faturamento': '/api/faixas-faturamento',
            'propostas': '/api/propostas',
            'health': '/api/health'
        }
    })

@health_bp.get("/ping")
def ping():
    return jsonify({"pong": True, "ts": datetime.utcnow().isoformat()})

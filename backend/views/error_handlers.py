"""
Error handlers para a API.
"""

from flask import Blueprint, jsonify, current_app

from config import db

error_handlers_bp = Blueprint('error_handlers', __name__)

@error_handlers_bp.errorhandler(404)
def not_found(error):
    return jsonify({
        'error': 'Recurso não encontrado',
        'message': 'O endpoint solicitado não existe ou o recurso não foi encontrado'
    }), 404

@error_handlers_bp.errorhandler(400)
def bad_request(error):
    return jsonify({
        'error': 'Requisição inválida',
        'message': 'Os dados enviados são inválidos ou estão mal formatados'
    }), 400

@error_handlers_bp.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        'error': 'Método não permitido',
        'message': 'O método HTTP usado não é permitido para este endpoint'
    }), 405

@error_handlers_bp.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    current_app.logger.error(f"Erro interno: {str(error)}")
    return jsonify({
        'error': 'Erro interno do servidor',
        'message': 'Ocorreu um erro inesperado. Tente novamente ou contate o suporte'
    }), 500

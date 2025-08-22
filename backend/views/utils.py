"""
Utilitários e decoradores para as views da API.
"""

from flask import Blueprint, request, jsonify, current_app
from sqlalchemy.exc import IntegrityError
from sqlalchemy import or_
from typing import Dict, List, Optional, Any, Tuple
from functools import wraps
import traceback
from datetime import datetime

from config import db

def handle_api_errors(f):
    """Decorator para tratamento padronizado de erros da API"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except IntegrityError as e:
            db.session.rollback()
            current_app.logger.error(f"Erro de integridade: {str(e)}")
            return jsonify({'error': 'Dados duplicados ou violação de integridade'}), 409
        except ValueError as e:
            db.session.rollback()
            current_app.logger.error(f"Erro de validação: {str(e)}")
            return jsonify({'error': str(e)}), 400
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Erro interno: {str(e)}\n{traceback.format_exc()}")
            return jsonify({'error': 'Erro interno do servidor'}), 500
    return decorated_function

def validate_required_fields(data: Dict[str, Any], required_fields: List[str]) -> Optional[Tuple[Dict, int]]:
    """Valida campos obrigatórios"""
    missing = [field for field in required_fields if not data.get(field)]
    if missing:
        return jsonify({'error': f'Campos obrigatórios faltando: {", ".join(missing)}'}), 400
    return None

def paginate_query(query, page: int = 1, per_page: int = 20, max_per_page: int = 100):
    """Paginação padronizada para queries"""
    per_page = min(per_page, max_per_page)
    return query.paginate(page=page, per_page=per_page, error_out=False)

def build_search_filters(model, search_term: str, search_fields: List[str]):
    """Constrói filtros de busca dinamicamente"""
    if not search_term:
        return []
    filters = []
    for field in search_fields:
        if hasattr(model, field):
            attr = getattr(model, field)
            filters.append(attr.ilike(f'%{search_term}%'))
    return filters

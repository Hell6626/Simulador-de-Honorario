# config.py
import os
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate

db = SQLAlchemy()
jwt = JWTManager()

def create_app():
    """Factory para criar a aplicação Flask"""
    app = Flask(__name__)
    
    # Configurações
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///propostas.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }
    app.config['JSON_SORT_KEYS'] = False
    app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
    app.config["JWT_SECRET_KEY"] = "troque-por-uma-chave-muito-segura"
    
    # Configurações JWT simplificadas
    app.config["JWT_BLACKLIST_ENABLED"] = False
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = False  # Tokens não expiram para desenvolvimento

    # Extensões
    db.init_app(app)
    Migrate(app, db)  # ⬅️ adiciona aqui

    jwt.init_app(app)

    # Configuração CORS mais robusta para desenvolvimento
    CORS(
        app,
        origins=["http://192.168.5.202:5173", "http://localhost:5173", "http://127.0.0.1:5173"],
        allow_headers=["Content-Type", "Authorization", "Accept", "Origin", "X-Requested-With"],
        methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        supports_credentials=True,
        expose_headers=["Content-Type", "Authorization"],
        max_age=86400
    )
    
    # Handler específico para requisições OPTIONS (preflight) - mais robusto
    @app.before_request
    def handle_preflight():
        if request.method == "OPTIONS":
            # Cria uma resposta vazia para OPTIONS
            response = app.response_class()
            response.status_code = 200
            
            # Define os headers CORS
            origin = request.headers.get("Origin")
            if origin in ["http://192.168.0.99:5173", "http://localhost:5173", "http://127.0.0.1:5173"]:
                response.headers["Access-Control-Allow-Origin"] = origin
            else:
                response.headers["Access-Control-Allow-Origin"] = "*"
                
            response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
            response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, Accept, Origin, X-Requested-With"
            response.headers["Access-Control-Allow-Credentials"] = "true"
            response.headers["Access-Control-Max-Age"] = "86400"
            
            return response

    from views import register_blueprints
    register_blueprints(app)

    return app


def init_database(app):
    """Inicializa o banco de dados e dados básicos (opcional chamar no __main__)."""
    with app.app_context():
        from models import (
            Funcionario, Cliente, TipoAtividade, RegimeTributario,
            AtividadeRegime, FaixaFaturamento, Servico,
            Proposta, ItemProposta, PropostaLog,
            inicializar_dados_basicos
        )
        db.create_all()

        if not TipoAtividade.query.first():
            inicializar_dados_basicos()


if __name__ == '__main__':
    app = create_app()
    init_database(app)
    app.run(debug=True, host='0.0.0.0', port=5000)

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

    # 🌐 Configuração CORS para rede local
    CORS(
        app,
        origins=[
            "http://localhost:5173", 
            "http://127.0.0.1:5173",
            "http://192.168.0.97:5173",  # IP atual da máquina
            "http://192.168.0.*:5173",  # Qualquer IP na rede 192.168.0.x
            "http://192.168.1.*:5173",  # Qualquer IP na rede 192.168.1.x
            "http://10.0.0.*:5173",     # Qualquer IP na rede 10.0.0.x
        ],
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
            
            # Define os headers CORS para rede local
            origin = request.headers.get("Origin")
            allowed_origins = [
                "http://localhost:5173", 
                "http://127.0.0.1:5173",
                "http://192.168.0.97:5173",  # IP atual da máquina
            ]
            
            # Permitir qualquer IP na rede local (192.168.x.x, 10.x.x.x)
            if origin and (
                origin.startswith("http://192.168.") or 
                origin.startswith("http://10.") or
                origin in allowed_origins
            ):
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

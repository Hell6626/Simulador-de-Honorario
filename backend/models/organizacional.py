"""
Modelos relacionados à estrutura organizacional da empresa.
Inclui empresa, cargos e funcionários.
"""

from datetime import datetime
from config import db
from werkzeug.security import generate_password_hash, check_password_hash
from .base import TimestampMixin, ActiveMixin


class Empresa(db.Model, TimestampMixin, ActiveMixin):
    """Modelo para empresa"""
    __tablename__ = "empresa"
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False, index=True)
    cnpj = db.Column(db.String(18), nullable=False, unique=True, index=True)
    endereco = db.Column(db.String(255), nullable=False)
    telefone = db.Column(db.String(15), nullable=True)
    email = db.Column(db.String(150), nullable=True)
    
    # Relacionamentos
    cargos = db.relationship('Cargo', backref='empresa', lazy=True, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f'<Empresa {self.nome}>'
    
    def to_json(self):
        return {
            "id": self.id,
            "nome": self.nome,
            "cnpj": self.cnpj,
            "endereco": self.endereco,
            "telefone": self.telefone,
            "email": self.email,
            "ativo": self.ativo,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


class Cargo(db.Model, TimestampMixin, ActiveMixin):
    """Modelo para cargo"""
    __tablename__ = "cargo"

    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(20), nullable=False, unique=True, index=True)
    nome = db.Column(db.String(100), nullable=False, index=True)
    descricao = db.Column(db.String(255), nullable=True)
    nivel = db.Column(db.String(50), nullable=True)
    empresa_id = db.Column(db.Integer, db.ForeignKey('empresa.id'), nullable=False, index=True)
    
    # Relacionamentos
    funcionarios = db.relationship('Funcionario', backref='cargo', lazy=True)
    
    def __repr__(self):
        return f'<Cargo {self.nome}>'

    def to_json(self):
        return {
            "id": self.id,
            "codigo": self.codigo,
            "nome": self.nome,
            "nivel": self.nivel,
            "empresa_id": self.empresa_id,
            "ativo": self.ativo,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


class Funcionario(db.Model, TimestampMixin, ActiveMixin):
    """Modelo para funcionário"""
    __tablename__ = "funcionario"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), nullable=False, unique=True, index=True)
    senha_hash = db.Column(db.String(255), nullable=False)
    gerente = db.Column(db.Boolean, default=False, nullable=False)
    cargo_id = db.Column(db.Integer, db.ForeignKey('cargo.id'), nullable=False, index=True)
    empresa_id = db.Column(db.Integer, db.ForeignKey('empresa.id'), nullable=False, index=True)
    
    # Relacionamentos
    empresa = db.relationship('Empresa', backref='funcionarios', lazy=True)
    propostas = db.relationship('Proposta', backref='funcionario_responsavel', lazy=True)
    logs_proposta = db.relationship('PropostaLog', backref='funcionario', lazy=True)
    
    def __repr__(self):
        return f'<Funcionario {self.nome}>'
    
    def set_senha(self, senha: str):
        """Define a senha do funcionário com hash"""
        self.senha_hash = generate_password_hash(senha)
        
    def check_senha(self, senha: str):
        """Verifica se a senha está correta"""
        return check_password_hash(self.senha_hash, senha)
        
    def to_json(self):
        return {
            "id": self.id,
            "nome": self.nome,
            "email": self.email,
            "gerente": self.gerente,
            "cargo_id": self.cargo_id,
            "empresa_id": self.empresa_id,
            "ativo": self.ativo,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

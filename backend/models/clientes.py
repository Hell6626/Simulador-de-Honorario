"""
Modelos relacionados aos clientes do sistema.
Inclui clientes, endereços e entidades jurídicas.
"""

from datetime import datetime
from config import db
from .base import TimestampMixin, ActiveMixin


class Cliente(db.Model, TimestampMixin, ActiveMixin):
    """Modelo para cliente"""
    __tablename__ = "cliente"
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False, index=True)
    cpf = db.Column(db.String(14), nullable=False, unique=True, index=True)
    email = db.Column(db.String(150), nullable=True)
    abertura_empresa = db.Column(db.Boolean, default=False, nullable=False)
    
    # Relacionamentos
    enderecos = db.relationship('Endereco', backref='cliente', lazy=True, cascade="all, delete-orphan")
    entidades_juridicas = db.relationship('EntidadeJuridica', backref='cliente', lazy=True, cascade="all, delete-orphan")
    propostas = db.relationship('Proposta', lazy=True)
    
    def __repr__(self):
        return f'<Cliente {self.nome}>'
    
    def to_json(self):
        return {
            "id": self.id,
            "nome": self.nome,
            "cpf": self.cpf,
            "email": self.email,
            "abertura_empresa": self.abertura_empresa,
            "ativo": self.ativo,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
    
    def to_json_completo(self):
        return {
            "id": self.id,
            "nome": self.nome,
            "cpf": self.cpf,
            "email": self.email,
            "abertura_empresa": self.abertura_empresa,
            "ativo": self.ativo,
            "enderecos": [endereco.to_json() for endereco in self.enderecos],
            "entidades_juridicas": [ej.to_json() for ej in self.entidades_juridicas],
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


class Endereco(db.Model, TimestampMixin, ActiveMixin):
    """Modelo para endereço"""
    __tablename__ = "endereco"
    
    id = db.Column(db.Integer, primary_key=True)
    rua = db.Column(db.String(255), nullable=False)
    numero = db.Column(db.String(10), nullable=False)
    cidade = db.Column(db.String(100), nullable=False)
    estado = db.Column(db.String(2), nullable=False)
    cep = db.Column(db.String(10), nullable=False, index=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('cliente.id'), nullable=False, index=True)
    
    # Relacionamentos
    entidades_juridicas = db.relationship('EntidadeJuridica', backref='endereco', lazy=True)
    
    def __repr__(self):
        return f'<Endereco {self.rua}, {self.numero}, {self.cidade}, {self.estado}>'
    
    def to_json(self):
        return {
            "id": self.id,
            "rua": self.rua,
            "numero": self.numero,
            "cidade": self.cidade,
            "estado": self.estado,
            "cep": self.cep,
            "cliente_id": self.cliente_id,
            "ativo": self.ativo,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


class EntidadeJuridica(db.Model, TimestampMixin, ActiveMixin):
    """Modelo para entidade jurídica"""
    __tablename__ = "entidade_juridica"
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False, index=True)
    cnpj = db.Column(db.String(18), nullable=True, unique=True, index=True)  # Mudado para nullable=True
    tipo = db.Column(db.String(50), nullable=False)
    cliente_id = db.Column(db.Integer, db.ForeignKey('cliente.id'), nullable=False, index=True)
    endereco_id = db.Column(db.Integer, db.ForeignKey('endereco.id'), nullable=True, index=True)
    
    def __repr__(self):
        return f'<EntidadeJuridica {self.nome}>'
    
    def to_json(self):
        return {
            "id": self.id,
            "nome": self.nome,
            "cnpj": self.cnpj,
            "tipo": self.tipo,
            "cliente_id": self.cliente_id,
            "endereco_id": self.endereco_id,
            "ativo": self.ativo,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

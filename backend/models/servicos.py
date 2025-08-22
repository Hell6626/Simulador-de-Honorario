"""
Modelos relacionados aos serviços oferecidos pelo sistema.
Inclui o catálogo de serviços disponíveis para propostas.
"""

from datetime import datetime
from config import db
from .base import TimestampMixin, ActiveMixin


class Servico(db.Model, TimestampMixin, ActiveMixin):
    """Modelo para serviço"""
    __tablename__ = "servico"
    
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(20), nullable=False, unique=True, index=True)
    nome = db.Column(db.String(100), nullable=False, index=True)
    categoria = db.Column(db.String(50), nullable=False, index=True)
    tipo_cobranca = db.Column(db.String(50), nullable=False, index=True)
    valor_base = db.Column(db.Numeric(precision=15, scale=2), nullable=False)
    descricao = db.Column(db.Text, nullable=True)
    
    # Relacionamentos
    itens_proposta = db.relationship('ItemProposta', backref='servico', lazy=True)
    
    def __repr__(self):
        return f'<Servico {self.nome}>'
    
    def to_json(self):
        return {
            "id": self.id,
            "codigo": self.codigo,
            "nome": self.nome,
            "categoria": self.categoria,
            "tipo_cobranca": self.tipo_cobranca,
            "valor_base": float(self.valor_base),
            "descricao": self.descricao,
            "ativo": self.ativo,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

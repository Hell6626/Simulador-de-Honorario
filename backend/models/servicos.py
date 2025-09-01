"""
Modelos relacionados aos serviços oferecidos pelo sistema.
Inclui o catálogo de serviços disponíveis para propostas.
"""

from datetime import datetime
from config import db
from .base import TimestampMixin, ActiveMixin
from sqlalchemy import UniqueConstraint
from .tributario import RegimeTributario


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
    tipo_atividade_id = db.Column(db.Integer, db.ForeignKey('tipo_atividade.id'), nullable=True, index=True)
    
    # Relacionamentos
    itens_proposta = db.relationship('ItemProposta', backref='servico', lazy=True)
    servico_regime = db.relationship('ServicoRegime', backref='servico', lazy=True, cascade="all, delete-orphan")
    tipo_atividade = db.relationship('TipoAtividade', backref='servicos', lazy=True)
    
    def __repr__(self):
        return f'<Servico {self.nome}>'
    
    def to_json(self):
        # Buscar regimes tributários vinculados
        regimes_vinculados = []
        for servico_regime in self.servico_regime:
            if servico_regime.ativo and servico_regime.regime_tributario:
                regimes_vinculados.append({
                    "id": servico_regime.regime_tributario.id,
                    "codigo": servico_regime.regime_tributario.codigo,
                    "nome": servico_regime.regime_tributario.nome
                })
        
        return {
            "id": self.id,
            "codigo": self.codigo,
            "nome": self.nome,
            "categoria": self.categoria,
            "tipo_cobranca": self.tipo_cobranca,
            "valor_base": float(self.valor_base),
            "descricao": self.descricao,
            "tipo_atividade_id": self.tipo_atividade_id,
            "ativo": self.ativo,
            "regimes_tributarios": regimes_vinculados,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

class ServicoRegime(db.Model, TimestampMixin, ActiveMixin):
    """Modelo para relacionamento entre serviço e regime tributário"""
    __tablename__ = "servico_regime"
    
    id = db.Column(db.Integer, primary_key=True)
    servico_id = db.Column(db.Integer, db.ForeignKey('servico.id'), nullable=False, index=True)
    regime_tributario_id = db.Column(db.Integer, db.ForeignKey('regime_tributario.id'), nullable=False, index=True)
    
    # Relacionamento com RegimeTributario
    regime_tributario = db.relationship('RegimeTributario', backref='servicos_regime', lazy=True)
    
    __table_args__ = (
        UniqueConstraint('servico_id', 'regime_tributario_id', name='unique_servico_regime'),
    )
    
    def __repr__(self):
        return f'<ServicoRegime {self.servico_id} - {self.regime_tributario_id}>'
    
    def to_json(self):
        return {
            "id": self.id,
            "servico_id": self.servico_id,
            "regime_tributario_id": self.regime_tributario_id,
            "ativo": self.ativo,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
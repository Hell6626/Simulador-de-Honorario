"""
Modelos relacionados ao sistema tributário.
Inclui tipos de atividade, regimes tributários, relacionamentos e faixas de faturamento.
"""

from datetime import datetime
from config import db
from sqlalchemy import CheckConstraint, UniqueConstraint
from .base import TimestampMixin, ActiveMixin


class TipoAtividade(db.Model, TimestampMixin, ActiveMixin):
    """Modelo para tipo de atividade"""
    __tablename__ = "tipo_atividade"
    
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(20), nullable=False, unique=True, index=True)
    nome = db.Column(db.String(100), nullable=False, index=True)
    aplicavel_pf = db.Column(db.Boolean, default=False, nullable=False)
    aplicavel_pj = db.Column(db.Boolean, default=False, nullable=False)
    
    # Relacionamentos
    atividades_regime = db.relationship('AtividadeRegime', backref='tipo_atividade', lazy=True, cascade="all, delete-orphan")
    propostas = db.relationship('Proposta', backref='tipo_atividade', lazy=True)
    
    def __repr__(self):
        return f'<TipoAtividade {self.nome}>'
    
    def to_json(self):
        return {
            "id": self.id,
            "codigo": self.codigo,
            "nome": self.nome,
            "aplicavel_pf": self.aplicavel_pf,
            "aplicavel_pj": self.aplicavel_pj,
            "ativo": self.ativo,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


class RegimeTributario(db.Model, TimestampMixin, ActiveMixin):
    """Modelo para regime tributário"""
    __tablename__ = "regime_tributario"
    
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(20), nullable=False, unique=True, index=True)
    nome = db.Column(db.String(100), nullable=False, index=True)
    descricao = db.Column(db.Text, nullable=True)
    aplicavel_pf = db.Column(db.Boolean, default=False, nullable=False)
    aplicavel_pj = db.Column(db.Boolean, default=False, nullable=False)
    
    # Relacionamentos
    atividades_regime = db.relationship('AtividadeRegime', backref='regime_tributario', lazy=True, cascade="all, delete-orphan")
    faixas_faturamento = db.relationship('FaixaFaturamento', backref='regime_tributario', lazy=True, cascade="all, delete-orphan")
    propostas = db.relationship('Proposta', backref='regime_tributario', lazy=True)
    
    def __repr__(self):
        return f'<RegimeTributario {self.nome}>'
    
    def to_json(self):
        return {
            "id": self.id,
            "codigo": self.codigo,
            "nome": self.nome,
            "descricao": self.descricao,
            "aplicavel_pf": self.aplicavel_pf,
            "aplicavel_pj": self.aplicavel_pj,
            "ativo": self.ativo,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


class AtividadeRegime(db.Model, TimestampMixin, ActiveMixin):
    """Modelo para relacionamento entre atividade e regime tributário"""
    __tablename__ = "atividade_regime"
    
    id = db.Column(db.Integer, primary_key=True)
    tipo_atividade_id = db.Column(db.Integer, db.ForeignKey('tipo_atividade.id'), nullable=False, index=True)
    regime_tributario_id = db.Column(db.Integer, db.ForeignKey('regime_tributario.id'), nullable=False, index=True)
    
    __table_args__ = (
        UniqueConstraint('tipo_atividade_id', 'regime_tributario_id', name='unique_atividade_regime'),
    )
    
    def __repr__(self):
        return f'<AtividadeRegime {self.tipo_atividade_id} - {self.regime_tributario_id}>'
    
    def to_json(self):
        return {
            "id": self.id,
            "tipo_atividade_id": self.tipo_atividade_id,
            "regime_tributario_id": self.regime_tributario_id,
            "ativo": self.ativo,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


class FaixaFaturamento(db.Model, TimestampMixin, ActiveMixin):
    """Modelo para faixa de faturamento"""
    __tablename__ = "faixa_faturamento"
    
    id = db.Column(db.Integer, primary_key=True)
    regime_tributario_id = db.Column(db.Integer, db.ForeignKey('regime_tributario.id'), nullable=False, index=True)
    valor_inicial = db.Column(db.Numeric(precision=15, scale=2), nullable=False)
    valor_final = db.Column(db.Numeric(precision=15, scale=2), nullable=True)
    aliquota = db.Column(db.Numeric(precision=5, scale=2), nullable=False)
    
    # Relacionamentos
    propostas = db.relationship('Proposta', backref='faixa_faturamento', lazy=True)
    
    __table_args__ = (
        UniqueConstraint('regime_tributario_id', 'valor_inicial', 'valor_final', name='unique_faixa_faturamento'),
    )
    
    def __repr__(self):
        return f'<FaixaFaturamento {self.valor_inicial} - {self.valor_final}>'
    
    def to_json(self):
        # Buscar informações do regime tributário
        regime_info = None
        if self.regime_tributario:
            regime_info = {
                "id": self.regime_tributario.id,
                "codigo": self.regime_tributario.codigo,
                "nome": self.regime_tributario.nome
            }
        
        return {
            "id": self.id,
            "regime_tributario_id": self.regime_tributario_id,
            "regime_tributario": regime_info,
            "valor_inicial": float(self.valor_inicial) if self.valor_inicial else 0.0,
            "valor_final": float(self.valor_final) if self.valor_final else None,
            "aliquota": float(self.aliquota) if self.aliquota else 0.0,
            "ativo": self.ativo,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

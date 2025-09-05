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


class MensalidadeAutomatica(db.Model, TimestampMixin, ActiveMixin):
    """Modelo para mensalidade automática baseada em configuração tributária"""
    __tablename__ = "mensalidade_automatica"
    
    id = db.Column(db.Integer, primary_key=True)
    tipo_atividade_id = db.Column(db.Integer, db.ForeignKey('tipo_atividade.id'), nullable=False, index=True)
    regime_tributario_id = db.Column(db.Integer, db.ForeignKey('regime_tributario.id'), nullable=False, index=True)
    faixa_faturamento_id = db.Column(db.Integer, db.ForeignKey('faixa_faturamento.id'), nullable=False, index=True)
    valor_mensalidade = db.Column(db.Numeric(precision=15, scale=2), nullable=False)
    observacoes = db.Column(db.Text, nullable=True)
    
    # Relacionamentos
    tipo_atividade = db.relationship('TipoAtividade', backref='mensalidades_automaticas', lazy=True)
    regime_tributario = db.relationship('RegimeTributario', backref='mensalidades_automaticas', lazy=True)
    faixa_faturamento = db.relationship('FaixaFaturamento', backref='mensalidades_automaticas', lazy=True)
    
    __table_args__ = (
        UniqueConstraint('tipo_atividade_id', 'regime_tributario_id', 'faixa_faturamento_id', name='unique_mensalidade_config'),
    )
    
    def __repr__(self):
        return f'<MensalidadeAutomatica {self.tipo_atividade_id}-{self.regime_tributario_id}-{self.faixa_faturamento_id}>'
    
    def to_json(self):
        # Buscar informações relacionadas
        tipo_atividade_info = None
        if self.tipo_atividade:
            tipo_atividade_info = {
                "id": self.tipo_atividade.id,
                "codigo": self.tipo_atividade.codigo,
                "nome": self.tipo_atividade.nome
            }
        
        regime_tributario_info = None
        if self.regime_tributario:
            regime_tributario_info = {
                "id": self.regime_tributario.id,
                "codigo": self.regime_tributario.codigo,
                "nome": self.regime_tributario.nome
            }
        
        faixa_faturamento_info = None
        if self.faixa_faturamento:
            faixa_faturamento_info = {
                "id": self.faixa_faturamento.id,
                "valor_inicial": float(self.faixa_faturamento.valor_inicial) if self.faixa_faturamento.valor_inicial else 0.0,
                "valor_final": float(self.faixa_faturamento.valor_final) if self.faixa_faturamento.valor_final else None,
                "aliquota": float(self.faixa_faturamento.aliquota) if self.faixa_faturamento.aliquota else 0.0
            }
        
        return {
            "id": self.id,
            "tipo_atividade_id": self.tipo_atividade_id,
            "tipo_atividade": tipo_atividade_info,
            "regime_tributario_id": self.regime_tributario_id,
            "regime_tributario": regime_tributario_info,
            "faixa_faturamento_id": self.faixa_faturamento_id,
            "faixa_faturamento": faixa_faturamento_info,
            "valor_mensalidade": float(self.valor_mensalidade) if self.valor_mensalidade else 0.0,
            "observacoes": self.observacoes,
            "ativo": self.ativo,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
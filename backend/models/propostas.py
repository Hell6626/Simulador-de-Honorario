"""
Modelos relacionados às propostas comerciais.
Inclui propostas, itens de proposta e logs de alterações.
"""

from datetime import datetime
from config import db
from sqlalchemy import CheckConstraint
from .base import TimestampMixin, ActiveMixin


class Proposta(db.Model, TimestampMixin, ActiveMixin):
    """Modelo para proposta"""
    __tablename__ = "proposta"
    
    id = db.Column(db.Integer, primary_key=True)
    numero = db.Column(db.String(50), nullable=False, unique=True, index=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('cliente.id'), nullable=False, index=True)
    funcionario_responsavel_id = db.Column(db.Integer, db.ForeignKey('funcionario.id'), nullable=False, index=True)
    tipo_atividade_id = db.Column(db.Integer, db.ForeignKey('tipo_atividade.id'), nullable=False, index=True)
    regime_tributario_id = db.Column(db.Integer, db.ForeignKey('regime_tributario.id'), nullable=False, index=True)
    faixa_faturamento_id = db.Column(db.Integer, db.ForeignKey('faixa_faturamento.id'), nullable=True, index=True)
    valor_total = db.Column(db.Numeric(precision=15, scale=2), nullable=False, default=0)
    percentual_desconto = db.Column(db.Integer, nullable=False, default=0)  # Percentual de desconto (0-100)
    requer_aprovacao = db.Column(db.Boolean, default=False)  # Se requer aprovação gerencial
    aprovada_por = db.Column(db.Integer, db.ForeignKey('funcionario.id'), nullable=True)  # ID do gerente que aprovou
    data_aprovacao = db.Column(db.DateTime, nullable=True)  # Data da aprovação
    motivo_rejeicao = db.Column(db.Text, nullable=True)  # Motivo da rejeição (se aplicável)
    data_validade = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='RASCUNHO', index=True)
    observacoes = db.Column(db.Text, nullable=True)
    
    # Campos para PDF
    pdf_gerado = db.Column(db.Boolean, default=False, index=True)
    pdf_caminho = db.Column(db.String(500), nullable=True)
    pdf_data_geracao = db.Column(db.DateTime, nullable=True)
    
    # Relacionamentos
    itens = db.relationship('ItemProposta', back_populates='proposta', lazy=True, cascade="all, delete-orphan")
    logs = db.relationship('PropostaLog', backref='proposta', lazy=True, cascade="all, delete-orphan")
    cliente = db.relationship('Cliente', lazy='joined')
    funcionario_responsavel = db.relationship('Funcionario', foreign_keys=[funcionario_responsavel_id], lazy='joined')
    aprovador = db.relationship('Funcionario', foreign_keys=[aprovada_por], lazy='joined')
    
    def __repr__(self):
        return f'<Proposta {self.numero}>'
    
    def to_json(self):
        return {
            "id": self.id,
            "numero": self.numero,
            "cliente_id": self.cliente_id,
            "funcionario_responsavel_id": self.funcionario_responsavel_id,
            "tipo_atividade_id": self.tipo_atividade_id,
            "regime_tributario_id": self.regime_tributario_id,
            "faixa_faturamento_id": self.faixa_faturamento_id,
            "valor_total": float(self.valor_total),
            "percentual_desconto": self.percentual_desconto,
            "requer_aprovacao": self.requer_aprovacao,
            "aprovada_por": self.aprovada_por,
            "data_aprovacao": self.data_aprovacao.isoformat() if self.data_aprovacao else None,
            "motivo_rejeicao": self.motivo_rejeicao,
            "data_validade": self.data_validade.isoformat() if self.data_validade else None,
            "status": self.status,
            "observacoes": self.observacoes,
            "ativo": self.ativo,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            # ⚠️ INCLUIR: Relacionamentos com cliente e funcionário
            "cliente": {
                "id": self.cliente.id,
                "nome": self.cliente.nome,
                "cpf": self.cliente.cpf,
                "email": self.cliente.email
            } if hasattr(self, 'cliente') and self.cliente else None,
            "funcionario_responsavel": {
                "id": self.funcionario_responsavel.id,
                "nome": self.funcionario_responsavel.nome,
                "email": self.funcionario_responsavel.email
            } if hasattr(self, 'funcionario_responsavel') and self.funcionario_responsavel else None,
            # ⚠️ INCLUIR: Itens da proposta
            "itens": [item.to_json() for item in self.itens if item.ativo] if hasattr(self, 'itens') else [],
            # Campos de PDF
            "pdf_gerado": self.pdf_gerado,
            "pdf_caminho": self.pdf_caminho,
            "pdf_data_geracao": self.pdf_data_geracao.isoformat() if self.pdf_data_geracao else None
        }
    
    def calcular_requer_aprovacao(self):
        """Verifica se a proposta requer aprovação gerencial"""
        return self.percentual_desconto > 20
    
    def aprovar(self, gerente_id):
        """Aprova a proposta por um gerente"""
        from datetime import datetime
        from models.notificacoes import Notificacao
        
        self.requer_aprovacao = False
        self.aprovada_por = gerente_id
        self.data_aprovacao = datetime.utcnow()
        self.status = 'APROVADA'
        self.motivo_rejeicao = None
        
        # Criar notificação para o funcionário responsável
        Notificacao.criar_notificacao_aprovacao_gerenciada(self, gerente_id, aprovada=True)
        
        db.session.commit()
    
    def rejeitar(self, gerente_id, motivo):
        """Rejeita a proposta por um gerente"""
        from datetime import datetime
        from models.notificacoes import Notificacao
        
        self.requer_aprovacao = False
        self.aprovada_por = gerente_id
        self.data_aprovacao = datetime.utcnow()
        self.status = 'REJEITADA'
        self.motivo_rejeicao = motivo
        
        # Criar notificação para o funcionário responsável
        Notificacao.criar_notificacao_aprovacao_gerenciada(self, gerente_id, aprovada=False)
        
        db.session.commit()


class ItemProposta(db.Model, TimestampMixin, ActiveMixin):
    """Modelo para item de proposta"""
    __tablename__ = "item_proposta"
    
    id = db.Column(db.Integer, primary_key=True)
    proposta_id = db.Column(db.Integer, db.ForeignKey('proposta.id', ondelete='CASCADE'), nullable=False, index=True)
    servico_id = db.Column(db.Integer, db.ForeignKey('servico.id'), nullable=False, index=True)
    quantidade = db.Column(db.Numeric(precision=10, scale=2), nullable=False, default=1.0)
    valor_unitario = db.Column(db.Numeric(precision=15, scale=2), nullable=False)
    valor_total = db.Column(db.Numeric(precision=15, scale=2), nullable=False)
    descricao_personalizada = db.Column(db.Text, nullable=True)
    
    # ⚠️ RELACIONAMENTOS
    proposta = db.relationship('Proposta', back_populates='itens')
    # servico é criado automaticamente pelo backref em Servico.itens_proposta
    
    __table_args__ = (
        CheckConstraint('quantidade > 0', name='check_quantidade'),
        CheckConstraint('valor_unitario >= 0', name='check_valor_unitario'),
        CheckConstraint('valor_total >= 0', name='check_valor_total')
    )
    
    def __repr__(self):
        return f'<ItemProposta {self.servico.nome if self.servico else "N/A"}>'
    
    def to_json(self):
        return {
            "id": self.id,
            "proposta_id": self.proposta_id,
            "servico_id": self.servico_id,
            "quantidade": float(self.quantidade),
            "valor_unitario": float(self.valor_unitario),
            "valor_total": float(self.valor_total),
            "descricao_personalizada": self.descricao_personalizada,
            "ativo": self.ativo,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


class PropostaLog(db.Model, TimestampMixin):
    """Modelo para log de propostas"""
    __tablename__ = "proposta_log"
    
    id = db.Column(db.Integer, primary_key=True)
    proposta_id = db.Column(db.Integer, db.ForeignKey('proposta.id', ondelete='CASCADE'), nullable=False, index=True)
    funcionario_id = db.Column(db.Integer, db.ForeignKey('funcionario.id'), nullable=False, index=True)
    acao = db.Column(db.String(50), nullable=False, index=True)
    detalhes = db.Column(db.Text, nullable=True)
    
    def __repr__(self):
        return f'<PropostaLog {self.proposta.numero if self.proposta else "N/A"} - {self.acao}>'
    
    def to_json(self):
        return {
            "id": self.id,
            "proposta_id": self.proposta_id,
            "funcionario_id": self.funcionario_id,
            "acao": self.acao,
            "detalhes": self.detalhes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

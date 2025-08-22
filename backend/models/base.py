"""
Classes base e mixins para os modelos do sistema.
Contém funcionalidades comuns reutilizáveis.
"""

from datetime import datetime
from config import db


class TimestampMixin:
    """Adiciona campos de data de criação/atualização automáticos"""
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
class ActiveMixin:
    """Adiciona campo para soft delete (ativo/inativo)"""
    ativo = db.Column(db.Boolean, default=True, nullable=False, index=True)

    @classmethod
    def ativos(cls):
        """Query para registros ativos"""
        return cls.query.filter(cls.ativo == True)
    
    def desativar(self):
        """Desativa o registro"""
        self.ativo = False
        self.updated_at = datetime.utcnow()
        
    def ativar(self):
        """Ativa o registro"""
        self.ativo = True
        self.updated_at = datetime.utcnow()

"""
Modelo de notificações para o sistema de aprovação gerencial.
"""

from datetime import datetime
from config import db
from .base import TimestampMixin, ActiveMixin


class Notificacao(db.Model, TimestampMixin, ActiveMixin):
    """Modelo para notificações do sistema"""
    
    __tablename__ = 'notificacao'
    
    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(50), nullable=False)  # 'APROVACAO_DESCONTO', 'SISTEMA', etc.
    titulo = db.Column(db.String(200), nullable=False)
    mensagem = db.Column(db.Text, nullable=False)
    proposta_id = db.Column(db.Integer, db.ForeignKey('proposta.id'), nullable=True)
    para_funcionario_id = db.Column(db.Integer, db.ForeignKey('funcionario.id'), nullable=False)
    de_funcionario_id = db.Column(db.Integer, db.ForeignKey('funcionario.id'), nullable=True)
    lida = db.Column(db.Boolean, default=False)
    data_leitura = db.Column(db.DateTime, nullable=True)
    deleted_at = db.Column(db.DateTime, nullable=True)  # NOVO CAMPO PARA SOFT DELETE
    
    # Relacionamentos
    proposta = db.relationship('Proposta', backref='notificacoes')
    para_funcionario = db.relationship('Funcionario', foreign_keys=[para_funcionario_id], backref='notificacoes_recebidas')
    de_funcionario = db.relationship('Funcionario', foreign_keys=[de_funcionario_id], backref='notificacoes_enviadas')
    
    @property
    def is_deleted(self):
        """Verifica se a notificação foi deletada (soft delete)"""
        return self.deleted_at is not None
    
    def to_json(self):
        """Converte para JSON"""
        return {
            'id': self.id,
            'tipo': self.tipo,
            'titulo': self.titulo,
            'mensagem': self.mensagem,
            'proposta_id': self.proposta_id,
            'para_funcionario_id': self.para_funcionario_id,
            'de_funcionario_id': self.de_funcionario_id,
            'lida': self.lida,
            'data_leitura': self.data_leitura.isoformat() if self.data_leitura else None,
            'deleted_at': self.deleted_at.isoformat() if self.deleted_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'ativo': self.ativo
        }
    
    def marcar_como_lida(self):
        """Marca a notificação como lida e aplica soft delete"""
        self.lida = True
        self.data_leitura = datetime.utcnow()
        self.deleted_at = datetime.utcnow()  # SOFT DELETE
        db.session.commit()
    
    @classmethod
    def criar_notificacao_aprovacao(cls, proposta, de_funcionario_id=None, is_update=False):
        """Cria notificação de aprovação para gerentes"""
        from models.organizacional import Funcionario
        
        # Buscar gerentes ativos
        gerentes = Funcionario.query.filter_by(gerente=True, ativo=True).all()
        
        # Mensagem diferente para criação vs atualização
        acao = "atualizada" if is_update else "criada"
        
        notificacoes_criadas = []
        for gerente in gerentes:
            # Não criar notificação para o próprio funcionário que criou a proposta
            if de_funcionario_id and gerente.id == de_funcionario_id:
                continue
                
            notificacao = cls(
                tipo='APROVACAO_DESCONTO',
                titulo=f'Aprovação Necessária - Proposta {proposta.numero}',
                mensagem=f'Proposta {acao} com desconto de {proposta.percentual_desconto:.1f}% requer sua aprovação. Cliente: {proposta.cliente.nome if proposta.cliente else "N/A"}',
                proposta_id=proposta.id,
                para_funcionario_id=gerente.id,
                de_funcionario_id=de_funcionario_id,
                lida=False
            )
            
            db.session.add(notificacao)
            notificacoes_criadas.append(notificacao)
        
        db.session.commit()
        return notificacoes_criadas
    
    @classmethod
    def criar_notificacao_aprovacao_gerenciada(cls, proposta, aprovada_por_id, aprovada=True):
        """Cria notificação informando sobre aprovação/rejeição"""
        if not proposta.funcionario_responsavel_id:
            return None
            
        status = "APROVADA" if aprovada else "REJEITADA"
        gerente = Funcionario.query.get(aprovada_por_id)
        nome_gerente = gerente.nome if gerente else "Gerente"
        
        notificacao = cls(
            tipo='RESPOSTA_APROVACAO',
            titulo=f'Proposta {proposta.numero} - {status}',
            mensagem=f'Sua proposta foi {status.lower()} pelo {nome_gerente}. Desconto: {proposta.percentual_desconto:.1f}%',
            proposta_id=proposta.id,
            para_funcionario_id=proposta.funcionario_responsavel_id,
            de_funcionario_id=aprovada_por_id,
            lida=False
        )
        
        db.session.add(notificacao)
        db.session.commit()
        return notificacao

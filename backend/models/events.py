"""
Event listeners do SQLAlchemy para automatizar cálculos e validações.
"""

from sqlalchemy import event
from config import db
from .propostas import Proposta, ItemProposta


@event.listens_for(ItemProposta, 'before_insert')
@event.listens_for(ItemProposta, 'before_update')
def calcular_valor_total_item(mapper, connection, target):
    """Calcula o valor total do item antes de inserir/atualizar"""
    if target.quantidade and target.valor_unitario:
        target.valor_total = target.quantidade * target.valor_unitario


@event.listens_for(Proposta, 'after_update')
def atualizar_valor_total_proposta(mapper, connection, target):
    """Atualiza o valor total da proposta após alterações nos itens"""
    if target.itens:
        target.valor_total = sum(item.valor_total for item in target.itens if item.ativo)
    else:
        target.valor_total = 0

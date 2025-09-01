"""
Módulo de modelos do sistema de propostas comerciais.
Organizado por domínios de negócio para melhor manutenibilidade.
"""

# =====================================================
# IMPORTS DOS MIXINS E CLASSES BASE
# =====================================================
from .base import TimestampMixin, ActiveMixin

# =====================================================
# IMPORTS DOS MODELOS ORGANIZACIONAIS
# =====================================================
from .organizacional import Empresa, Cargo, Funcionario

# =====================================================
# IMPORTS DOS MODELOS DE CLIENTES
# =====================================================
from .clientes import Cliente, Endereco, EntidadeJuridica

# =====================================================
# IMPORTS DOS MODELOS TRIBUTÁRIOS
# =====================================================
from .tributario import TipoAtividade, RegimeTributario, AtividadeRegime, FaixaFaturamento

# =====================================================
# IMPORTS DOS MODELOS DE SERVIÇOS
# =====================================================
from .servicos import Servico

# =====================================================
# IMPORTS DOS MODELOS DE PROPOSTAS
# =====================================================
from .propostas import Proposta, ItemProposta, PropostaLog
from .notificacoes import Notificacao

# =====================================================
# IMPORTS DOS SERVIÇOS
# =====================================================
from .services import PropostaService

# =====================================================
# IMPORTS DOS EVENT LISTENERS
# =====================================================
from .events import *

# =====================================================
# IMPORTS DAS FUNÇÕES DE INICIALIZAÇÃO
# =====================================================
from .initialization import (
    inicializar_dados_basicos, 
    inicializar_faixas_faturamento,
    criar_usuario_admin,
    inicializar_sistema_completo
)

# =====================================================
# LISTA DE TODOS OS MODELOS PARA FACILITAR IMPORTS
# =====================================================
__all__ = [
    # Mixins e Base
    'TimestampMixin',
    'ActiveMixin',
    
    # Organizacional
    'Empresa',
    'Cargo', 
    'Funcionario',
    
    # Clientes
    'Cliente',
    'Endereco',
    'EntidadeJuridica',
    
    # Tributário
    'TipoAtividade',
    'RegimeTributario',
    'AtividadeRegime',
    'FaixaFaturamento',
    
    # Serviços
    'Servico',
    
    # Propostas
    'Proposta',
    'ItemProposta',
    'PropostaLog',
    
    # Serviços
    'PropostaService',
    
    # Funções
    'inicializar_dados_basicos',
    'inicializar_faixas_faturamento',
    'criar_usuario_admin',
    'inicializar_sistema_completo'
]

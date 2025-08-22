# models.py - Versão Melhorada
from config import db
from datetime import datetime, timezone
from sqlalchemy import CheckConstraint, UniqueConstraint, Index, event
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.sqlite import JSON
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.sql import expression
from decimal import Decimal
from typing import Dict, List, Optional, Any
import json
import re
from werkzeug.security import generate_password_hash, check_password_hash

# =====================================================
# MIXINS E CLASSES BASE
# =====================================================

class TimestampMixin:
    """Mixin para campos de timestamp"""
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

class ActiveMixin:
    """Mixin para controle de ativo/inativo"""
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


# =====================================================
# MODELOS PRINCIPAIS
# =====================================================

class Funcionario(db.Model, TimestampMixin, ActiveMixin):
    """Modelo para funcionários"""
    __tablename__ = "funcionarios"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False, index=True)
    email = db.Column(db.String(100), unique=True, nullable=False, index=True)
    telefone = db.Column(db.String(20))
    cargo = db.Column(db.String(50), index=True)
    senha_hash = db.Column(db.String(255), nullable=False)

    # Relacionamentos
    propostas = db.relationship('Proposta', backref='funcionario', lazy=True)
    historicos = db.relationship('PropostaHistorico', backref='funcionario', lazy=True)

    def __repr__(self):
        return f'<Funcionario {self.nome}>'
    
    def set_senha(self, senha: str):
        self.senha_hash = generate_password_hash(senha)

    def check_senha(self, senha: str) -> bool:
        return check_password_hash(self.senha_hash, senha)

    def to_json(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "nome": self.nome,
            "email": self.email,
            "telefone": self.telefone,
            "cargo": self.cargo,
            "ativo": self.ativo,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

    def pode_ser_removido(self) -> bool:
        """Verifica se o funcionário pode ser removido"""
        return not bool(self.propostas)

    @classmethod
    def buscar(cls, termo: str):
        """Busca funcionários por termo"""
        if not termo:
            return cls.query
        
        termo = f"%{termo.strip()}%"
        return cls.query.filter(
            db.or_(
                cls.nome.ilike(termo),
                cls.email.ilike(termo),
                cls.cargo.ilike(termo)
            )
        )


class Cliente(db.Model, TimestampMixin, ActiveMixin):
    """Modelo para clientes (PF e PJ)"""
    __tablename__ = "clientes"

    id = db.Column(db.Integer, primary_key=True)
    tipo_pessoa = db.Column(db.String(1), nullable=False, index=True)
    
    # Dados Pessoa Física
    nome = db.Column(db.String(200), index=True)
    cpf = db.Column(db.String(14), index=True)
    
    # Dados Pessoa Jurídica
    razao_social = db.Column(db.String(200), index=True)
    nome_fantasia = db.Column(db.String(200), index=True)
    cnpj = db.Column(db.String(18), index=True)
    
    # Dados Comuns
    telefone = db.Column(db.String(20))
    email = db.Column(db.String(100), index=True)
    endereco = db.Column(db.Text)
    
    abertura_empresa = db.Column(
        db.Boolean,
        nullable=False,
        server_default=expression.false()
    )

    # Constraints
    __table_args__ = (
        CheckConstraint(tipo_pessoa.in_(['F', 'J']), name='check_tipo_pessoa'),
        # Garantir que CPF seja único quando preenchido
        Index('ix_cliente_cpf_unique', cpf, unique=True, 
              postgresql_where=db.and_(cpf.isnot(None), cpf != '')),
        # Garantir que CNPJ seja único quando preenchido
        Index('ix_cliente_cnpj_unique', cnpj, unique=True,
              postgresql_where=db.and_(cnpj.isnot(None), cnpj != '')),
    )

    # Relacionamentos
    propostas = db.relationship('Proposta', backref='cliente', lazy=True)

    def __repr__(self):
        nome_display = self.nome if self.tipo_pessoa == 'F' else self.razao_social
        return f'<Cliente {nome_display}>'

    @hybrid_property
    def nome_completo(self):
        """Retorna o nome completo baseado no tipo de pessoa"""
        if self.tipo_pessoa == 'F':
            return self.nome
        return self.razao_social

    @hybrid_property
    def documento_principal(self):
        """Retorna o documento principal (CPF ou CNPJ)"""
        if self.tipo_pessoa == 'F':
            return self.cpf
        return self.cnpj

    @hybrid_property
    def eh_pessoa_fisica(self):
        """Verifica se é pessoa física"""
        return self.tipo_pessoa == 'F'

    @hybrid_property
    def eh_pessoa_juridica(self):
        """Verifica se é pessoa jurídica"""
        return self.tipo_pessoa == 'J'

    def to_json(self) -> Dict[str, Any]:
        base_data = {
            "id": self.id,
            "tipo_pessoa": self.tipo_pessoa,
            "telefone": self.telefone,
            "email": self.email,
            "endereco": self.endereco,
            "ativo": self.ativo,
            "abertura_empresa": bool(self.abertura_empresa),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

        if self.tipo_pessoa == 'F':
            base_data.update({
                "nome": self.nome,
                "cpf": self.cpf,
                "documento": self.cpf,
                "nome_completo": self.nome
            })
        else:
            base_data.update({
                "razao_social": self.razao_social,
                "nome_fantasia": self.nome_fantasia,
                "cnpj": self.cnpj,
                "documento": None if self.abertura_empresa else self.cnpj,
                "nome_completo": self.razao_social
            })

        return base_data

    def pode_ser_removido(self) -> bool:
        """Verifica se o cliente pode ser removido"""
        return not bool(self.propostas)

    @classmethod
    def buscar(cls, termo: str):
        """Busca clientes por termo"""
        if not termo:
            return cls.query
        
        termo = f"%{termo.strip()}%"
        return cls.query.filter(
            db.or_(
                cls.nome.ilike(termo),
                cls.razao_social.ilike(termo),
                cls.nome_fantasia.ilike(termo),
                cls.cpf.ilike(termo),
                cls.cnpj.ilike(termo),
                cls.email.ilike(termo)
            )
        )

    def validar_dados_pf(self) -> List[str]:
        """Valida dados específicos de pessoa física"""
        erros = []
        if not self.nome or not self.nome.strip():
            erros.append("Nome é obrigatório para pessoa física")
        if not self.cpf or not self.cpf.strip():
            erros.append("CPF é obrigatório para pessoa física")
        elif not self._validar_cpf(self.cpf):
            erros.append("CPF inválido")
        return erros

    def validar_dados_pj(self) -> List[str]:
        """Valida dados específicos de pessoa jurídica"""
        erros = []
        if not self.abertura_empresa:
            if not self.razao_social or not self.razao_social.strip():
                erros.append("Razão social é obrigatória para pessoa jurídica")
            if not self.cnpj or not self.cnpj.strip():
                erros.append("CNPJ é obrigatório para pessoa jurídica")
            elif not self._validar_cnpj(self.cnpj):
                erros.append("CNPJ inválido")
        else:
            if not self.nome or not self.nome.strip():
                erros.append("Nome é obrigatório para abertura de empresa")
            if not self.cpf or not self.cpf.strip():
                erros.append("CPF é obrigatório para abertura de empresa")
            elif not self._validar_cpf(self.cpf):
                erros.append("CPF inválido")
        return erros

    def validar(self) -> List[str]:
        """Valida todos os dados do cliente"""
        if self.tipo_pessoa == 'F':
            return self.validar_dados_pf()
        elif self.tipo_pessoa == 'J':
            return self.validar_dados_pj()
        else:
            return ["Tipo de pessoa inválido"]

    @staticmethod
    def _validar_cpf(cpf: str) -> bool:
        """Valida CPF (algoritmo simplificado)"""
        if not cpf:
            return False
        
        # Remove caracteres não numéricos
        cpf = re.sub(r'[^0-9]', '', cpf)
        
        # Verifica se tem 11 dígitos
        if len(cpf) != 11:
            return False
        
        # Verifica se não são todos iguais
        if len(set(cpf)) == 1:
            return False
        
        # Aqui poderia implementar a validação completa do CPF
        return True

    @staticmethod
    def _validar_cnpj(cnpj: str) -> bool:
        """Valida CNPJ (algoritmo simplificado)"""
        if not cnpj:
            return False
        
        # Remove caracteres não numéricos
        cnpj = re.sub(r'[^0-9]', '', cnpj)
        
        # Verifica se tem 14 dígitos
        if len(cnpj) != 14:
            return False
        
        # Verifica se não são todos iguais
        if len(set(cnpj)) == 1:
            return False
        
        # Aqui poderia implementar a validação completa do CNPJ
        return True


class TipoAtividade(db.Model, ActiveMixin):
    """Modelo para tipos de atividade"""
    __tablename__ = "tipos_atividade"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(50), nullable=False, unique=True, index=True)
    codigo = db.Column(db.String(10), nullable=False, unique=True, index=True)
    descricao = db.Column(db.Text)
    aplicavel_pf = db.Column(db.Boolean, default=False, nullable=False)
    aplicavel_pj = db.Column(db.Boolean, default=False, nullable=False)

    # Relacionamentos
    regimes_permitidos = db.relationship(
        'AtividadeRegimePermitido', 
        backref='tipo_atividade', 
        lazy=True,
        cascade='all, delete-orphan'
    )

    def __repr__(self):
        return f'<TipoAtividade {self.nome}>'

    def to_json(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "nome": self.nome,
            "codigo": self.codigo,
            "descricao": self.descricao,
            "aplicavel_pf": self.aplicavel_pf,
            "aplicavel_pj": self.aplicavel_pj,
            "ativo": self.ativo
        }

    @classmethod
    def para_tipo_pessoa(cls, tipo_pessoa: str):
        """Filtra atividades aplicáveis ao tipo de pessoa"""
        if tipo_pessoa == 'F':
            return cls.query.filter(cls.aplicavel_pf == True)
        elif tipo_pessoa == 'J':
            return cls.query.filter(cls.aplicavel_pj == True)
        return cls.query

    def pode_ser_removido(self) -> bool:
        """Verifica se o tipo pode ser removido"""
        return not bool(self.regimes_permitidos)


class RegimeTributario(db.Model, ActiveMixin):
    """Modelo para regimes tributários"""
    __tablename__ = "regimes_tributarios"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(50), nullable=False, unique=True, index=True)
    codigo = db.Column(db.String(10), nullable=False, unique=True, index=True)
    descricao = db.Column(db.Text)
    aplicavel_pf = db.Column(db.Boolean, default=False, nullable=False)
    aplicavel_pj = db.Column(db.Boolean, default=False, nullable=False)
    requer_definicoes_fiscais = db.Column(db.Boolean, default=False, nullable=False)

    # Relacionamentos
    faixas_faturamento = db.relationship(
        'FaixaFaturamento', 
        backref='regime_tributario', 
        lazy=True,
        cascade='all, delete-orphan'
    )
    propostas = db.relationship('Proposta', backref='regime_tributario', lazy=True)
    atividades_permitidas = db.relationship(
        'AtividadeRegimePermitido',
        backref='regime_tributario',
        lazy=True,
        cascade='all, delete-orphan'
    )

    def __repr__(self):
        return f'<RegimeTributario {self.nome}>'

    def to_json(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "nome": self.nome,
            "codigo": self.codigo,
            "descricao": self.descricao,
            "aplicavel_pf": self.aplicavel_pf,
            "aplicavel_pj": self.aplicavel_pj,
            "requer_definicoes_fiscais": self.requer_definicoes_fiscais,
            "ativo": self.ativo,
            "possui_faixas": bool(self.faixas_faturamento)
        }

    @classmethod
    def para_tipo_pessoa(cls, tipo_pessoa: str):
        """Filtra regimes aplicáveis ao tipo de pessoa"""
        if tipo_pessoa == 'F':
            return cls.query.filter(cls.aplicavel_pf == True)
        elif tipo_pessoa == 'J':
            return cls.query.filter(cls.aplicavel_pj == True)
        return cls.query

    @classmethod
    def para_atividades(cls, atividades_ids: List[int]):
        """Filtra regimes compatíveis com as atividades"""
        return cls.query.join(AtividadeRegimePermitido).filter(
            AtividadeRegimePermitido.tipo_atividade_id.in_(atividades_ids),
            AtividadeRegimePermitido.ativo == True
        ).distinct()

    def pode_ser_removido(self) -> bool:
        """Verifica se o regime pode ser removido"""
        return not bool(self.propostas)


class AtividadeRegimePermitido(db.Model, ActiveMixin):
    """Modelo para relacionamento atividade x regime"""
    __tablename__ = "atividade_regime_permitidos"

    id = db.Column(db.Integer, primary_key=True)
    tipo_atividade_id = db.Column(
        db.Integer, 
        db.ForeignKey('tipos_atividade.id', ondelete='CASCADE'), 
        nullable=False
    )
    regime_tributario_id = db.Column(
        db.Integer, 
        db.ForeignKey('regimes_tributarios.id', ondelete='CASCADE'), 
        nullable=False
    )

    __table_args__ = (
        UniqueConstraint('tipo_atividade_id', 'regime_tributario_id'),
    )

    def __repr__(self):
        return f'<AtividadeRegime {self.tipo_atividade_id}-{self.regime_tributario_id}>'

    def to_json(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "tipo_atividade_id": self.tipo_atividade_id,
            "regime_tributario_id": self.regime_tributario_id,
            "ativo": self.ativo,
            "tipo_atividade_nome": self.tipo_atividade.nome if self.tipo_atividade else None,
            "regime_tributario_nome": self.regime_tributario.nome if self.regime_tributario else None
        }


class FaixaFaturamento(db.Model, ActiveMixin):
    """Modelo para faixas de faturamento"""
    __tablename__ = "faixas_faturamento"

    id = db.Column(db.Integer, primary_key=True)
    regime_tributario_id = db.Column(
        db.Integer, 
        db.ForeignKey('regimes_tributarios.id', ondelete='CASCADE'), 
        nullable=False
    )
    descricao = db.Column(db.String(100), nullable=False)
    valor_minimo = db.Column(db.Numeric(15, 2))
    valor_maximo = db.Column(db.Numeric(15, 2))
    codigo_legislacao = db.Column(db.String(20), index=True)

    # Relacionamentos
    propostas = db.relationship('Proposta', backref='faixa_faturamento', lazy=True)

    def __repr__(self):
        return f'<FaixaFaturamento {self.descricao}>'

    def to_json(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "regime_tributario_id": self.regime_tributario_id,
            "descricao": self.descricao,
            "valor_minimo": float(self.valor_minimo) if self.valor_minimo else None,
            "valor_maximo": float(self.valor_maximo) if self.valor_maximo else None,
            "codigo_legislacao": self.codigo_legislacao,
            "ativo": self.ativo,
            "regime_nome": self.regime_tributario.nome if self.regime_tributario else None
        }

    @hybrid_property
    def faixa_formatada(self):
        """Retorna a faixa formatada para exibição"""
        if self.valor_minimo is not None and self.valor_maximo is not None:
            return f"R$ {self.valor_minimo:,.2f} a R$ {self.valor_maximo:,.2f}"
        elif self.valor_minimo is not None:
            return f"A partir de R$ {self.valor_minimo:,.2f}"
        elif self.valor_maximo is not None:
            return f"Até R$ {self.valor_maximo:,.2f}"
        return "Sem limite definido"

    def valor_esta_na_faixa(self, valor: Decimal) -> bool:
        """Verifica se um valor está dentro da faixa"""
        if self.valor_minimo is not None and valor < self.valor_minimo:
            return False
        if self.valor_maximo is not None and valor > self.valor_maximo:
            return False
        return True


class ServicoBase(db.Model, ActiveMixin, TimestampMixin):
    """Modelo para serviços base"""
    __tablename__ = "servicos_base"

    CATEGORIAS = ['CONTABIL', 'FISCAL', 'PESSOAL', 'SOCIETARIO']
    TIPOS_COBRANCA = ['FIXO', 'UNITARIO', 'PERCENTUAL']

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False, index=True)
    categoria = db.Column(db.String(20), nullable=False, index=True)
    tipo_cobranca = db.Column(db.String(20), nullable=False)
    valor_base = db.Column(db.Numeric(10, 2), nullable=False)
    descricao = db.Column(db.Text)
    requer_regime_empresarial = db.Column(db.Boolean, default=False, nullable=False)

    __table_args__ = (
        CheckConstraint(categoria.in_(CATEGORIAS), name='check_categoria'),
        CheckConstraint(tipo_cobranca.in_(TIPOS_COBRANCA), name='check_tipo_cobranca'),
        CheckConstraint(valor_base >= 0, name='check_valor_base_positivo'),
    )

    # Relacionamentos
    regras_preco = db.relationship(
        'RegraPreco', 
        backref='servico_base', 
        lazy=True,
        cascade='all, delete-orphan'
    )
    itens_proposta = db.relationship('PropostaItem', backref='servico_base', lazy=True)

    def __repr__(self):
        return f'<ServicoBase {self.nome}>'

    def to_json(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "nome": self.nome,
            "categoria": self.categoria,
            "tipo_cobranca": self.tipo_cobranca,
            "valor_base": float(self.valor_base),
            "descricao": self.descricao,
            "requer_regime_empresarial": self.requer_regime_empresarial,
            "ativo": self.ativo,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

    def calcular_preco(self, quantidade: int = 1, **kwargs) -> Decimal:
        """Calcula o preço do serviço baseado no tipo de cobrança"""
        if self.tipo_cobranca == 'FIXO':
            return self.valor_base
        elif self.tipo_cobranca == 'UNITARIO':
            return self.valor_base * quantidade
        elif self.tipo_cobranca == 'PERCENTUAL':
            valor_base = kwargs.get('valor_base', 0)
            return (self.valor_base / 100) * Decimal(str(valor_base))
        return Decimal('0')


class RegraPreco(db.Model, ActiveMixin):
    """Modelo para regras de preço específicas"""
    __tablename__ = "regras_preco"

    id = db.Column(db.Integer, primary_key=True)
    servico_base_id = db.Column(
        db.Integer, 
        db.ForeignKey('servicos_base.id', ondelete='CASCADE'), 
        nullable=False
    )
    regime_tributario_id = db.Column(
        db.Integer, 
        db.ForeignKey('regimes_tributarios.id', ondelete='CASCADE')
    )
    tipo_atividade_id = db.Column(
        db.Integer, 
        db.ForeignKey('tipos_atividade.id', ondelete='CASCADE')
    )
    faixa_faturamento_id = db.Column(
        db.Integer, 
        db.ForeignKey('faixas_faturamento.id', ondelete='CASCADE')
    )
    valor_customizado = db.Column(db.Numeric(10, 2))
    multiplicador = db.Column(db.Numeric(5, 2), default=1.0)

    __table_args__ = (
        CheckConstraint(multiplicador > 0, name='check_multiplicador_positivo'),
        CheckConstraint(
            db.or_(valor_customizado.isnot(None), multiplicador.isnot(None)),
            name='check_valor_ou_multiplicador'
        ),
    )

    # Relacionamentos
    regime_tributario_regra = db.relationship('RegimeTributario')
    tipo_atividade_regra = db.relationship('TipoAtividade')
    faixa_faturamento_regra = db.relationship('FaixaFaturamento')

    def __repr__(self):
        return f'<RegraPreco {self.servico_base_id}>'

    def to_json(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "servico_base_id": self.servico_base_id,
            "regime_tributario_id": self.regime_tributario_id,
            "tipo_atividade_id": self.tipo_atividade_id,
            "faixa_faturamento_id": self.faixa_faturamento_id,
            "valor_customizado": float(self.valor_customizado) if self.valor_customizado else None,
            "multiplicador": float(self.multiplicador) if self.multiplicador else 1.0,
            "ativo": self.ativo
        }


class Proposta(db.Model, TimestampMixin):
    """Modelo principal para propostas"""
    __tablename__ = "propostas"

    STATUS_CHOICES = ['RASCUNHO', 'ENVIADA', 'APROVADA', 'REJEITADA', 'CANCELADA']

    id = db.Column(db.Integer, primary_key=True)
    numero_proposta = db.Column(db.String(20), unique=True, nullable=False, index=True)
    cliente_id = db.Column(
        db.Integer, 
        db.ForeignKey('clientes.id', ondelete='RESTRICT'), 
        nullable=False, 
        index=True
    )
    funcionario_id = db.Column(
        db.Integer, 
        db.ForeignKey('funcionarios.id', ondelete='RESTRICT'), 
        nullable=False,
        index=True
    )
    
    # Dados do questionário
    regime_tributario_id = db.Column(
        db.Integer, 
        db.ForeignKey('regimes_tributarios.id', ondelete='RESTRICT'),
        index=True
    )
    faixa_faturamento_id = db.Column(
        db.Integer, 
        db.ForeignKey('faixas_faturamento.id', ondelete='RESTRICT')
    )
    
    # Definições fiscais
    quantidade_notas_fiscais = db.Column(db.Integer, default=0, nullable=False)
    emite_notas_fiscais = db.Column(db.Boolean, default=False, nullable=False)
    
    # Departamento pessoal
    quantidade_funcionarios = db.Column(db.Integer, default=0, nullable=False)
    quantidade_socios_prolabore = db.Column(db.Integer, default=0, nullable=False)
    
    # Área contábil
    precisa_balancete = db.Column(db.Boolean, default=False, nullable=False)
    
    # Área societária
    possui_orgao_classe = db.Column(db.Boolean, default=False, nullable=False)
    
    # Valores
    subtotal = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    percentual_desconto = db.Column(db.Numeric(5, 2), default=0)
    valor_desconto = db.Column(db.Numeric(10, 2), default=0)
    valor_total = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    
    # Controle
    status = db.Column(db.String(20), default='RASCUNHO', nullable=False, index=True)
    etapa_atual = db.Column(db.Integer, default=1, nullable=False)
    validade_dias = db.Column(db.Integer, default=30, nullable=False)
    observacoes = db.Column(db.Text)

    __table_args__ = (
        CheckConstraint(status.in_(STATUS_CHOICES), name='check_status'),
        CheckConstraint(etapa_atual.between(1, 7), name='check_etapa_atual'),
        CheckConstraint(validade_dias > 0, name='check_validade_positiva'),
        CheckConstraint(quantidade_notas_fiscais >= 0, name='check_notas_fiscais_positivo'),
        CheckConstraint(quantidade_funcionarios >= 0, name='check_funcionarios_positivo'),
        CheckConstraint(quantidade_socios_prolabore >= 0, name='check_socios_positivo'),
        CheckConstraint(subtotal >= 0, name='check_subtotal_positivo'),
        CheckConstraint(valor_total >= 0, name='check_valor_total_positivo'),
        CheckConstraint(percentual_desconto.between(0, 100), name='check_desconto_valido'),
    )

    # Relacionamentos
    atividades = db.relationship(
        'PropostaAtividade', 
        backref='proposta', 
        lazy=True, 
        cascade='all, delete-orphan'
    )
    itens = db.relationship(
        'PropostaItem', 
        backref='proposta', 
        lazy=True, 
        cascade='all, delete-orphan'
    )
    historicos = db.relationship(
        'PropostaHistorico', 
        backref='proposta', 
        lazy=True, 
        cascade='all, delete-orphan'
    )
    versoes = db.relationship(
        'PropostaVersao', 
        backref='proposta_original', 
        lazy=True,
        cascade='all, delete-orphan'
    )

    def __repr__(self):
        return f'<Proposta {self.numero_proposta}>'

    @hybrid_property
    def data_vencimento(self):
        """Calcula a data de vencimento da proposta"""
        from datetime import timedelta
        return self.created_at + timedelta(days=self.validade_dias)

    @hybrid_property
    def esta_vencida(self):
        """Verifica se a proposta está vencida"""
        return datetime.utcnow() > self.data_vencimento

    @hybrid_property
    def pode_ser_editada(self):
        """Verifica se a proposta pode ser editada"""
        return self.status in ['RASCUNHO']

    def to_json(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "numero_proposta": self.numero_proposta,
            "cliente_id": self.cliente_id,
            "funcionario_id": self.funcionario_id,
            "regime_tributario_id": self.regime_tributario_id,
            "faixa_faturamento_id": self.faixa_faturamento_id,
            "quantidade_notas_fiscais": self.quantidade_notas_fiscais,
            "emite_notas_fiscais": self.emite_notas_fiscais,
            "quantidade_funcionarios": self.quantidade_funcionarios,
            "quantidade_socios_prolabore": self.quantidade_socios_prolabore,
            "precisa_balancete": self.precisa_balancete,
            "possui_orgao_classe": self.possui_orgao_classe,
            "subtotal": float(self.subtotal),
            "percentual_desconto": float(self.percentual_desconto),
            "valor_desconto": float(self.valor_desconto),
            "valor_total": float(self.valor_total),
            "status": self.status,
            "etapa_atual": self.etapa_atual,
            "validade_dias": self.validade_dias,
            "observacoes": self.observacoes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "data_vencimento": self.data_vencimento.isoformat() if self.data_vencimento else None,
            "esta_vencida": self.esta_vencida,
            "pode_ser_editada": self.pode_ser_editada,
            "atividades": [a.to_json() for a in self.atividades],
            "itens": [i.to_json() for i in self.itens],
            # Dados relacionados
            "cliente_nome": self.cliente.nome_completo if self.cliente else None,
            "funcionario_nome": self.funcionario.nome if self.funcionario else None,
            "regime_nome": self.regime_tributario.nome if self.regime_tributario else None
        }

    def get_atividades_nomes(self) -> List[str]:
        """Retorna lista com nomes das atividades selecionadas"""
        return [
            atividade.tipo_atividade.nome 
            for atividade in self.atividades 
            if atividade.tipo_atividade
        ]

    def requer_etapas_avancadas(self) -> bool:
        """Verifica se o regime tributário requer as etapas avançadas"""
        return (
            self.regime_tributario.requer_definicoes_fiscais 
            if self.regime_tributario else False
        )

    def alterar_status(self, novo_status: str, funcionario_id: int, observacao: str = None):
        """Altera o status da proposta com histórico"""
        if novo_status not in self.STATUS_CHOICES:
            raise ValueError(f"Status inválido: {novo_status}")
        
        status_anterior = self.status
        self.status = novo_status
        self.updated_at = datetime.utcnow()
        
        # Adicionar ao histórico
        PropostaService.adicionar_historico(
            self, 
            funcionario_id, 
            f'STATUS_ALTERADO',
            f'Status alterado de {status_anterior} para {novo_status}' + 
            (f' - {observacao}' if observacao else '')
        )


# Continuação dos modelos auxiliares...

class PropostaAtividade(db.Model, TimestampMixin):
    """Modelo para atividades da proposta"""
    __tablename__ = "proposta_atividades"

    id = db.Column(db.Integer, primary_key=True)
    proposta_id = db.Column(
        db.Integer, 
        db.ForeignKey('propostas.id', ondelete='CASCADE'), 
        nullable=False
    )
    tipo_atividade_id = db.Column(
        db.Integer, 
        db.ForeignKey('tipos_atividade.id', ondelete='RESTRICT'), 
        nullable=False
    )

    __table_args__ = (
        UniqueConstraint('proposta_id', 'tipo_atividade_id'),
    )

    # Relacionamentos
    tipo_atividade = db.relationship('TipoAtividade')

    def __repr__(self):
        return f'<PropostaAtividade {self.proposta_id}-{self.tipo_atividade_id}>'

    def to_json(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "proposta_id": self.proposta_id,
            "tipo_atividade_id": self.tipo_atividade_id,
            "tipo_atividade_nome": self.tipo_atividade.nome if self.tipo_atividade else None,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class PropostaItem(db.Model, TimestampMixin):
    """Modelo para itens da proposta"""
    __tablename__ = "proposta_itens"

    ORIGENS = ['MANUAL', 'AUTO']

    id = db.Column(db.Integer, primary_key=True)
    proposta_id = db.Column(
        db.Integer, 
        db.ForeignKey('propostas.id', ondelete='CASCADE'), 
        nullable=False
    )
    servico_base_id = db.Column(
        db.Integer, 
        db.ForeignKey('servicos_base.id', ondelete='RESTRICT'),
        nullable=False
    )
    descricao = db.Column(db.String(200), nullable=False)
    quantidade = db.Column(db.Integer, default=1, nullable=False)
    valor_unitario = db.Column(db.Numeric(10, 2), nullable=False)
    valor_total = db.Column(db.Numeric(10, 2), nullable=False)
    origem = db.Column(db.String(20), default='MANUAL', nullable=False)

    __table_args__ = (
        CheckConstraint(origem.in_(ORIGENS), name='check_origem'),
        CheckConstraint(quantidade > 0, name='check_quantidade_positiva'),
        CheckConstraint(valor_unitario >= 0, name='check_valor_unitario_positivo'),
        CheckConstraint(valor_total >= 0, name='check_valor_total_positivo'),
    )

    def __repr__(self):
        return f'<PropostaItem {self.descricao}>'

    def to_json(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "proposta_id": self.proposta_id,
            "servico_base_id": self.servico_base_id,
            "descricao": self.descricao,
            "quantidade": self.quantidade,
            "valor_unitario": float(self.valor_unitario),
            "valor_total": float(self.valor_total),
            "origem": self.origem,
            "servico_categoria": self.servico_base.categoria if self.servico_base else None,
            "servico_nome": self.servico_base.nome if self.servico_base else None,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

    def recalcular_valor_total(self):
        """Recalcula o valor total baseado na quantidade e valor unitário"""
        self.valor_total = self.valor_unitario * self.quantidade


class PropostaHistorico(db.Model, TimestampMixin):
    """Modelo para histórico da proposta"""
    __tablename__ = "proposta_historico"

    id = db.Column(db.Integer, primary_key=True)
    proposta_id = db.Column(
        db.Integer, 
        db.ForeignKey('propostas.id', ondelete='CASCADE'), 
        nullable=False
    )
    funcionario_id = db.Column(
        db.Integer, 
        db.ForeignKey('funcionarios.id', ondelete='RESTRICT'), 
        nullable=False
    )
    etapa = db.Column(db.Integer)
    acao = db.Column(db.String(50), nullable=False, index=True)
    descricao = db.Column(db.Text)
    dados_anteriores = db.Column(JSON)
    dados_novos = db.Column(JSON)

    def __repr__(self):
        return f'<PropostaHistorico {self.acao}>'

    def to_json(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "proposta_id": self.proposta_id,
            "funcionario_id": self.funcionario_id,
            "funcionario_nome": self.funcionario.nome if self.funcionario else None,
            "etapa": self.etapa,
            "acao": self.acao,
            "descricao": self.descricao,
            "dados_anteriores": self.dados_anteriores,
            "dados_novos": self.dados_novos,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class PropostaVersao(db.Model, TimestampMixin):
    """Modelo para versões da proposta com descontos"""
    __tablename__ = "proposta_versoes"

    id = db.Column(db.Integer, primary_key=True)
    proposta_original_id = db.Column(
        db.Integer, 
        db.ForeignKey('propostas.id', ondelete='CASCADE'), 
        nullable=False
    )
    numero_versao = db.Column(db.Integer, nullable=False)
    percentual_desconto = db.Column(db.Numeric(5, 2), nullable=False)
    valor_total = db.Column(db.Numeric(10, 2), nullable=False)
    motivo_desconto = db.Column(db.Text)
    funcionario_id = db.Column(
        db.Integer, 
        db.ForeignKey('funcionarios.id', ondelete='RESTRICT'), 
        nullable=False
    )

    __table_args__ = (
        CheckConstraint(percentual_desconto.between(0, 100), name='check_desconto_versao'),
        CheckConstraint(valor_total >= 0, name='check_valor_total_versao'),
        UniqueConstraint('proposta_original_id', 'numero_versao'),
    )

    # Relacionamentos
    funcionario_versao = db.relationship('Funcionario')

    def __repr__(self):
        return f'<PropostaVersao {self.proposta_original_id}-v{self.numero_versao}>'

    def to_json(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "proposta_original_id": self.proposta_original_id,
            "numero_versao": self.numero_versao,
            "percentual_desconto": float(self.percentual_desconto),
            "valor_total": float(self.valor_total),
            "motivo_desconto": self.motivo_desconto,
            "funcionario_id": self.funcionario_id,
            "funcionario_nome": self.funcionario_versao.nome if self.funcionario_versao else None,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class ConfiguracaoSistema(db.Model, TimestampMixin):
    """Modelo para configurações do sistema"""
    __tablename__ = "configuracoes_sistema"

    TIPOS = ['STRING', 'NUMBER', 'BOOLEAN', 'JSON']

    id = db.Column(db.Integer, primary_key=True)
    chave = db.Column(db.String(100), unique=True, nullable=False, index=True)
    valor = db.Column(db.Text, nullable=False)
    descricao = db.Column(db.Text)
    tipo = db.Column(db.String(20), default='STRING', nullable=False)

    __table_args__ = (
        CheckConstraint(tipo.in_(TIPOS), name='check_tipo_configuracao'),
    )

    def __repr__(self):
        return f'<ConfiguracaoSistema {self.chave}>'

    def to_json(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "chave": self.chave,
            "valor": self.valor,
            "valor_tipado": self.get_valor_tipado(),
            "descricao": self.descricao,
            "tipo": self.tipo,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

    def get_valor_tipado(self) -> Any:
        """Retorna o valor convertido para o tipo correto"""
        try:
            if self.tipo == 'NUMBER':
                return int(self.valor) if '.' not in self.valor else float(self.valor)
            elif self.tipo == 'BOOLEAN':
                return self.valor.lower() in ['true', '1', 'yes', 'sim']
            elif self.tipo == 'JSON':
                return json.loads(self.valor)
            else:
                return self.valor
        except (ValueError, json.JSONDecodeError):
            # Retorna valor padrão em caso de erro
            if self.tipo == 'NUMBER':
                return 0
            elif self.tipo == 'BOOLEAN':
                return False
            elif self.tipo == 'JSON':
                return {}
            return self.valor

    @classmethod
    def get_configuracao(cls, chave: str, padrao: Any = None) -> Any:
        """Obtém uma configuração específica"""
        config = cls.query.filter_by(chave=chave).first()
        return config.get_valor_tipado() if config else padrao

    @classmethod
    def set_configuracao(cls, chave: str, valor: Any, descricao: str = None, tipo: str = 'STRING'):
        """Define uma configuração"""
        config = cls.query.filter_by(chave=chave).first()
        
        if config:
            config.valor = str(valor)
            if descricao:
                config.descricao = descricao
            config.tipo = tipo
            config.updated_at = datetime.utcnow()
        else:
            config = cls(
                chave=chave,
                valor=str(valor),
                descricao=descricao,
                tipo=tipo
            )
            db.session.add(config)
        
        db.session.commit()
        return config


# =====================================================
# SERVIÇO DE PROPOSTAS
# =====================================================

class PropostaService:
    """Classe com métodos estáticos para lógica de negócio das propostas"""
    
    @staticmethod
    def gerar_numero_proposta() -> str:
        """Gera o próximo número de proposta no formato AAAA0001"""
        ano_atual = datetime.now().year
        
        # Busca o último número do ano
        ultima_proposta = db.session.query(Proposta)\
            .filter(Proposta.numero_proposta.like(f'{ano_atual}%'))\
            .order_by(Proposta.numero_proposta.desc())\
            .first()
        
        if ultima_proposta:
            try:
                ultimo_numero = int(ultima_proposta.numero_proposta[-4:])
                proximo_numero = ultimo_numero + 1
            except ValueError:
                proximo_numero = 1
        else:
            proximo_numero = 1
            
        return f'{ano_atual}{proximo_numero:04d}'
    
    @staticmethod
    def validar_regime_para_atividades(proposta: Proposta) -> bool:
        """Valida se o regime tributário é compatível com as atividades selecionadas"""
        if not proposta.regime_tributario_id:
            return True
            
        atividades_ids = [a.tipo_atividade_id for a in proposta.atividades]
        if not atividades_ids:
            return True
        
        # Verifica se existe pelo menos uma combinação válida
        combinacao_valida = db.session.query(AtividadeRegimePermitido)\
            .filter(
                AtividadeRegimePermitido.tipo_atividade_id.in_(atividades_ids),
                AtividadeRegimePermitido.regime_tributario_id == proposta.regime_tributario_id,
                AtividadeRegimePermitido.ativo == True
            ).first()
            
        return combinacao_valida is not None
    
    @staticmethod
    def get_regimes_disponiveis_para_atividades(
        atividades_ids: List[int], 
        tipo_pessoa: str = 'J'
    ) -> List[RegimeTributario]:
        """Retorna regimes tributários disponíveis para as atividades selecionadas"""
        query = db.session.query(RegimeTributario)\
            .join(AtividadeRegimePermitido)\
            .filter(
                AtividadeRegimePermitido.tipo_atividade_id.in_(atividades_ids),
                AtividadeRegimePermitido.ativo == True,
                RegimeTributario.ativo == True
            )
        
        if tipo_pessoa == 'F':
            query = query.filter(RegimeTributario.aplicavel_pf == True)
        elif tipo_pessoa == 'J':
            query = query.filter(RegimeTributario.aplicavel_pj == True)
            
        return query.distinct().all()
    
    @staticmethod
    def calcular_servicos_automaticos(proposta: Proposta):
        """Calcula e adiciona serviços automaticamente baseado nas configurações"""
        if not proposta.requer_etapas_avancadas():
            return
        
        # Remove itens automáticos existentes
        PropostaItem.query.filter_by(
            proposta_id=proposta.id, 
            origem='AUTO'
        ).delete()
        
        servicos_adicionados = []
        
        # Contabilidade Mensal (sempre inclui para regimes empresariais)
        servico_contabil = ServicoBase.query.filter_by(
            nome='Contabilidade Mensal', 
            ativo=True
        ).first()
        
        if servico_contabil:
            item = PropostaItem(
                proposta_id=proposta.id,
                servico_base_id=servico_contabil.id,
                descricao='Contabilidade Mensal',
                quantidade=1,
                valor_unitario=servico_contabil.valor_base,
                valor_total=servico_contabil.valor_base,
                origem='AUTO'
            )
            db.session.add(item)
            servicos_adicionados.append('Contabilidade Mensal')
        
        # Funcionários DP
        if proposta.quantidade_funcionarios > 0:
            servico_func = ServicoBase.query.filter_by(
                nome='Funcionário DP', 
                ativo=True
            ).first()
            
            if servico_func:
                valor_total = servico_func.valor_base * proposta.quantidade_funcionarios
                item = PropostaItem(
                    proposta_id=proposta.id,
                    servico_base_id=servico_func.id,
                    descricao=f'Departamento Pessoal - {proposta.quantidade_funcionarios} funcionário(s)',
                    quantidade=proposta.quantidade_funcionarios,
                    valor_unitario=servico_func.valor_base,
                    valor_total=valor_total,
                    origem='AUTO'
                )
                db.session.add(item)
                servicos_adicionados.append(f'Funcionário DP ({proposta.quantidade_funcionarios}x)')
        
        # Pró-labore
        if proposta.quantidade_socios_prolabore > 0:
            servico_prolabore = ServicoBase.query.filter_by(
                nome='Pró-labore', 
                ativo=True
            ).first()
            
            if servico_prolabore:
                valor_total = servico_prolabore.valor_base * proposta.quantidade_socios_prolabore
                item = PropostaItem(
                    proposta_id=proposta.id,
                    servico_base_id=servico_prolabore.id,
                    descricao=f'Pró-labore - {proposta.quantidade_socios_prolabore} sócio(s)',
                    quantidade=proposta.quantidade_socios_prolabore,
                    valor_unitario=servico_prolabore.valor_base,
                    valor_total=valor_total,
                    origem='AUTO'
                )
                db.session.add(item)
                servicos_adicionados.append(f'Pró-labore ({proposta.quantidade_socios_prolabore}x)')
        
        # Balancete Mensal
        if proposta.precisa_balancete:
            servico_balancete = ServicoBase.query.filter_by(
                nome='Balancete Mensal', 
                ativo=True
            ).first()
            
            if servico_balancete:
                item = PropostaItem(
                    proposta_id=proposta.id,
                    servico_base_id=servico_balancete.id,
                    descricao='Balancete Mensal',
                    quantidade=1,
                    valor_unitario=servico_balancete.valor_base,
                    valor_total=servico_balancete.valor_base,
                    origem='AUTO'
                )
                db.session.add(item)
                servicos_adicionados.append('Balancete Mensal')
        
        # Notas Fiscais
        if proposta.emite_notas_fiscais and proposta.quantidade_notas_fiscais > 0:
            servico_nf = ServicoBase.query.filter_by(
                nome='Nota Fiscal', 
                ativo=True
            ).first()
            
            if servico_nf:
                valor_total = servico_nf.valor_base * proposta.quantidade_notas_fiscais
                item = PropostaItem(
                    proposta_id=proposta.id,
                    servico_base_id=servico_nf.id,
                    descricao=f'Emissão de Notas Fiscais - {proposta.quantidade_notas_fiscais}/mês',
                    quantidade=proposta.quantidade_notas_fiscais,
                    valor_unitario=servico_nf.valor_base,
                    valor_total=valor_total,
                    origem='AUTO'
                )
                db.session.add(item)
                servicos_adicionados.append(f'Nota Fiscal ({proposta.quantidade_notas_fiscais}x)')
        
        # Órgão de Classe
        if proposta.possui_orgao_classe:
            servico_orgao = ServicoBase.query.filter_by(
                nome='Órgão de Classe', 
                ativo=True
            ).first()
            
            if servico_orgao:
                item = PropostaItem(
                    proposta_id=proposta.id,
                    servico_base_id=servico_orgao.id,
                    descricao='Registro em Órgão de Classe',
                    quantidade=1,
                    valor_unitario=servico_orgao.valor_base,
                    valor_total=servico_orgao.valor_base,
                    origem='AUTO'
                )
                db.session.add(item)
                servicos_adicionados.append('Órgão de Classe')
        
        # Atualiza totais
        PropostaService.atualizar_totais(proposta)
        
        # Adicionar histórico
        PropostaService.adicionar_historico(
            proposta,
            proposta.funcionario_id,
            'SERVICOS_CALCULADOS',
            f'Serviços calculados automaticamente: {", ".join(servicos_adicionados)}'
        )
    
    @staticmethod
    def atualizar_totais(proposta: Proposta):
        """Atualiza subtotal, desconto e total da proposta"""
        # Calcula subtotal
        subtotal = db.session.query(
            db.func.coalesce(db.func.sum(PropostaItem.valor_total), 0)
        ).filter_by(proposta_id=proposta.id).scalar() or Decimal('0')
        
        # Calcula desconto
        desconto = (
            subtotal * (proposta.percentual_desconto / 100) 
            if proposta.percentual_desconto else Decimal('0')
        )
        
        # Atualiza proposta
        proposta.subtotal = subtotal
        proposta.valor_desconto = desconto
        proposta.valor_total = subtotal - desconto
        
        db.session.commit()
    
    @staticmethod
    def adicionar_historico(
        proposta: Proposta, 
        funcionario_id: int, 
        acao: str, 
        descricao: str = None, 
        etapa: int = None, 
        dados_anteriores: Dict = None, 
        dados_novos: Dict = None
    ):
        """Adiciona entrada no histórico da proposta"""
        historico = PropostaHistorico(
            proposta_id=proposta.id,
            funcionario_id=funcionario_id,
            etapa=etapa,
            acao=acao,
            descricao=descricao,
            dados_anteriores=dados_anteriores,
            dados_novos=dados_novos
        )
        db.session.add(historico)
        db.session.commit()
    
    @staticmethod
    def criar_versao_com_desconto(
        proposta: Proposta, 
        percentual_desconto: float, 
        motivo_desconto: str, 
        funcionario_id: int
    ) -> PropostaVersao:
        """Cria nova versão da proposta com desconto específico"""
        # Valida desconto
        if not (0 <= percentual_desconto <= 100):
            raise ValueError("Percentual de desconto deve estar entre 0 e 100")
        
        # Calcula novo total
        novo_desconto = proposta.subtotal * (Decimal(str(percentual_desconto)) / 100)
        novo_total = proposta.subtotal - novo_desconto
        
        # Busca próximo número de versão
        ultima_versao = PropostaVersao.query.filter_by(
            proposta_original_id=proposta.id
        ).order_by(PropostaVersao.numero_versao.desc()).first()
        
        proximo_numero = (ultima_versao.numero_versao + 1) if ultima_versao else 1
        
        # Cria nova versão
        versao = PropostaVersao(
            proposta_original_id=proposta.id,
            numero_versao=proximo_numero,
            percentual_desconto=Decimal(str(percentual_desconto)),
            valor_total=novo_total,
            motivo_desconto=motivo_desconto,
            funcionario_id=funcionario_id
        )
        
        db.session.add(versao)
        
        # Adicionar histórico
        PropostaService.adicionar_historico(
            proposta,
            funcionario_id,
            'VERSAO_CRIADA',
            f'Versão {proximo_numero} criada com {percentual_desconto}% de desconto'
        )
        
        db.session.commit()
        return versao


# =====================================================
# EVENT LISTENERS
# =====================================================

@event.listens_for(PropostaItem, 'before_insert')
@event.listens_for(PropostaItem, 'before_update')
def validate_proposta_item(mapper, connection, target):
    """Valida item da proposta antes de salvar"""
    # Recalcula valor total
    target.recalcular_valor_total()

@event.listens_for(Cliente, 'before_insert')
@event.listens_for(Cliente, 'before_update')
def validate_cliente(mapper, connection, target):
    """Valida cliente antes de salvar"""
    # Normaliza dados
    if target.email:
        target.email = target.email.strip().lower()
    
    # Remove caracteres especiais de documentos
    if target.cpf:
        target.cpf = re.sub(r'[^0-9]', '', target.cpf)
    if target.cnpj:
        target.cnpj = re.sub(r'[^0-9]', '', target.cnpj)

@event.listens_for(Funcionario, 'before_insert')
@event.listens_for(Funcionario, 'before_update')
def validate_funcionario(mapper, connection, target):
    """Valida funcionário antes de salvar"""
    if target.email:
        target.email = target.email.strip().lower()

# =====================================================
# FUNÇÕES DE INICIALIZAÇÃO DOS DADOS
# =====================================================

def inicializar_dados_basicos():
    """Inicializa dados básicos do sistema"""
    
    # Tipos de Atividade
    tipos_atividade = [
        {'nome': 'Serviços', 'codigo': 'SERV', 'descricao': 'Empresas prestadoras de serviços', 'aplicavel_pf': False, 'aplicavel_pj': True},
        {'nome': 'Comércio', 'codigo': 'COM', 'descricao': 'Empresas comerciais', 'aplicavel_pf': False, 'aplicavel_pj': True},
        {'nome': 'Indústria', 'codigo': 'IND', 'descricao': 'Empresas industriais', 'aplicavel_pf': False, 'aplicavel_pj': True},
        {'nome': 'Pessoa Física', 'codigo': 'PF', 'descricao': 'Pessoa física com atividades', 'aplicavel_pf': True, 'aplicavel_pj': False},
    ]
    
    for tipo_data in tipos_atividade:
        if not TipoAtividade.query.filter_by(codigo=tipo_data['codigo']).first():
            tipo = TipoAtividade(**tipo_data)
            db.session.add(tipo)
    
    # Regimes Tributários
    regimes = [
        {'nome': 'MEI', 'codigo': 'MEI', 'descricao': 'Microempreendedor Individual', 'aplicavel_pf': False, 'aplicavel_pj': True, 'requer_definicoes_fiscais': True},
        {'nome': 'Simples Nacional', 'codigo': 'SN', 'descricao': 'Regime Simplificado de Tributação', 'aplicavel_pf': False, 'aplicavel_pj': True, 'requer_definicoes_fiscais': True},
        {'nome': 'Lucro Presumido', 'codigo': 'LP', 'descricao': 'Tributação com base em presunção de lucro', 'aplicavel_pf': False, 'aplicavel_pj': True, 'requer_definicoes_fiscais': True},
        {'nome': 'Lucro Real', 'codigo': 'LR', 'descricao': 'Tributação com base no lucro real', 'aplicavel_pf': False, 'aplicavel_pj': True, 'requer_definicoes_fiscais': True},
        {'nome': 'Produtor Rural', 'codigo': 'PR', 'descricao': 'Regime específico para produtores rurais', 'aplicavel_pf': True, 'aplicavel_pj': False, 'requer_definicoes_fiscais': False},
        {'nome': 'Autônomo', 'codigo': 'AUT', 'descricao': 'Pessoa física autônoma', 'aplicavel_pf': True, 'aplicavel_pj': False, 'requer_definicoes_fiscais': False},
        {'nome': 'Empregador Doméstico', 'codigo': 'ED', 'descricao': 'Empregador doméstico', 'aplicavel_pf': True, 'aplicavel_pj': False, 'requer_definicoes_fiscais': False},
    ]
    
    for regime_data in regimes:
        if not RegimeTributario.query.filter_by(codigo=regime_data['codigo']).first():
            regime = RegimeTributario(**regime_data)
            db.session.add(regime)
    
    db.session.commit()
    
    # Relacionamentos Atividade x Regime
    relacionamentos = [
        # Serviços, Comércio, Indústria podem ser: MEI, SN, LP, LR
        ('SERV', ['MEI', 'SN', 'LP', 'LR']),
        ('COM', ['MEI', 'SN', 'LP', 'LR']),
        ('IND', ['MEI', 'SN', 'LP', 'LR']),
        # Pessoa Física pode ser: PR, AUT, ED
        ('PF', ['PR', 'AUT', 'ED']),
    ]
    
    for atividade_codigo, regimes_codigos in relacionamentos:
        atividade = TipoAtividade.query.filter_by(codigo=atividade_codigo).first()
        for regime_codigo in regimes_codigos:
            regime = RegimeTributario.query.filter_by(codigo=regime_codigo).first()
            if atividade and regime:
                if not AtividadeRegimePermitido.query.filter_by(
                    tipo_atividade_id=atividade.id,
                    regime_tributario_id=regime.id
                ).first():
                    rel = AtividadeRegimePermitido(
                        tipo_atividade_id=atividade.id,
                        regime_tributario_id=regime.id
                    )
                    db.session.add(rel)
    
    # Faixas de Faturamento
    mei = RegimeTributario.query.filter_by(codigo='MEI').first()
    sn = RegimeTributario.query.filter_by(codigo='SN').first()
    lp = RegimeTributario.query.filter_by(codigo='LP').first()
    lr = RegimeTributario.query.filter_by(codigo='LR').first()
    
    faixas = [
        # MEI
        {'regime_id': mei.id if mei else None, 'descricao': 'Até R$ 81.000 anuais', 'valor_min': 0, 'valor_max': 81000.00, 'codigo': 'MEI_ANUAL'},
        # Simples Nacional
        {'regime_id': sn.id if sn else None, 'descricao': 'Até R$ 180.000', 'valor_min': 0, 'valor_max': 180000.00, 'codigo': 'SN_FAIXA1'},
        {'regime_id': sn.id if sn else None, 'descricao': 'R$ 180.001 a R$ 360.000', 'valor_min': 180000.01, 'valor_max': 360000.00, 'codigo': 'SN_FAIXA2'},
        {'regime_id': sn.id if sn else None, 'descricao': 'R$ 360.001 a R$ 720.000', 'valor_min': 360000.01, 'valor_max': 720000.00, 'codigo': 'SN_FAIXA3'},
        {'regime_id': sn.id if sn else None, 'descricao': 'R$ 720.001 a R$ 1.800.000', 'valor_min': 720000.01, 'valor_max': 1800000.00, 'codigo': 'SN_FAIXA4'},
        # Lucro Presumido
        {'regime_id': lp.id if lp else None, 'descricao': 'Até R$ 78.000.000 anuais', 'valor_min': 0, 'valor_max': 78000000.00, 'codigo': 'LP_ANUAL'},
        # Lucro Real
        {'regime_id': lr.id if lr else None, 'descricao': 'Acima de R$ 78.000.000 anuais', 'valor_min': 78000000.01, 'valor_max': None, 'codigo': 'LR_ANUAL'},
    ]
    
    for faixa_data in faixas:
        if faixa_data['regime_id'] and not FaixaFaturamento.query.filter_by(codigo_legislacao=faixa_data['codigo']).first():
            faixa = FaixaFaturamento(
                regime_tributario_id=faixa_data['regime_id'],
                descricao=faixa_data['descricao'],
                valor_minimo=Decimal(str(faixa_data['valor_min'])),
                valor_maximo=Decimal(str(faixa_data['valor_max'])) if faixa_data['valor_max'] else None,
                codigo_legislacao=faixa_data['codigo']
            )
            db.session.add(faixa)
    
    # Serviços Base
    servicos = [
        {'nome': 'Contabilidade Mensal', 'categoria': 'CONTABIL', 'tipo_cobranca': 'FIXO', 'valor_base': 500.00, 'descricao': 'Escrituração contábil mensal', 'requer_regime_empresarial': True},
        {'nome': 'Funcionário DP', 'categoria': 'PESSOAL', 'tipo_cobranca': 'UNITARIO', 'valor_base': 45.00, 'descricao': 'Departamento pessoal por funcionário', 'requer_regime_empresarial': True},
        {'nome': 'Pró-labore', 'categoria': 'PESSOAL', 'tipo_cobranca': 'UNITARIO', 'valor_base': 30.00, 'descricao': 'Processamento de pró-labore por sócio', 'requer_regime_empresarial': True},
        {'nome': 'Balancete Mensal', 'categoria': 'CONTABIL', 'tipo_cobranca': 'FIXO', 'valor_base': 50.00, 'descricao': 'Emissão de balancete mensal', 'requer_regime_empresarial': True},
        {'nome': 'Nota Fiscal', 'categoria': 'FISCAL', 'tipo_cobranca': 'UNITARIO', 'valor_base': 1.50, 'descricao': 'Emissão de nota fiscal', 'requer_regime_empresarial': True},
        {'nome': 'Órgão de Classe', 'categoria': 'SOCIETARIO', 'tipo_cobranca': 'FIXO', 'valor_base': 100.00, 'descricao': 'Registro em órgão de classe', 'requer_regime_empresarial': True},
        # Serviços para Pessoa Física
        {'nome': 'IRPF - Declaração', 'categoria': 'FISCAL', 'tipo_cobranca': 'FIXO', 'valor_base': 200.00, 'descricao': 'Declaração de Imposto de Renda Pessoa Física', 'requer_regime_empresarial': False},
        {'nome': 'Carnê-Leão', 'categoria': 'FISCAL', 'tipo_cobranca': 'FIXO', 'valor_base': 150.00, 'descricao': 'Recolhimento mensal Carnê-Leão', 'requer_regime_empresarial': False},
        {'nome': 'Livro Caixa', 'categoria': 'CONTABIL', 'tipo_cobranca': 'FIXO', 'valor_base': 300.00, 'descricao': 'Escrituração livro caixa para autônomos', 'requer_regime_empresarial': False},
    ]
    
    for servico_data in servicos:
        if not ServicoBase.query.filter_by(nome=servico_data['nome']).first():
            servico = ServicoBase(
                nome=servico_data['nome'],
                categoria=servico_data['categoria'],
                tipo_cobranca=servico_data['tipo_cobranca'],
                valor_base=Decimal(str(servico_data['valor_base'])),
                descricao=servico_data['descricao'],
                requer_regime_empresarial=servico_data['requer_regime_empresarial']
            )
            db.session.add(servico)
    
    # Configurações do Sistema
    configuracoes = [
        {'chave': 'empresa_nome', 'valor': 'Escritório Contábil XYZ', 'descricao': 'Nome da empresa', 'tipo': 'STRING'},
        {'chave': 'empresa_endereco', 'valor': 'Rua das Flores, 123 - Centro - São Paulo/SP', 'descricao': 'Endereço completo', 'tipo': 'STRING'},
        {'chave': 'empresa_telefone', 'valor': '(11) 3333-4444', 'descricao': 'Telefone principal', 'tipo': 'STRING'},
        {'chave': 'empresa_email', 'valor': 'contato@escritorio.com.br', 'descricao': 'Email principal', 'tipo': 'STRING'},
        {'chave': 'proposta_validade_padrao', 'valor': '30', 'descricao': 'Validade padrão das propostas em dias', 'tipo': 'NUMBER'},
        {'chave': 'desconto_maximo_permitido', 'valor': '25', 'descricao': 'Desconto máximo permitido em %', 'tipo': 'NUMBER'},
    ]
    
    for config_data in configuracoes:
        if not ConfiguracaoSistema.query.filter_by(chave=config_data['chave']).first():
            config = ConfiguracaoSistema(**config_data)
            db.session.add(config)
    
    db.session.commit()
    print("✅ Dados básicos inicializados com sucesso!")


# =====================================================
# EXEMPLO DE USO
# =====================================================

def exemplo_criar_proposta():
    """Exemplo de como criar uma proposta completa"""
    
    # 1. Criar cliente PJ
    cliente = Cliente(
        tipo_pessoa='J',
        razao_social='João da Silva Comércio LTDA',
        nome_fantasia='Loja do João',
        cnpj='12.345.678/0001-90',
        telefone='(11) 99999-8888',
        email='joao@lojadojoao.com.br'
    )
    db.session.add(cliente)
    db.session.flush()  # Para obter o ID
    
    # 2. Buscar funcionário
    funcionario = Funcionario.query.first()  # Assumindo que existe
    
    # 3. Criar proposta
    proposta = Proposta(
        numero_proposta=PropostaService.gerar_numero_proposta(),
        cliente_id=cliente.id,
        funcionario_id=funcionario.id,
        etapa_atual=1
    )
    db.session.add(proposta)
    db.session.flush()
    
    # 4. Adicionar atividades (Etapa 2)
    atividade_comercio = TipoAtividade.query.filter_by(codigo='COM').first()
    proposta_atividade = PropostaAtividade(
        proposta_id=proposta.id,
        tipo_atividade_id=atividade_comercio.id
    )
    db.session.add(proposta_atividade)
    proposta.etapa_atual = 2
    
    # 5. Selecionar regime tributário (Etapa 3)
    regime_sn = RegimeTributario.query.filter_by(codigo='SN').first()
    proposta.regime_tributario_id = regime_sn.id
    proposta.etapa_atual = 3
    
    # 6. Definições fiscais (Etapa 4)
    faixa = FaixaFaturamento.query.filter_by(codigo_legislacao='SN_FAIXA2').first()
    proposta.faixa_faturamento_id = faixa.id
    proposta.emite_notas_fiscais = True
    proposta.quantidade_notas_fiscais = 15
    proposta.etapa_atual = 4
    
    # 7. Departamento Pessoal (Etapa 5)
    proposta.quantidade_funcionarios = 2
    proposta.quantidade_socios_prolabore = 1
    proposta.etapa_atual = 5
    
    # 8. Área Contábil (Etapa 6)
    proposta.precisa_balancete = True
    proposta.etapa_atual = 6
    
    # 9. Área Societária (Etapa 7)
    proposta.possui_orgao_classe = False
    proposta.etapa_atual = 7
    proposta.status = 'ENVIADA'
    
    # 10. Calcular serviços automaticamente
    PropostaService.calcular_servicos_automaticos(proposta)
    
    # 11. Adicionar histórico
    PropostaService.adicionar_historico(
        proposta, 
        funcionario.id, 
        'CRIADA', 
        'Proposta criada e finalizada'
    )
    
    db.session.commit()
    return proposta
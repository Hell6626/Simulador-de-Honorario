"""Create initial tables

Revision ID: 20241220_000
Revises: 
Create Date: 2024-12-20 09:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20241220_000'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    """Criar todas as tabelas iniciais do sistema"""
    
    # Tabela de empresas
    op.create_table('empresa',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('nome', sa.String(length=255), nullable=False),
        sa.Column('cnpj', sa.String(length=18), nullable=True),
        sa.Column('inscricao_estadual', sa.String(length=20), nullable=True),
        sa.Column('endereco', sa.String(length=255), nullable=True),
        sa.Column('telefone', sa.String(length=20), nullable=True),
        sa.Column('email', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('ativo', sa.Boolean(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Tabela de cargos
    op.create_table('cargo',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('nome', sa.String(length=100), nullable=False),
        sa.Column('descricao', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('ativo', sa.Boolean(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Tabela de funcionários
    op.create_table('funcionario',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('nome', sa.String(length=255), nullable=False),
        sa.Column('cpf', sa.String(length=14), nullable=True),
        sa.Column('email', sa.String(length=255), nullable=True),
        sa.Column('telefone', sa.String(length=20), nullable=True),
        sa.Column('cargo_id', sa.Integer(), nullable=True),
        sa.Column('empresa_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('ativo', sa.Boolean(), nullable=True),
        sa.ForeignKeyConstraint(['cargo_id'], ['cargo.id'], ),
        sa.ForeignKeyConstraint(['empresa_id'], ['empresa.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Tabela de tipos de atividade
    op.create_table('tipo_atividade',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('codigo', sa.String(length=10), nullable=False),
        sa.Column('nome', sa.String(length=100), nullable=False),
        sa.Column('aplicavel_pf', sa.Boolean(), nullable=True),
        sa.Column('aplicavel_pj', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('ativo', sa.Boolean(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('codigo')
    )
    
    # Tabela de regimes tributários
    op.create_table('regime_tributario',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('codigo', sa.String(length=10), nullable=False),
        sa.Column('nome', sa.String(length=100), nullable=False),
        sa.Column('descricao', sa.Text(), nullable=True),
        sa.Column('aplicavel_pf', sa.Boolean(), nullable=True),
        sa.Column('aplicavel_pj', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('ativo', sa.Boolean(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('codigo')
    )
    
    # Tabela de atividades por regime
    op.create_table('atividade_regime',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tipo_atividade_id', sa.Integer(), nullable=False),
        sa.Column('regime_tributario_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('ativo', sa.Boolean(), nullable=True),
        sa.ForeignKeyConstraint(['regime_tributario_id'], ['regime_tributario.id'], ),
        sa.ForeignKeyConstraint(['tipo_atividade_id'], ['tipo_atividade.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('tipo_atividade_id', 'regime_tributario_id')
    )
    
    # Tabela de faixas de faturamento
    op.create_table('faixa_faturamento',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('regime_tributario_id', sa.Integer(), nullable=False),
        sa.Column('valor_inicial', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('valor_final', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('aliquota', sa.Numeric(precision=5, scale=2), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('ativo', sa.Boolean(), nullable=True),
        sa.ForeignKeyConstraint(['regime_tributario_id'], ['regime_tributario.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Tabela de serviços
    op.create_table('servico',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('codigo', sa.String(length=20), nullable=False),
        sa.Column('nome', sa.String(length=255), nullable=False),
        sa.Column('categoria', sa.String(length=50), nullable=True),
        sa.Column('tipo_cobranca', sa.String(length=20), nullable=True),
        sa.Column('valor_base', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('descricao', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('ativo', sa.Boolean(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('codigo')
    )
    
    # Tabela de endereços
    op.create_table('endereco',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('cep', sa.String(length=10), nullable=True),
        sa.Column('logradouro', sa.String(length=255), nullable=True),
        sa.Column('numero', sa.String(length=20), nullable=True),
        sa.Column('complemento', sa.String(length=100), nullable=True),
        sa.Column('bairro', sa.String(length=100), nullable=True),
        sa.Column('cidade', sa.String(length=100), nullable=True),
        sa.Column('estado', sa.String(length=2), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('ativo', sa.Boolean(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Tabela de entidades jurídicas
    op.create_table('entidade_juridica',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('cnpj', sa.String(length=18), nullable=True),
        sa.Column('inscricao_estadual', sa.String(length=20), nullable=True),
        sa.Column('inscricao_municipal', sa.String(length=20), nullable=True),
        sa.Column('razao_social', sa.String(length=255), nullable=True),
        sa.Column('nome_fantasia', sa.String(length=255), nullable=True),
        sa.Column('data_abertura', sa.Date(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('ativo', sa.Boolean(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('cnpj')
    )
    
    # Tabela de clientes
    op.create_table('cliente',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('nome', sa.String(length=255), nullable=False),
        sa.Column('cpf_cnpj', sa.String(length=18), nullable=True),
        sa.Column('email', sa.String(length=255), nullable=True),
        sa.Column('telefone', sa.String(length=20), nullable=True),
        sa.Column('tipo_atividade_id', sa.Integer(), nullable=True),
        sa.Column('regime_tributario_id', sa.Integer(), nullable=True),
        sa.Column('endereco_id', sa.Integer(), nullable=True),
        sa.Column('entidade_juridica_id', sa.Integer(), nullable=True),
        sa.Column('data_abertura_empresa', sa.Date(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('ativo', sa.Boolean(), nullable=True),
        sa.ForeignKeyConstraint(['endereco_id'], ['endereco.id'], ),
        sa.ForeignKeyConstraint(['entidade_juridica_id'], ['entidade_juridica.id'], ),
        sa.ForeignKeyConstraint(['regime_tributario_id'], ['regime_tributario.id'], ),
        sa.ForeignKeyConstraint(['tipo_atividade_id'], ['tipo_atividade.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('cpf_cnpj')
    )
    
    # Tabela de propostas
    op.create_table('proposta',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('numero', sa.String(length=50), nullable=False),
        sa.Column('cliente_id', sa.Integer(), nullable=False),
        sa.Column('funcionario_responsavel_id', sa.Integer(), nullable=True),
        sa.Column('faixa_faturamento_id', sa.Integer(), nullable=True),
        sa.Column('valor_total', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=True),
        sa.Column('data_proposta', sa.Date(), nullable=True),
        sa.Column('validade_proposta', sa.Date(), nullable=True),
        sa.Column('observacoes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('ativo', sa.Boolean(), nullable=True),
        sa.ForeignKeyConstraint(['cliente_id'], ['cliente.id'], ),
        sa.ForeignKeyConstraint(['faixa_faturamento_id'], ['faixa_faturamento.id'], ),
        sa.ForeignKeyConstraint(['funcionario_responsavel_id'], ['funcionario.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('numero')
    )
    
    # Tabela de itens de proposta
    op.create_table('item_proposta',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('proposta_id', sa.Integer(), nullable=False),
        sa.Column('servico_id', sa.Integer(), nullable=False),
        sa.Column('quantidade', sa.Integer(), nullable=True),
        sa.Column('valor_unitario', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('valor_total', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('observacoes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('ativo', sa.Boolean(), nullable=True),
        sa.ForeignKeyConstraint(['proposta_id'], ['proposta.id'], ),
        sa.ForeignKeyConstraint(['servico_id'], ['servico.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Tabela de logs de proposta
    op.create_table('proposta_log',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('proposta_id', sa.Integer(), nullable=False),
        sa.Column('acao', sa.String(length=50), nullable=False),
        sa.Column('descricao', sa.Text(), nullable=True),
        sa.Column('usuario_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('ativo', sa.Boolean(), nullable=True),
        sa.ForeignKeyConstraint(['proposta_id'], ['proposta.id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    """Remover todas as tabelas criadas"""
    
    # Remover tabelas na ordem inversa (devido às foreign keys)
    op.drop_table('proposta_log')
    op.drop_table('item_proposta')
    op.drop_table('proposta')
    op.drop_table('cliente')
    op.drop_table('entidade_juridica')
    op.drop_table('endereco')
    op.drop_table('servico')
    op.drop_table('faixa_faturamento')
    op.drop_table('atividade_regime')
    op.drop_table('regime_tributario')
    op.drop_table('tipo_atividade')
    op.drop_table('funcionario')
    op.drop_table('cargo')
    op.drop_table('empresa')

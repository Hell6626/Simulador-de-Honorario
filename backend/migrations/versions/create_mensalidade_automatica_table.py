"""Create mensalidade_automatica table

Revision ID: create_mensalidade_automatica_table
Revises: add_percentual_desconto_to_proposta
Create Date: 2024-12-20 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'create_mensalidade_automatica_table'
down_revision = 'add_percentual_desconto_to_proposta'
branch_labels = None
depends_on = None


def upgrade():
    # Create mensalidade_automatica table
    op.create_table('mensalidade_automatica',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tipo_atividade_id', sa.Integer(), nullable=False),
        sa.Column('regime_tributario_id', sa.Integer(), nullable=False),
        sa.Column('faixa_faturamento_id', sa.Integer(), nullable=False),
        sa.Column('valor_mensalidade', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('observacoes', sa.Text(), nullable=True),
        sa.Column('ativo', sa.Boolean(), nullable=False, default=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['faixa_faturamento_id'], ['faixa_faturamento.id'], ),
        sa.ForeignKeyConstraint(['regime_tributario_id'], ['regime_tributario.id'], ),
        sa.ForeignKeyConstraint(['tipo_atividade_id'], ['tipo_atividade.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('tipo_atividade_id', 'regime_tributario_id', 'faixa_faturamento_id', name='unique_mensalidade_config')
    )
    
    # Create indexes
    op.create_index(op.f('ix_mensalidade_automatica_tipo_atividade_id'), 'mensalidade_automatica', ['tipo_atividade_id'], unique=False)
    op.create_index(op.f('ix_mensalidade_automatica_regime_tributario_id'), 'mensalidade_automatica', ['regime_tributario_id'], unique=False)
    op.create_index(op.f('ix_mensalidade_automatica_faixa_faturamento_id'), 'mensalidade_automatica', ['faixa_faturamento_id'], unique=False)


def downgrade():
    # Drop indexes
    op.drop_index(op.f('ix_mensalidade_automatica_faixa_faturamento_id'), table_name='mensalidade_automatica')
    op.drop_index(op.f('ix_mensalidade_automatica_regime_tributario_id'), table_name='mensalidade_automatica')
    op.drop_index(op.f('ix_mensalidade_automatica_tipo_atividade_id'), table_name='mensalidade_automatica')
    
    # Drop table
    op.drop_table('mensalidade_automatica')

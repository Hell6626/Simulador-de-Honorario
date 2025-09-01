"""Create notificacao table

Revision ID: c3d4e5f6g7h8
Revises: b2c3d4e5f6g7
Create Date: 2025-01-29 10:01:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c3d4e5f6g7h8'
down_revision = 'b2c3d4e5f6g7'
branch_labels = None
depends_on = None


def upgrade():
    # Create notificacao table
    op.create_table('notificacao',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tipo', sa.String(length=50), nullable=False),
        sa.Column('titulo', sa.String(length=200), nullable=False),
        sa.Column('mensagem', sa.Text(), nullable=False),
        sa.Column('proposta_id', sa.Integer(), nullable=True),
        sa.Column('para_funcionario_id', sa.Integer(), nullable=False),
        sa.Column('de_funcionario_id', sa.Integer(), nullable=True),
        sa.Column('lida', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('data_leitura', sa.DateTime(), nullable=True),
        sa.Column('ativo', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['de_funcionario_id'], ['funcionario.id'], ),
        sa.ForeignKeyConstraint(['para_funcionario_id'], ['funcionario.id'], ),
        sa.ForeignKeyConstraint(['proposta_id'], ['proposta.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes
    op.create_index(op.f('ix_notificacao_para_funcionario_id'), 'notificacao', ['para_funcionario_id'], unique=False)
    op.create_index(op.f('ix_notificacao_lida'), 'notificacao', ['lida'], unique=False)
    op.create_index(op.f('ix_notificacao_tipo'), 'notificacao', ['tipo'], unique=False)


def downgrade():
    # Drop indexes
    op.drop_index(op.f('ix_notificacao_tipo'), table_name='notificacao')
    op.drop_index(op.f('ix_notificacao_lida'), table_name='notificacao')
    op.drop_index(op.f('ix_notificacao_para_funcionario_id'), table_name='notificacao')
    
    # Drop table
    op.drop_table('notificacao')

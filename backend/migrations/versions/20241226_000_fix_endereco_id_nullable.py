"""Fix endereco_id nullable in entidade_juridica

Revision ID: 20241226_000
Revises: d40f383ff0d1
Create Date: 2024-12-26 18:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20241226_000'
down_revision = 'd40f383ff0d1'
branch_labels = None
depends_on = None


def upgrade():
    # Tornar endereco_id nullable na tabela entidade_juridica
    with op.batch_alter_table('entidade_juridica', schema=None) as batch_op:
        batch_op.alter_column('endereco_id',
               existing_type=sa.INTEGER(),
               nullable=True)


def downgrade():
    # Reverter endereco_id para NOT NULL
    with op.batch_alter_table('entidade_juridica', schema=None) as batch_op:
        batch_op.alter_column('endereco_id',
               existing_type=sa.INTEGER(),
               nullable=False)

"""Add is_holiday column to closing_prices

Revision ID: add_is_holiday_column
Revises: 7eb36068c3cd
Create Date: 2025-07-04 18:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_is_holiday_column'
down_revision = '7eb36068c3cd'
branch_labels = None
depends_on = None

def upgrade():
    # Add is_holiday column with default value False
    with op.batch_alter_table('closing_prices', schema=None) as batch_op:
        batch_op.add_column(sa.Column('is_holiday', sa.Boolean(), nullable=False, server_default='false'))

def downgrade():
    with op.batch_alter_table('closing_prices', schema=None) as batch_op:
        batch_op.drop_column('is_holiday') 
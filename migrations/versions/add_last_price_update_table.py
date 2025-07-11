"""Add last_price_update table

Revision ID: add_last_price_update
Revises: add_is_holiday_column
Create Date: 2025-07-04 19:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_last_price_update'
down_revision = 'add_is_holiday_column'
branch_labels = None
depends_on = None

def upgrade():
    op.create_table('last_price_update',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade():
    op.drop_table('last_price_update') 
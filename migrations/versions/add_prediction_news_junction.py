"""Add prediction news junction table

Revision ID: add_prediction_news_junction
Revises: add_news_tables
Create Date: 2024-03-19 11:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_prediction_news_junction'
down_revision = 'add_news_tables'
branch_labels = None
depends_on = None


def upgrade():
    # Create prediction_news junction table
    op.create_table(
        'prediction_news',
        sa.Column('prediction_id', sa.Integer(), nullable=False),
        sa.Column('news_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['prediction_id'], ['prediction_summaries.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['news_id'], ['classified_news.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('prediction_id', 'news_id')
    )

    # Remove prediction_id from classified_news and make url unique
    op.drop_constraint('classified_news_prediction_id_fkey', 'classified_news', type_='foreignkey')
    op.drop_column('classified_news', 'prediction_id')
    op.create_unique_constraint('uq_classified_news_url', 'classified_news', ['url'])


def downgrade():
    # Add prediction_id back to classified_news
    op.add_column('classified_news', sa.Column('prediction_id', sa.Integer(), nullable=True))
    op.create_foreign_key('classified_news_prediction_id_fkey', 'classified_news', 'prediction_summaries', ['prediction_id'], ['id'], ondelete='CASCADE')
    op.drop_constraint('uq_classified_news_url', 'classified_news', type_='unique')

    # Drop prediction_news junction table
    op.drop_table('prediction_news') 
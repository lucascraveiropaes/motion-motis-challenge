"""Manual migration for transaction_records table

Revision ID: 31d3e817cac8
Revises: 
Create Date: 2026-04-09 08:17:31.423567

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '31d3e817cac8'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'transaction_records',
        sa.Column('id', sa.Integer, primary_key=True, index=True),
        sa.Column('description', sa.String, nullable=False),
        sa.Column('category', sa.String, nullable=False),
        sa.Column('processed_at', sa.DateTime, server_default=sa.func.now())
    )


def downgrade() -> None:
    op.drop_table('transaction_records')

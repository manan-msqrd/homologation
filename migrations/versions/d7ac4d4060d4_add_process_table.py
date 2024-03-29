"""Add Process table

Revision ID: d7ac4d4060d4
Revises: a01ea49b8e0d
Create Date: 2024-01-25 12:37:30.027197

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd7ac4d4060d4'
down_revision = 'a01ea49b8e0d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('process_table',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('job_id', sa.String(length=20), nullable=False),
    sa.Column('admin_id', sa.String(length=50), nullable=False),
    sa.Column('operator_id', sa.String(length=50), nullable=False),
    sa.Column('date_time', sa.DateTime(), nullable=False),
    sa.Column('vehicle_name', sa.String(length=20), nullable=False),
    sa.Column('vehicle_part', sa.String(length=50), nullable=True),
    sa.Column('part_code_name', sa.String(length=100), nullable=True),
    sa.Column('part_code_requirement', sa.String(length=50), nullable=True),
    sa.Column('scan_output', sa.String(length=50), nullable=True),
    sa.Column('result', sa.String(length=20), nullable=False),
    sa.Column('image', sa.LargeBinary(), nullable=True),
    sa.Column('approve_status', sa.String(length=50), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('process_table')
    # ### end Alembic commands ###

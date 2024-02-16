"""Edit Process table and add final table

Revision ID: e245974a33c6
Revises: d7ac4d4060d4
Create Date: 2024-02-05 15:24:05.988238

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e245974a33c6'
down_revision = 'd7ac4d4060d4'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('final_table',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('job_id', sa.String(length=20), nullable=False),
    sa.Column('admin_id', sa.String(length=50), nullable=False),
    sa.Column('operator_id', sa.String(length=50), nullable=False),
    sa.Column('date_time_operator', sa.DateTime(), nullable=False),
    sa.Column('date_time_admin', sa.DateTime(), nullable=False),
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
    with op.batch_alter_table('process_table', schema=None) as batch_op:
        batch_op.add_column(sa.Column('vehicle_part_id', sa.Integer(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('process_table', schema=None) as batch_op:
        batch_op.drop_column('vehicle_part_id')

    op.drop_table('final_table')
    # ### end Alembic commands ###
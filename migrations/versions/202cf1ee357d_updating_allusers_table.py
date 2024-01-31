"""Updating AllUsers table

Revision ID: 202cf1ee357d
Revises: b9e33fe2b175
Create Date: 2024-01-22 13:40:16.598559

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '202cf1ee357d'
down_revision = 'b9e33fe2b175'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('all_users',
    sa.Column('employee_id', sa.String(length=20), nullable=False),
    sa.Column('name', sa.String(length=50), nullable=False),
    sa.Column('password', sa.String(length=50), nullable=False),
    sa.Column('user_type', sa.String(length=10), nullable=False),
    sa.PrimaryKeyConstraint('employee_id')
    )
    op.create_table('process_table',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('job_id', sa.String(length=20), nullable=False),
    sa.Column('admin_id', sa.String(length=50), nullable=False),
    sa.Column('operator_id', sa.String(length=50), nullable=False),
    sa.Column('date_time', sa.DateTime(), nullable=False),
    sa.Column('vehicle_name', sa.String(length=20), nullable=False),
    sa.Column('vehicle_part', sa.String(length=50), nullable=True),
    sa.Column('requirement', sa.String(length=50), nullable=True),
    sa.Column('scan_output', sa.String(length=50), nullable=True),
    sa.Column('result', sa.Boolean(), nullable=True),
    sa.Column('image', sa.LargeBinary(), nullable=True),
    sa.Column('approve_status', sa.String(length=50), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('test',
    sa.Column('ID', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('Parts', sa.String(length=50), nullable=True),
    sa.Column('Regulation_Requirements', sa.String(length=255), nullable=True),
    sa.Column('Expected_Value', sa.String(length=255), nullable=True),
    sa.PrimaryKeyConstraint('ID')
    )
    op.create_table('vehicle_details',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=50), nullable=False),
    sa.Column('variant', sa.String(length=50), nullable=False),
    sa.Column('model', sa.String(length=50), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('login_log',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.String(length=20), nullable=False),
    sa.Column('login_time', sa.DateTime(), nullable=False),
    sa.Column('logout_time', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['all_users.employee_id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.drop_table('session_log')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('session_log',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('employee_id', sa.VARCHAR(length=20), autoincrement=False, nullable=True),
    sa.Column('name', sa.VARCHAR(length=50), autoincrement=False, nullable=False),
    sa.PrimaryKeyConstraint('id', name='session_log_pkey')
    )
    op.drop_table('login_log')
    op.drop_table('vehicle_details')
    op.drop_table('test')
    op.drop_table('process_table')
    op.drop_table('all_users')
    # ### end Alembic commands ###
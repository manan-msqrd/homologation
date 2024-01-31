"""Edit Process table

Revision ID: a01ea49b8e0d
Revises: 438a54eb08e5
Create Date: 2024-01-25 12:35:13.802146

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a01ea49b8e0d'
down_revision = '438a54eb08e5'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('process_table', schema=None) as batch_op:
        batch_op.add_column(sa.Column('part_code_name', sa.String(length=100), nullable=True))
        batch_op.add_column(sa.Column('part_code_requirement', sa.String(length=50), nullable=True))
        batch_op.drop_column('requirement')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('process_table', schema=None) as batch_op:
        batch_op.add_column(sa.Column('requirement', sa.VARCHAR(length=50), autoincrement=False, nullable=True))
        batch_op.drop_column('part_code_requirement')
        batch_op.drop_column('part_code_name')

    # ### end Alembic commands ###
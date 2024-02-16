"""Edit Testtable

Revision ID: 2442855a04cc
Revises: 76cbe1c37adb
Create Date: 2024-02-08 12:01:50.861222

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '2442855a04cc'
down_revision = '76cbe1c37adb'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('test_table', schema=None) as batch_op:
        batch_op.alter_column('date_time',
               existing_type=postgresql.TIMESTAMP(),
               nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('test_table', schema=None) as batch_op:
        batch_op.alter_column('date_time',
               existing_type=postgresql.TIMESTAMP(),
               nullable=False)

    # ### end Alembic commands ###
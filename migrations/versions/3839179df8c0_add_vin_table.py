"""Add VIN Table

Revision ID: 3839179df8c0
Revises: 5b98b90a144c
Create Date: 2024-01-04 15:57:55.317429

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3839179df8c0'
down_revision = '5b98b90a144c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('vin',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('Activa_110_BS_VI_Year_Code', sa.String(length=50), nullable=True),
    sa.Column('Activa_110_BS_VI_Plant_Code', sa.String(length=50), nullable=True),
    sa.Column('Activa_110_BS_VI_Engine_No', sa.String(length=50), nullable=True),
    sa.Column('Activa_125_BS_IV_WMI', sa.String(length=50), nullable=True),
    sa.Column('Activa_125_BS_IV_Month_Code', sa.String(length=50), nullable=True),
    sa.Column('Activa_125_BS_TV_Year_Code', sa.String(length=50), nullable=True),
    sa.Column('Activa_125_BS_IV_Plant_Code', sa.String(length=50), nullable=True),
    sa.Column('Activa_125_BS_IV_Engine_No', sa.String(length=12), nullable=True),
    sa.Column('Activa_125_BS_VI_WMI', sa.String(length=50), nullable=True),
    sa.Column('Activa_125_BS_VI_Month_Code', sa.String(length=50), nullable=True),
    sa.Column('Activa_125_BS_VI_Year_Code', sa.String(length=50), nullable=True),
    sa.Column('Activa_125_BS_VI_Plant_Code', sa.String(length=50), nullable=True),
    sa.Column('Activa_125_BS_VI_Engine_No', sa.String(length=50), nullable=True),
    sa.Column('Dio_110_BS_IV_WMI', sa.String(length=50), nullable=True),
    sa.Column('Dio_110_BS_IV_Month_Code', sa.String(length=50), nullable=True),
    sa.Column('Dio_110_BS_TV_Year_Code', sa.String(length=50), nullable=True),
    sa.Column('Dio_110_BS_IV_Plant_Code', sa.String(length=50), nullable=True),
    sa.Column('Dio_110_BS_IV_Engine_No', sa.String(length=12), nullable=True),
    sa.Column('Dio_110_BS_VI_WMI', sa.String(length=50), nullable=True),
    sa.Column('Dio_110_BS_VI_Month_Code', sa.String(length=50), nullable=True),
    sa.Column('Dio_110_BS_VI_Year_Code', sa.String(length=50), nullable=True),
    sa.Column('Dio_110_BS_VI_Plant_Code', sa.String(length=50), nullable=True),
    sa.Column('Dio_110_BS_VI_Engine_No', sa.String(length=50), nullable=True),
    sa.Column('Dio_125_BS_VI_WMI', sa.String(length=50), nullable=True),
    sa.Column('Dio_125_BS_VI_Month_Code', sa.String(length=50), nullable=True),
    sa.Column('Dio_125_BS_VI_Year_Code', sa.String(length=50), nullable=True),
    sa.Column('Dio_125_BS_VI_Plant_Code', sa.String(length=50), nullable=True),
    sa.Column('Dio_125_BS_VI_Engine_No', sa.String(length=50), nullable=True),
    sa.Column('Grazia_125_BS_IV_WMI', sa.String(length=50), nullable=True),
    sa.Column('Grazia_125_BS_IV_Month_Code', sa.String(length=50), nullable=True),
    sa.Column('Grazia_125_BS_TV_Year_Code', sa.String(length=50), nullable=True),
    sa.Column('Grazia_125_BS_IV_Plant_Code', sa.String(length=50), nullable=True),
    sa.Column('Grazia_125_BS_IV_Engine_No', sa.String(length=12), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('vin')
    # ### end Alembic commands ###

"""170424

Revision ID: 5eebf58f7d28
Revises: b794f861d6a7
Create Date: 2024-04-16 22:22:57.042509

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '5eebf58f7d28'
down_revision = 'b794f861d6a7'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('contents', schema=None) as batch_op:
        batch_op.add_column(sa.Column('creation_date', sa.Date(), nullable=True))
        batch_op.add_column(sa.Column('creation_time', sa.Time(), nullable=True))
        batch_op.add_column(sa.Column('created_by', sa.Integer(), nullable=True))
        batch_op.create_foreign_key(None, 'Users', ['created_by'], ['id'])

    with op.batch_alter_table('influencers', schema=None) as batch_op:
        batch_op.add_column(sa.Column('creation_date', sa.Date(), nullable=True))
        batch_op.add_column(sa.Column('creation_time', sa.Time(), nullable=True))
        batch_op.add_column(sa.Column('created_by', sa.Integer(), nullable=True))
        batch_op.create_foreign_key(None, 'Users', ['created_by'], ['id'])

    with op.batch_alter_table('log', schema=None) as batch_op:
        batch_op.add_column(sa.Column('creation_date', sa.Date(), nullable=True))
        batch_op.add_column(sa.Column('creation_time', sa.Time(), nullable=True))
        batch_op.add_column(sa.Column('created_by', sa.Integer(), nullable=True))
        batch_op.drop_constraint('log_user_id_fkey', type_='foreignkey')
        batch_op.create_foreign_key(None, 'Users', ['created_by'], ['id'])
        batch_op.drop_column('log_time')
        batch_op.drop_column('user_id')
        batch_op.drop_column('log_date')

    with op.batch_alter_table('platforms', schema=None) as batch_op:
        batch_op.add_column(sa.Column('creation_date', sa.Date(), nullable=True))
        batch_op.add_column(sa.Column('creation_time', sa.Time(), nullable=True))
        batch_op.add_column(sa.Column('created_by', sa.Integer(), nullable=True))
        batch_op.create_foreign_key(None, 'Users', ['created_by'], ['id'])

    with op.batch_alter_table('scanlogs', schema=None) as batch_op:
        batch_op.add_column(sa.Column('creation_date', sa.Date(), nullable=True))
        batch_op.add_column(sa.Column('creation_time', sa.Time(), nullable=True))
        batch_op.drop_column('scan_time')
        batch_op.drop_column('scan_date')

    with op.batch_alter_table('socialaccounts', schema=None) as batch_op:
        batch_op.add_column(sa.Column('creation_date', sa.Date(), nullable=True))
        batch_op.add_column(sa.Column('creation_time', sa.Time(), nullable=True))
        batch_op.add_column(sa.Column('created_by', sa.Integer(), nullable=True))
        batch_op.create_foreign_key(None, 'Users', ['created_by'], ['id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('socialaccounts', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_column('created_by')
        batch_op.drop_column('creation_time')
        batch_op.drop_column('creation_date')

    with op.batch_alter_table('scanlogs', schema=None) as batch_op:
        batch_op.add_column(sa.Column('scan_date', sa.DATE(), autoincrement=False, nullable=True))
        batch_op.add_column(sa.Column('scan_time', postgresql.TIME(), autoincrement=False, nullable=True))
        batch_op.drop_column('creation_time')
        batch_op.drop_column('creation_date')

    with op.batch_alter_table('platforms', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_column('created_by')
        batch_op.drop_column('creation_time')
        batch_op.drop_column('creation_date')

    with op.batch_alter_table('log', schema=None) as batch_op:
        batch_op.add_column(sa.Column('log_date', sa.DATE(), autoincrement=False, nullable=True))
        batch_op.add_column(sa.Column('user_id', sa.INTEGER(), autoincrement=False, nullable=False))
        batch_op.add_column(sa.Column('log_time', postgresql.TIME(), autoincrement=False, nullable=True))
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.create_foreign_key('log_user_id_fkey', 'Users', ['user_id'], ['id'])
        batch_op.drop_column('created_by')
        batch_op.drop_column('creation_time')
        batch_op.drop_column('creation_date')

    with op.batch_alter_table('influencers', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_column('created_by')
        batch_op.drop_column('creation_time')
        batch_op.drop_column('creation_date')

    with op.batch_alter_table('contents', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_column('created_by')
        batch_op.drop_column('creation_time')
        batch_op.drop_column('creation_date')

    # ### end Alembic commands ###

"""240424-1

Revision ID: 933b63c8ee33
Revises: e0446bc87481
Create Date: 2024-04-24 23:28:49.083912

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '933b63c8ee33'
down_revision = 'e0446bc87481'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('socialaccounts', schema=None) as batch_op:
        batch_op.drop_constraint('socialaccounts_content_id_fkey', type_='foreignkey')
        batch_op.drop_column('content_id')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('socialaccounts', schema=None) as batch_op:
        batch_op.add_column(sa.Column('content_id', sa.INTEGER(), autoincrement=False, nullable=True))
        batch_op.create_foreign_key('socialaccounts_content_id_fkey', 'contents', ['content_id'], ['id'])

    # ### end Alembic commands ###

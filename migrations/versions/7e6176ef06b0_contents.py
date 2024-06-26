"""contents

Revision ID: 7e6176ef06b0
Revises: dab5e7697db1
Create Date: 2024-04-06 17:31:33.483897

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7e6176ef06b0'
down_revision = 'dab5e7697db1'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('socialaccounts', schema=None) as batch_op:
        batch_op.add_column(sa.Column('content_id', sa.Integer(), nullable=False))
        batch_op.create_foreign_key(None, 'contents', ['content_id'], ['id'])
        batch_op.drop_column('content_type')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('socialaccounts', schema=None) as batch_op:
        batch_op.add_column(sa.Column('content_type', sa.VARCHAR(), autoincrement=False, nullable=True))
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_column('content_id')

    # ### end Alembic commands ###

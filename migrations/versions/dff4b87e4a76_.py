"""empty message

Revision ID: dff4b87e4a76
Revises: 3a24fc02365e
Create Date: 2020-07-17 23:47:51.096874

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = 'dff4b87e4a76'
down_revision = '3a24fc02365e'
branch_labels = None
depends_on = None


def upgrade():
	# ### commands auto generated by Alembic - please adjust! ###
	op.add_column('package', sa.Column('approved_at', sa.DateTime(), nullable=True, server_default=None))

	op.execute("""
		UPDATE package SET approved_at=created_at WHERE approved;
	""")
	# ### end Alembic commands ###


def downgrade():
	# ### commands auto generated by Alembic - please adjust! ###
	op.drop_column('package', 'approved_at')
	# ### end Alembic commands ###

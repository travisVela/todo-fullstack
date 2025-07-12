"""phone number

Revision ID: 78ddae0e32a4
Revises: 
Create Date: 2025-07-12 02:16:47.407653

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '78ddae0e32a4'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("users", sa.Column("phone_number", sa.String(length=16), nullable=True))


def downgrade() -> None:
    op.drop_column("users", "phone_number")

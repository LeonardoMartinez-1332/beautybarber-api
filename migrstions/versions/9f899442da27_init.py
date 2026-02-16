"""init

Revision ID: 9f899442da27
Revises: f000ccea6231
Create Date: 2026-02-02 22:22:18.119030

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9f899442da27'
down_revision: Union[str, None] = 'f000ccea6231'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass

"""fix updated_at server default

Revision ID: 6b752d312514
Revises: 17ecabe20acc
Create Date: 2025-12-25 07:12:30.256350

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "6b752d312514"
down_revision: Union[str, Sequence[str], None] = "17ecabe20acc"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        ALTER TABLE users
        MODIFY updated_at DATETIME
        NOT NULL
        DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP
        """
    )
    op.execute(
        """
        ALTER TABLE refresh_tokens
        MODIFY updated_at DATETIME
        NOT NULL
        DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP
        """
    )


def downgrade() -> None:
    """Downgrade schema."""
    pass

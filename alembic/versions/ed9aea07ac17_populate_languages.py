"""populate_languages

Revision ID: ed9aea07ac17
Revises: 761249ebf49c
Create Date: 2025-11-25 18:31:04.244036

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "ed9aea07ac17"
down_revision: Union[str, Sequence[str], None] = "761249ebf49c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("INSERT INTO languages (name, slug) VALUES ('Python', 'python')")
    op.execute("INSERT INTO languages (name, slug) VALUES ('JavaScript', 'javascript')")
    op.execute("INSERT INTO languages (name, slug) VALUES ('Java', 'java')")
    op.execute("INSERT INTO languages (name, slug) VALUES ('Go', 'go')")


def downgrade() -> None:
    """Downgrade schema."""
    op.execute(
        "DELETE FROM languages WHERE slug IN ('python', 'javascript', 'java', 'go')"
    )

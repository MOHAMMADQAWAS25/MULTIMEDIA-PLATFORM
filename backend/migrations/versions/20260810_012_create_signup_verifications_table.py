"""create signup verifications table

Revision ID: 20260810_012
Revises: 20260810_011
Create Date: 2026-08-10 02:30:00
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "20260810_012"
down_revision: str | None = "20260810_011"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "signup_verifications",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("full_name", sa.String(length=120), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("department", sa.String(length=120), nullable=True),
        sa.Column("major", sa.String(length=120), nullable=True),
        sa.Column("code_hash", sa.Text(), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("consumed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id", name="pk_signup_verifications"),
    )
    op.create_index(
        "ix_signup_verifications_active_email",
        "signup_verifications",
        ["email"],
        postgresql_where=sa.text("consumed_at is null"),
    )
    op.create_index("ix_signup_verifications_expires_at", "signup_verifications", ["expires_at"])
    op.create_index("ix_signup_verifications_consumed_at", "signup_verifications", ["consumed_at"])


def downgrade() -> None:
    op.drop_index("ix_signup_verifications_consumed_at", table_name="signup_verifications")
    op.drop_index("ix_signup_verifications_expires_at", table_name="signup_verifications")
    op.drop_index("ix_signup_verifications_active_email", table_name="signup_verifications")
    op.drop_table("signup_verifications")

"""Initial migration

Revision ID: 20250211_initial_migration
Revises:
Create Date: 2025-02-11 00:00:00.000000

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic
revision = "20250211_initial_migration"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create companies table first
    op.create_table(
        "companies",
        sa.Column("company_uuid", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("auth_token", sa.String(255), nullable=False, unique=True),
        sa.Column(
            "created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()
        ),
    )

    # Create single_invoice_task_data table
    op.create_table(
        "single_invoice_task_data",
        sa.Column("task_uuid", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("my_company_idno", sa.String(50), nullable=False),
        sa.Column("person_name_certificate", sa.String(50), nullable=False),
        sa.Column("seria", sa.String(50), nullable=False),
        sa.Column("number", sa.Integer(), nullable=False),
        sa.Column("action_type", sa.String(50), nullable=False),
    )

    # Create company_tasks table with proper foreign keys
    op.create_table(
        "company_tasks",
        sa.Column("task_uuid", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("company_uuid", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("status", sa.String(50), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("task_type", sa.String(50), nullable=False),
    )

    # Add only company foreign key constraint
    op.create_foreign_key(
        "fk_company_tasks_company",
        "company_tasks",
        "companies",
        ["company_uuid"],
        ["company_uuid"],
    )

    # Create multiple_invoices_task_data table
    op.create_table(
        "multiple_invoices_task_data",
        sa.Column("task_uuid", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("my_company_idno", sa.String(50), nullable=False),
        sa.Column("person_name_certificate", sa.String(50), nullable=False),
        sa.Column("buyer_idno", sa.String(50), nullable=False),
        sa.Column("signature_type", sa.String(50), nullable=False),
        sa.Column("action_type", sa.String(50), nullable=False),
    )


def downgrade():
    # Drop tables in correct order
    op.drop_table("multiple_invoices_task_data")
    op.drop_table("company_tasks")
    op.drop_table("single_invoice_task_data")
    op.drop_table("companies")

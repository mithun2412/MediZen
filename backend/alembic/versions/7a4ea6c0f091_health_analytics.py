"""Add health analytics persistence tables.

Revision ID: 7a4ea6c0f091
Revises: 49876525e384
"""
from alembic import op
import sqlalchemy as sa

revision = "7a4ea6c0f091"
down_revision = "49876525e384"
branch_labels = None
depends_on = None

def upgrade():
    op.create_table("medication_logs", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False), sa.Column("reminder_id", sa.String(), nullable=True), sa.Column("medicine_name", sa.String(), nullable=False), sa.Column("scheduled_time", sa.DateTime(), nullable=False), sa.Column("status", sa.String(length=16), nullable=False, server_default="Pending"), sa.Column("taken_at", sa.DateTime(), nullable=True), sa.Column("created_at", sa.DateTime(), nullable=False))
    op.create_index("ix_medication_logs_user_id", "medication_logs", ["user_id"])
    op.create_index("ix_medication_logs_scheduled_time", "medication_logs", ["scheduled_time"])
    op.create_table("health_analytics", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False, unique=True), sa.Column("health_score", sa.Integer(), nullable=False, server_default="100"), sa.Column("adherence_percentage", sa.Float(), nullable=False, server_default="0"), sa.Column("risk_level", sa.String(length=16), nullable=False, server_default="Low"), sa.Column("last_updated", sa.DateTime(), nullable=False))
    op.create_table("symptom_trends", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False), sa.Column("symptom_name", sa.String(), nullable=False), sa.Column("severity", sa.String(length=16), nullable=False), sa.Column("recorded_date", sa.DateTime(), nullable=False))
    op.create_index("ix_symptom_trends_user_id", "symptom_trends", ["user_id"])

def downgrade():
    op.drop_table("symptom_trends"); op.drop_table("health_analytics"); op.drop_table("medication_logs")

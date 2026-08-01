"""Initial schema

Revision ID: 49876525e384
Revises: 6bf67f18cb25
Create Date: 2026-06-18 15:16:18.125179

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '49876525e384'
down_revision: Union[str, Sequence[str], None] = '6bf67f18cb25'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ============================================
    # DROP TABLES IN REVERSE DEPENDENCY ORDER
    # ============================================
    # Note: We use `op.execute('DROP TABLE IF EXISTS ... CASCADE')` 
    # to safely drop tables that may or may not exist
    
    # Drop tables that depend on reports
    op.execute('DROP TABLE IF EXISTS vector_indexes CASCADE')
    op.execute('DROP TABLE IF EXISTS report_chats CASCADE')
    op.execute('DROP TABLE IF EXISTS report_parameters CASCADE')
    
    # Drop reports (depends on users and conversations)
    op.execute('DROP TABLE IF EXISTS reports CASCADE')
    
    # Drop messages (depends on conversations)
    op.execute('DROP TABLE IF EXISTS messages CASCADE')
    
    # Drop conversations (depends on users)
    op.execute('DROP TABLE IF EXISTS conversations CASCADE')
    
    # Drop tables that depend on users
    op.execute('DROP TABLE IF EXISTS symptom_history CASCADE')
    op.execute('DROP TABLE IF EXISTS dose_logs CASCADE')
    op.execute('DROP TABLE IF EXISTS medicine_reminders CASCADE')
    
    # Finally drop users
    op.execute('DROP TABLE IF EXISTS users CASCADE')
    
    # ============================================
    # CREATE TABLES IN CORRECT ORDER
    # ============================================
    
    # 1. Create users
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('email', sa.String(length=150), nullable=False),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    
    # 2. Create conversations (depends on users)
    op.create_table(
        'conversations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=True),
        sa.Column('report_generated', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_conversations_id'), 'conversations', ['id'], unique=False)
    op.create_foreign_key('conversations_user_id_fkey', 'conversations', 'users', ['user_id'], ['id'])
    
    # 3. Create messages (depends on conversations)
    op.create_table(
        'messages',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('conversation_id', sa.Integer(), nullable=False),
        sa.Column('role', sa.String(length=50), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_messages_id'), 'messages', ['id'], unique=False)
    op.create_foreign_key('messages_conversation_id_fkey', 'messages', 'conversations', ['conversation_id'], ['id'])
    
    # 4. Create reports (depends on users and conversations)
    op.create_table(
        'reports',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('conversation_id', sa.Integer(), nullable=True),
        sa.Column('file_name', sa.String(length=255), nullable=False),
        sa.Column('file_path', sa.String(length=500), nullable=False),
        sa.Column('pdf_type', sa.String(length=50), nullable=True),
        sa.Column('extracted_text', sa.Text(), nullable=True),
        sa.Column('content', sa.Text(), nullable=True),
        sa.Column('uploaded_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_reports_id'), 'reports', ['id'], unique=False)
    op.create_foreign_key('reports_user_id_fkey', 'reports', 'users', ['user_id'], ['id'])
    op.create_foreign_key('reports_conversation_id_fkey', 'reports', 'conversations', ['conversation_id'], ['id'])
    
    # 5. Create report_parameters (depends on reports)
    op.create_table(
        'report_parameters',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('report_id', sa.Integer(), nullable=False),
        sa.Column('parameter_name', sa.String(length=255), nullable=False),
        sa.Column('value', sa.String(length=100), nullable=True),
        sa.Column('unit', sa.String(length=50), nullable=True),
        sa.Column('normal_min', sa.String(length=100), nullable=True),
        sa.Column('normal_max', sa.String(length=100), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_report_parameters_id'), 'report_parameters', ['id'], unique=False)
    op.create_foreign_key('report_parameters_report_id_fkey', 'report_parameters', 'reports', ['report_id'], ['id'])
    
    # 6. Create report_chats (depends on reports)
    op.create_table(
        'report_chats',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('report_id', sa.Integer(), nullable=False),
        sa.Column('question', sa.Text(), nullable=False),
        sa.Column('answer', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_report_chats_id'), 'report_chats', ['id'], unique=False)
    op.create_foreign_key('report_chats_report_id_fkey', 'report_chats', 'reports', ['report_id'], ['id'])
    
    # 7. Create vector_indexes (depends on reports)
    op.create_table(
        'vector_indexes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('report_id', sa.Integer(), nullable=False),
        sa.Column('chunk_index', sa.Integer(), nullable=False),
        sa.Column('chunk_text', sa.Text(), nullable=False),
        sa.Column('embedding', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_vector_indexes_id'), 'vector_indexes', ['id'], unique=False)
    op.create_foreign_key('vector_indexes_report_id_fkey', 'vector_indexes', 'reports', ['report_id'], ['id'])
    
    # 8. Create symptom_history (depends on users)
    op.create_table(
        'symptom_history',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('symptom', sa.Text(), nullable=False),
        sa.Column('analysis', sa.Text(), nullable=False),
        sa.Column('severity', sa.String(length=20), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_symptom_history_id'), 'symptom_history', ['id'], unique=False)
    op.create_foreign_key('symptom_history_user_id_fkey', 'symptom_history', 'users', ['user_id'], ['id'])
    
    # 9. Create medicine_reminders (depends on users)
    op.create_table(
        'medicine_reminders',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('medicine_name', sa.String(), nullable=False),
        sa.Column('dosage', sa.String(), nullable=False),
        sa.Column('reminder_time', sa.Time(), nullable=True),
        sa.Column('continue_medicine_until', sa.Date(), nullable=True),
        sa.Column('status', sa.String(), nullable=True, server_default='Active'),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_foreign_key('medicine_reminders_user_id_fkey', 'medicine_reminders', 'users', ['user_id'], ['id'])
    
    # 10. Create dose_logs (depends on users and medicine_reminders)
    op.create_table(
        'dose_logs',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('reminder_id', sa.String(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('scheduled_date', sa.Date(), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='Pending'),
        sa.Column('taken_at', sa.DateTime(), nullable=True),
        sa.Column('snoozed_until', sa.DateTime(), nullable=True),
        sa.Column('logged_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_dose_logs_id'), 'dose_logs', ['id'], unique=False)
    op.create_foreign_key('dose_logs_user_id_fkey', 'dose_logs', 'users', ['user_id'], ['id'])
    op.create_foreign_key('dose_logs_reminder_id_fkey', 'dose_logs', 'medicine_reminders', ['reminder_id'], ['id'])


def downgrade() -> None:
    """Downgrade schema."""
    # Drop tables in reverse order of creation (children first)
    op.execute('DROP TABLE IF EXISTS dose_logs CASCADE')
    op.execute('DROP TABLE IF EXISTS medicine_reminders CASCADE')
    op.execute('DROP TABLE IF EXISTS symptom_history CASCADE')
    op.execute('DROP TABLE IF EXISTS vector_indexes CASCADE')
    op.execute('DROP TABLE IF EXISTS report_chats CASCADE')
    op.execute('DROP TABLE IF EXISTS report_parameters CASCADE')
    op.execute('DROP TABLE IF EXISTS reports CASCADE')
    op.execute('DROP TABLE IF EXISTS messages CASCADE')
    op.execute('DROP TABLE IF EXISTS conversations CASCADE')
    op.execute('DROP TABLE IF EXISTS users CASCADE')
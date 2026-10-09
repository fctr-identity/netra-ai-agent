from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey, Integer, Table, Index, UniqueConstraint, Text, JSON, Enum as SQLEnum
from sqlalchemy.sql import func, text, functions
from datetime import datetime, timezone
import enum

Base = declarative_base()

# Add this helper function at the top of the file
def get_utc_now():
    """Return current UTC datetime"""
    return datetime.now(timezone.utc)

class SyncStatus(enum.Enum):
    """Status of a sync operation"""
    IDLE = "idle"
    RUNNING = "running" 
    STARTED = "started"
    COMPLETED = "completed"
    FAILED = "failed"
    PARTIAL = "partial"
    CANCELED = "canceled"
    SUCCESS = "completed"   

# Add these fields to your SyncHistory class
class SyncHistory(Base):
    __tablename__ = "sync_history"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    tenant_id = Column(String, nullable=False, index=True)
    entity_type = Column(String, nullable=True)  # Add this field for SyncOrchestrator compatibility
    last_successful_sync = Column(DateTime(timezone=True), nullable=True)  # Add this field
    start_time = Column(DateTime(timezone=True), default=get_utc_now, nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=True)
    sync_end_time = Column(DateTime(timezone=True), nullable=True)  # Add alias for end_time
    status = Column(SQLEnum(SyncStatus), default=SyncStatus.IDLE, nullable=False)
    success = Column(Boolean, default=False)
    error_details = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)  # Add alias for error_details
    
    # Entity counts
    users_count = Column(Integer, default=0)
    groups_count = Column(Integer, default=0)
    apps_count = Column(Integer, default=0)
    policies_count = Column(Integer, default=0)
    devices_count = Column(Integer, default=0)
    mfa_count = Column(Integer, default=0)
    records_processed = Column(Integer, default=0)  
    
    # Progress tracking
    progress_percentage = Column(Integer, default=0)
    
    # Process tracking (for cancellation)
    process_id = Column(String, nullable=True)
    
    # Indexes for frequent queries
    __table_args__ = (
        Index('idx_sync_history_tenant_status', 'tenant_id', 'status'),
        Index('idx_sync_history_tenant_time', 'tenant_id', 'start_time'),
        Index('idx_sync_history_entity_type', 'entity_type'),  # Add index for entity_type
    )

    # Add this property to handle the SUCCESS vs COMPLETED mismatch
    @property
    def SUCCESS(self):
        return SyncStatus.COMPLETED 

# Authentication Models
class UserRole(str, enum.Enum):
    ADMIN = "admin"
    USER = "user"

class AuthUser(Base):
    """User model for authentication"""
    __tablename__ = "auth_users"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(SQLEnum(UserRole), default=UserRole.ADMIN, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=get_utc_now, nullable=False)
    updated_at = Column(DateTime, default=get_utc_now, onupdate=get_utc_now, nullable=False)
    
    # Keep track of whether initial setup has been completed
    setup_completed = Column(Boolean, default=False, nullable=False)
    
    # For security, add login tracking
    last_login = Column(DateTime, nullable=True)
    login_attempts = Column(Integer, default=0, nullable=False)
    locked_until = Column(DateTime, nullable=True)

    def __repr__(self):
        return f"<AuthUser username={self.username}, role={self.role}>"

class QueryProcedure(Base):
    """Private retrieval procedures, retained independently of conversation rows."""
    __tablename__ = "query_procedures"

    procedure_id = Column(String(36), primary_key=True)
    tenant_id = Column(String, nullable=False)
    owner_id = Column(String(255), nullable=False)
    sharing_scope = Column(String(32), nullable=False, default="private")
    query_text = Column(Text, nullable=False)
    description = Column(Text, nullable=False)
    script_code = Column(Text, nullable=False)
    content_hash = Column(String(64), nullable=False)
    compatibility_key = Column(String(64), nullable=False)
    evidence_json = Column(JSON, nullable=False)
    classification_json = Column(JSON, nullable=False)
    output_fields_json = Column(JSON, nullable=False)
    result_summary = Column(Text, nullable=False)
    data_source = Column(String(32), nullable=False)
    source = Column(String(32), nullable=False)
    originating_run_id = Column(String(255), nullable=False)
    parent_procedure_id = Column(String(36), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=get_utc_now)
    last_used_at = Column(DateTime(timezone=True), nullable=False, default=get_utc_now)
    execution_count = Column(Integer, nullable=False, default=1)

    __table_args__ = (
        UniqueConstraint('tenant_id', 'owner_id', 'sharing_scope', 'compatibility_key', 'content_hash', name='uix_query_procedure_content'),
        Index('idx_query_procedure_owner', 'tenant_id', 'owner_id', 'sharing_scope'),
        Index('idx_query_procedure_retention', 'tenant_id', 'last_used_at'),
    )


class QueryProcedureAdmission(Base):
    """Durable candidates awaiting semantic comparison; never exposed to reuse."""
    __tablename__ = "query_procedure_admissions"

    admission_id = Column(String(36), primary_key=True)
    tenant_id = Column(String, nullable=False)
    run_id = Column(String(255), nullable=False)
    payload_json = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=get_utc_now)
    next_attempt_at = Column(DateTime(timezone=True), nullable=False, default=get_utc_now)
    attempts = Column(Integer, nullable=False, default=0)
    lease_token = Column(String(36), nullable=True)
    lease_until = Column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        UniqueConstraint('tenant_id', 'run_id', name='uix_procedure_admission_run'),
        Index('idx_procedure_admission_due', 'tenant_id', 'next_attempt_at'),
    )


class QueryHistory(Base):
    """Table to store rolling history of queries and their results"""
    __tablename__ = "query_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    tenant_id = Column(String, nullable=False, index=True)
    user_id = Column(String(255), nullable=False, index=True)  # Future-proof for SSO/multi-user
    query_text = Column(Text, nullable=False)
    final_script = Column(Text, nullable=False)
    results_summary = Column(Text, nullable=True)
    is_favorite = Column(Boolean, default=False, index=True)
    created_at = Column(DateTime(timezone=True), default=get_utc_now, index=True)
    last_run_at = Column(DateTime(timezone=True), default=get_utc_now, index=True)

    # Execution metrics
    execution_count = Column(Integer, default=1, nullable=False)

    # Query source tracking
    source = Column(String(20), default="web", nullable=False)  # "web", "cli", or "slack"
    slack_user_id = Column(String(255), nullable=True)
    slack_channel_id = Column(String(255), nullable=True)
    slack_thread_ts = Column(String(255), nullable=True)

    __table_args__ = (
        Index('idx_query_history_tenant_fav', 'tenant_id', 'is_favorite'),
        Index('idx_query_history_last_run', 'last_run_at'),
        # Composite index for UPSERT duplicate detection per-user by query text only
        Index('idx_query_upsert', 'tenant_id', 'user_id', 'query_text'),
        Index('idx_query_history_source', 'source'),
    )

    def __repr__(self):
        return f"<QueryHistory id={self.id}, query={self.query_text[:50]}...>"


class ConversationSession(Base):
    """Conversation session metadata for multi-turn chat history."""
    __tablename__ = "conversation_sessions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    tenant_id = Column(String, nullable=False, index=True)
    user_id = Column(String(255), nullable=False, index=True)
    session_id = Column(String(255), nullable=False, unique=True, index=True)
    source = Column(String(32), nullable=False, default="web")
    title = Column(Text, nullable=True)
    summary = Column(Text, nullable=True)
    status = Column(String(32), nullable=False, default="active")
    last_activity_at = Column(DateTime(timezone=True), default=get_utc_now, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), default=get_utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=get_utc_now, onupdate=get_utc_now, nullable=False)
    slack_thread_ts = Column(String(255), nullable=True)
    parent_session_id = Column(String(255), ForeignKey('conversation_sessions.session_id', ondelete='SET NULL'), nullable=True)
    handoff_reason = Column(String(64), nullable=True)
    is_pinned = Column(Boolean, default=False, nullable=False)
    is_archived = Column(Boolean, default=False, nullable=False)
    archived_at = Column(DateTime(timezone=True), nullable=True)
    started_from_query_history_id = Column(Integer, ForeignKey('query_history.id', ondelete='SET NULL'), nullable=True)

    __table_args__ = (
        Index('idx_conversation_sessions_user_activity', 'tenant_id', 'user_id', 'last_activity_at'),
        Index('idx_conversation_sessions_user_status', 'tenant_id', 'user_id', 'status'),
    )


class ConversationTurn(Base):
    """One persisted turn within a conversation session."""
    __tablename__ = "conversation_turns"

    id = Column(Integer, primary_key=True, autoincrement=True)
    tenant_id = Column(String, nullable=False, index=True)
    session_id = Column(String(255), ForeignKey('conversation_sessions.session_id', ondelete='CASCADE'), nullable=False)
    run_id = Column(String(255), nullable=False, unique=True, index=True)
    turn_number = Column(Integer, nullable=False)
    query_text = Column(Text, nullable=False)
    source = Column(String(32), nullable=False, default="user")
    query_history_id = Column(Integer, ForeignKey('query_history.id', ondelete='SET NULL'), nullable=True)
    status = Column(String(32), nullable=False, default="created")
    completion_mode = Column(String(32), nullable=True)
    approval_state = Column(String(32), nullable=True)
    deferred_execution_state = Column(String(32), nullable=True)
    display_type = Column(String(64), nullable=True)
    final_response_summary = Column(Text, nullable=True)
    result_count = Column(Integer, nullable=True)
    is_partial_result = Column(Boolean, default=False, nullable=False)
    token_usage_json = Column(JSON, nullable=True)
    turn_dir = Column(Text, nullable=True)
    artifact_file = Column(Text, nullable=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=get_utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=get_utc_now, onupdate=get_utc_now, nullable=False)

    __table_args__ = (
        UniqueConstraint('session_id', 'turn_number', name='uix_conversation_turn_session_turn'),
        Index('idx_conversation_turns_session_created', 'tenant_id', 'session_id', 'created_at'),
        Index('idx_conversation_turns_completion_mode', 'tenant_id', 'completion_mode'),
    )


class ConversationResultSet(Base):
    """Reusable result-set metadata for follow-up resolution."""
    __tablename__ = "conversation_result_sets"

    id = Column(Integer, primary_key=True, autoincrement=True)
    tenant_id = Column(String, nullable=False, index=True)
    session_id = Column(String(255), ForeignKey('conversation_sessions.session_id', ondelete='CASCADE'), nullable=False, index=True)
    run_id = Column(String(255), nullable=False, index=True)
    turn_number = Column(Integer, nullable=False)
    sequence_in_turn = Column(Integer, nullable=False)
    result_set_id = Column(String(255), nullable=False, unique=True, index=True)
    storage_path = Column(Text, nullable=False)
    source_specialist = Column(String(32), nullable=False)
    entity_type = Column(String(64), nullable=False, index=True)
    derivation_kind = Column(String(32), nullable=False, default='initial', index=True)
    user_facing_label = Column(String(255), nullable=True, index=True)
    filter_summary = Column(Text, nullable=True)
    row_count = Column(Integer, nullable=True)
    is_empty = Column(Boolean, default=False, nullable=False)
    is_partial = Column(Boolean, default=False, nullable=False)
    key_columns_json = Column(JSON, nullable=True)
    metadata_json = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), default=get_utc_now, nullable=False)

    __table_args__ = (
        UniqueConstraint('session_id', 'turn_number', 'sequence_in_turn', name='uix_conversation_result_set_sequence'),
        Index('idx_conversation_result_sets_entity', 'tenant_id', 'session_id', 'entity_type', 'created_at'),
        Index('idx_conversation_result_sets_label', 'tenant_id', 'session_id', 'user_facing_label', 'created_at'),
    )


class ConversationResultSetParent(Base):
    """Lineage links between derived result sets and parents."""
    __tablename__ = "conversation_result_set_parents"

    child_result_set_id = Column(String(255), ForeignKey('conversation_result_sets.result_set_id', ondelete='CASCADE'), primary_key=True)
    parent_result_set_id = Column(String(255), ForeignKey('conversation_result_sets.result_set_id', ondelete='CASCADE'), primary_key=True)
    created_at = Column(DateTime(timezone=True), default=get_utc_now, nullable=False)

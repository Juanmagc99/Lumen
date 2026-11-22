"""SQLAlchemy persistence models."""

import uuid
from datetime import datetime

from sqlalchemy import Boolean, CheckConstraint, Column, DateTime, ForeignKey, Index, Integer, Numeric, String, Table, Text, func, text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class UserAccount(Base):
    __tablename__ = "user_accounts"
    __table_args__ = (
        CheckConstraint("role IN ('administrator', 'operator')", name="user_account_role"),
        CheckConstraint("length(trim(username)) > 0", name="user_account_username"),
        Index("user_account_username_unique", text("lower(username)"), unique=True),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username: Mapped[str] = mapped_column(String(150), nullable=False)
    password_hash: Mapped[str] = mapped_column(Text, nullable=False)
    role: Mapped[str] = mapped_column(String(16), nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("true"))


class UserSession(Base):
    __tablename__ = "user_sessions"

    token_digest: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("user_accounts.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)


class SignInCounter(Base):
    __tablename__ = "sign_in_counters"
    __table_args__ = (CheckConstraint("failures >= 0", name="sign_in_counter_failures"),)

    key: Mapped[str] = mapped_column(String(64), primary_key=True)
    failures: Mapped[int] = mapped_column(Integer, nullable=False)
    window_started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    blocked_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


ticket_manual_categories = Table(
    "ticket_manual_categories", Base.metadata,
    Column("ticket_id", UUID(as_uuid=True), ForeignKey("tickets.id", ondelete="CASCADE"), primary_key=True),
    Column("category_id", UUID(as_uuid=True), ForeignKey("classification_options.id"), primary_key=True),
)
classification_job_categories = Table(
    "classification_job_categories", Base.metadata,
    Column("ticket_id", UUID(as_uuid=True), ForeignKey("classification_jobs.ticket_id", ondelete="CASCADE"), primary_key=True),
    Column("category_id", UUID(as_uuid=True), ForeignKey("classification_options.id"), primary_key=True),
)


class Ticket(Base):
    __tablename__ = "tickets"
    __table_args__ = (CheckConstraint("classification_revision >= 0", name="ticket_classification_revision"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    subject: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    received_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    manual_categories_override: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("false"))
    manual_priority_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("classification_options.id"))
    classification_revision: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))
    manual_categories: Mapped[list["ClassificationOption"]] = relationship(secondary=ticket_manual_categories, lazy="selectin", order_by="ClassificationOption.name")
    manual_priority: Mapped["ClassificationOption | None"] = relationship(foreign_keys=[manual_priority_id], lazy="selectin")
    classification: Mapped["ClassificationJob | None"] = relationship(lazy="selectin", uselist=False)

    @property
    def classification_status(self) -> str:
        return self.classification.status if self.classification else "unavailable"

    @property
    def classification_result(self) -> str | None:
        return self.classification.result if self.classification else None

    @property
    def classification_source(self) -> str | None:
        return self.classification.result_source if self.classification else None

    @property
    def classification_categories(self) -> list["ClassificationOption"]:
        return self.classification.categories if self.classification else []

    @property
    def classification_priority(self) -> "ClassificationOption | None":
        return self.classification.priority if self.classification else None

    @property
    def classification_failure_reason(self) -> str | None:
        return self.classification.failure_reason if self.classification else None


class TicketResponse(Base):
    __tablename__ = "ticket_responses"
    __table_args__ = (
        CheckConstraint("text ~ '[^[:space:]]'", name="ticket_response_text"),
        CheckConstraint("status IN ('draft', 'approved')", name="ticket_response_status"),
        CheckConstraint("revision > 0", name="ticket_response_revision"),
    )

    ticket_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tickets.id", ondelete="CASCADE"), primary_key=True)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(16), nullable=False)
    edited_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    revision: Mapped[int] = mapped_column(Integer, nullable=False)
    adopted_generation_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("response_generations.id", name="response_adopted_generation_fk"))


class KnowledgeBase(Base):
    __tablename__ = "knowledge_bases"
    __table_args__ = (CheckConstraint("name ~ '[^[:space:]]'", name="knowledge_base_name"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())


class KnowledgeDocument(Base):
    __tablename__ = "knowledge_documents"
    __table_args__ = (CheckConstraint("name ~ '[^[:space:]]'", name="knowledge_document_name"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    knowledge_base_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("knowledge_bases.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("true"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())


class KnowledgeVersion(Base):
    __tablename__ = "knowledge_versions"
    __table_args__ = (
        CheckConstraint("version > 0", name="knowledge_version_number"),
        CheckConstraint("content ~ '[^[:space:]]'", name="knowledge_version_content"),
        Index("knowledge_version_unique", "document_id", "version", unique=True),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("knowledge_documents.id"), nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())


class KnowledgeChunk(Base):
    __tablename__ = "knowledge_chunks"
    __table_args__ = (Index("knowledge_chunk_unique", "version_id", "position", unique=True),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    version_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("knowledge_versions.id"), nullable=False)
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)


class IngestionJob(Base):
    __tablename__ = "ingestion_jobs"
    __table_args__ = (
        CheckConstraint("status IN ('pending', 'processing', 'ready', 'failed')", name="ingestion_status"),
        CheckConstraint("attempts >= 0", name="ingestion_attempts"),
        CheckConstraint("(status = 'processing' AND claim_token IS NOT NULL AND claim_expires_at IS NOT NULL) OR (status <> 'processing' AND claim_token IS NULL AND claim_expires_at IS NULL)", name="ingestion_claim"),
    )

    version_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("knowledge_versions.id"), primary_key=True)
    status: Mapped[str] = mapped_column(String(16), nullable=False, server_default="pending")
    attempts: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    available_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    claim_token: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    claim_expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    failure_reason: Mapped[str | None] = mapped_column(String(255))


class ResponseGeneration(Base):
    __tablename__ = "response_generations"
    __table_args__ = (
        CheckConstraint("status IN ('queued', 'running', 'completed', 'failed')", name="response_generation_status"),
        CheckConstraint("attempts >= 0", name="response_generation_attempts"),
        CheckConstraint("(status = 'running' AND claim_token IS NOT NULL AND claim_expires_at IS NOT NULL) OR (status <> 'running' AND claim_token IS NULL AND claim_expires_at IS NULL)", name="response_generation_claim"),
        Index("response_generation_active_ticket", "ticket_id", unique=True, postgresql_where=text("status IN ('queued', 'running')")),
    )
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ticket_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tickets.id"), nullable=False)
    knowledge_base_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("knowledge_bases.id"), nullable=True)
    subject: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(16), nullable=False, server_default="queued")
    attempts: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    available_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    claim_token: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    claim_expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    original_text: Mapped[str | None] = mapped_column(Text)
    rationale: Mapped[str | None] = mapped_column(Text)
    insufficient_evidence: Mapped[bool | None] = mapped_column(Boolean)
    failure_reason: Mapped[str | None] = mapped_column(String(64))


class ResponseAttempt(Base):
    __tablename__ = "response_attempts"
    __table_args__ = (Index("response_attempt_generation", "generation_id", "started_at"),)
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    generation_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("response_generations.id"), nullable=False)
    claim_token: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    status: Mapped[str] = mapped_column(String(24), nullable=False)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    requested_model: Mapped[str | None] = mapped_column(Text)
    reported_model: Mapped[str | None] = mapped_column(Text)
    provider: Mapped[str | None] = mapped_column(Text)
    config_version: Mapped[str] = mapped_column(String(64), nullable=False)
    sources: Mapped[list] = mapped_column(JSONB, nullable=False)
    citations: Mapped[list | None] = mapped_column(JSONB)
    provider_request_id: Mapped[str | None] = mapped_column(Text)
    input_tokens: Mapped[int | None] = mapped_column(Integer)
    output_tokens: Mapped[int | None] = mapped_column(Integer)
    estimated_cost: Mapped[object | None] = mapped_column(Numeric(20, 8))
    currency: Mapped[str | None] = mapped_column(String(3))
    pricing_basis: Mapped[str | None] = mapped_column(Text)
    failure_reason: Mapped[str | None] = mapped_column(String(64))
    retrieval_mode: Mapped[str | None] = mapped_column(String(16))
    retrieval_reason: Mapped[str | None] = mapped_column(String(64))
    embedding_input_tokens: Mapped[int | None] = mapped_column(Integer)


class ResponseCallReservation(Base):
    __tablename__ = "response_call_reservations"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    attempt_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("response_attempts.id"), nullable=False, unique=True)
    reserved_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    released_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class IdempotencyKey(Base):
    __tablename__ = "idempotency_keys"

    key: Mapped[str] = mapped_column(String(255), primary_key=True)
    ticket_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tickets.id", ondelete="CASCADE"), nullable=False, unique=True)


class ClassificationOption(Base):
    __tablename__ = "classification_options"
    __table_args__ = (
        CheckConstraint("kind IN ('category', 'priority')", name="classification_option_kind"),
        CheckConstraint("name ~ '[^[:space:]]'", name="classification_option_name"),
        CheckConstraint("color ~ '^#[0-9A-Fa-f]{6}$'", name="classification_option_color"),
        Index("classification_option_unique_name", "kind", text("lower(regexp_replace(name, '^[[:space:]]+|[[:space:]]+$', '', 'g'))"), unique=True),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    kind: Mapped[str] = mapped_column(String(16), nullable=False)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("true"))
    color: Mapped[str] = mapped_column(String(7), nullable=False, server_default="#64748B")


class ClassificationJob(Base):
    __tablename__ = "classification_jobs"
    __table_args__ = (
        CheckConstraint("status IN ('pending', 'processing', 'completed', 'failed')", name="classification_status"),
        CheckConstraint("attempts >= 0", name="classification_attempts"),
        CheckConstraint("(status = 'processing' AND claim_token IS NOT NULL AND claim_expires_at IS NOT NULL) OR (status <> 'processing' AND claim_token IS NULL AND claim_expires_at IS NULL)", name="classification_claim"),
    )

    ticket_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tickets.id", ondelete="CASCADE"), primary_key=True)
    status: Mapped[str] = mapped_column(String(16), nullable=False, server_default="pending")
    attempts: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    available_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    claim_token: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    claim_expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    result: Mapped[str | None] = mapped_column(Text)
    result_source: Mapped[str | None] = mapped_column(String(32))
    priority_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("classification_options.id"))
    failure_reason: Mapped[str | None] = mapped_column(String(32))
    categories: Mapped[list["ClassificationOption"]] = relationship(secondary=classification_job_categories, lazy="selectin", order_by="ClassificationOption.name")
    priority: Mapped["ClassificationOption | None"] = relationship(foreign_keys=[priority_id], lazy="selectin")

import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    String,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from src.infrastructure.database import Base


class WorkspaceORM(Base):
    __tablename__ = "workspaces"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        index=True,
        server_default=text("gen_random_uuid()"),
    )
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    category = Column(String, nullable=True) # e.g., 'Personal', 'Business', 'Investment'
    owner_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    owner = relationship("UserORM", backref="owned_workspaces")
    members = relationship(
        "WorkspaceMemberORM", back_populates="workspace", cascade="all, delete-orphan"
    )

    __table_args__ = (
        UniqueConstraint("owner_id", "name", name="uq_workspace_owner_name"),
    )


class WorkspaceMemberORM(Base):
    __tablename__ = "workspace_members"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workspace_id = Column(
        UUID(as_uuid=True),
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )
    role = Column(String, nullable=False)
    joined_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    # Relationships
    workspace = relationship("WorkspaceORM", back_populates="members")
    user = relationship("UserORM", backref="workspace_memberships")

    __table_args__ = (
        UniqueConstraint("workspace_id", "user_id", name="uq_workspace_member"),
    )

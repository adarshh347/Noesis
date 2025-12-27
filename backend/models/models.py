"""
SQLAlchemy models for Noesis
"""
from sqlalchemy import Column, String, Integer, Text, Boolean, DateTime, ForeignKey, Enum as SQLEnum, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid
import enum

from backend.database.config import Base


class BlockType(str, enum.Enum):
    """Types of blocks in a document"""
    PARAGRAPH = "paragraph"
    HEADER = "header"
    QUOTE = "quote"
    AXIOM = "axiom"
    LIST = "list"


class TransformIntent(str, enum.Enum):
    """Intent for AI transformations"""
    CRITIQUE = "critique"
    STEELMAN = "steelman"
    SIMPLIFY = "simplify"
    MYSTIFY = "mystify"
    EXPAND = "expand"
    CONDENSE = "condense"


class User(Base):
    """User model for authentication"""
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=True)  # Nullable for OAuth users
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    documents = relationship("Document", back_populates="owner", cascade="all, delete-orphan")


class Document(Base):
    """Document model - represents a philosophical essay/paper"""
    __tablename__ = "documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(500), nullable=False)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    tags = Column(JSON, default=list)  # List of tag strings
    folder_path = Column(String(1000), default="/")  # Hierarchical path like "/Projects/Ethics"
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    owner = relationship("User", back_populates="documents")
    blocks = relationship("Block", back_populates="document", cascade="all, delete-orphan", order_by="Block.position_index")


class Block(Base):
    """Block model - represents a paragraph/section in a document"""
    __tablename__ = "blocks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    position_index = Column(Integer, nullable=False)  # Order in the document
    block_type = Column(SQLEnum(BlockType), default=BlockType.PARAGRAPH, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    document = relationship("Document", back_populates="blocks")
    versions = relationship("BlockVersion", back_populates="block", cascade="all, delete-orphan", order_by="BlockVersion.created_at")


class BlockVersion(Base):
    """BlockVersion model - represents a version of a block (the "stack")"""
    __tablename__ = "block_versions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    block_id = Column(UUID(as_uuid=True), ForeignKey("blocks.id", ondelete="CASCADE"), nullable=False)
    content = Column(Text, nullable=False)  # The actual text content
    
    # Metadata about how this version was created
    author_type = Column(String(50), default="user")  # "user", "system_nietzsche", "system_kant", etc.
    transform_intent = Column(SQLEnum(TransformIntent), nullable=True)  # Only for AI-generated versions
    transform_params = Column(JSON, nullable=True)  # Additional parameters used for transformation
    
    # Version control
    is_active = Column(Boolean, default=True)  # Is this the currently visible version?
    version_number = Column(Integer, nullable=False)  # v1, v2, v3, etc.
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    block = relationship("Block", back_populates="versions")


class Connection(Base):
    """Connection model - represents links between blocks (for graph view)"""
    __tablename__ = "connections"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_block_id = Column(UUID(as_uuid=True), ForeignKey("blocks.id", ondelete="CASCADE"), nullable=False)
    target_block_id = Column(UUID(as_uuid=True), ForeignKey("blocks.id", ondelete="CASCADE"), nullable=False)
    connection_type = Column(String(50), default="reference")  # "reference", "contradiction", "support", etc.
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

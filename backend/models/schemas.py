"""
Pydantic schemas for API requests and responses
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID

from backend.models.models import BlockType, TransformIntent


# ============================================================================
# Document Schemas
# ============================================================================

class DocumentCreate(BaseModel):
    """Schema for creating a new document"""
    title: str = Field(..., min_length=1, max_length=500)
    tags: Optional[List[str]] = Field(default_factory=list)
    folder_path: Optional[str] = Field(default="/")


class DocumentUpdate(BaseModel):
    """Schema for updating a document"""
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    tags: Optional[List[str]] = None
    folder_path: Optional[str] = None


class DocumentResponse(BaseModel):
    """Schema for document response"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    title: str
    owner_id: UUID
    tags: List[str]
    folder_path: str
    created_at: datetime
    updated_at: datetime
    block_count: Optional[int] = None


# ============================================================================
# Block Schemas
# ============================================================================

class BlockCreate(BaseModel):
    """Schema for creating a new block"""
    document_id: UUID
    position_index: int = Field(..., ge=0)
    block_type: BlockType = BlockType.PARAGRAPH
    initial_content: str = Field(..., min_length=1)


class BlockUpdate(BaseModel):
    """Schema for updating a block"""
    position_index: Optional[int] = Field(None, ge=0)
    block_type: Optional[BlockType] = None


class BlockResponse(BaseModel):
    """Schema for block response"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    document_id: UUID
    position_index: int
    block_type: BlockType
    created_at: datetime
    updated_at: datetime
    active_version: Optional["BlockVersionResponse"] = None
    version_count: Optional[int] = None


# ============================================================================
# BlockVersion Schemas
# ============================================================================

class BlockVersionCreate(BaseModel):
    """Schema for creating a new block version"""
    block_id: UUID
    content: str = Field(..., min_length=1)
    author_type: str = "user"
    transform_intent: Optional[TransformIntent] = None
    transform_params: Optional[Dict[str, Any]] = None


class BlockVersionResponse(BaseModel):
    """Schema for block version response"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    block_id: UUID
    content: str
    author_type: str
    transform_intent: Optional[TransformIntent]
    transform_params: Optional[Dict[str, Any]]
    is_active: bool
    version_number: int
    created_at: datetime


# ============================================================================
# AI Transformation Schemas
# ============================================================================

class TransformRequest(BaseModel):
    """Schema for AI transformation request"""
    block_id: UUID
    thinker: str = Field(..., description="Philosopher to emulate (e.g., 'Nietzsche', 'Kant')")
    intent: TransformIntent
    style: Optional[str] = Field(None, description="Writing style (e.g., 'aphoristic', 'syllogistic')")
    model: Optional[str] = Field(None, description="LLM model to use (optional)")


class TransformResponse(BaseModel):
    """Schema for AI transformation response"""
    original_version_id: UUID
    new_version_id: UUID
    original_content: str
    transformed_content: str
    thinker: str
    intent: TransformIntent


# ============================================================================
# Logic Analysis Schemas
# ============================================================================

class LogicAnalysisRequest(BaseModel):
    """Schema for logic analysis request"""
    content: str = Field(..., min_length=1)


class Fallacy(BaseModel):
    """Schema for a logical fallacy"""
    type: str
    location: str
    explanation: str


class Assumption(BaseModel):
    """Schema for a hidden assumption"""
    assumption: str
    explanation: str


class ArgumentStructure(BaseModel):
    """Schema for argument structure"""
    premises: List[str]
    conclusion: str


class LogicAnalysisResponse(BaseModel):
    """Schema for logic analysis response"""
    fallacies: List[Fallacy]
    assumptions: List[Assumption]
    undefined_terms: List[str]
    structure: ArgumentStructure
    raw_analysis: Optional[str] = None


# ============================================================================
# Full Document with Blocks Schema
# ============================================================================

class DocumentWithBlocks(BaseModel):
    """Schema for document with all its blocks"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    title: str
    owner_id: UUID
    tags: List[str]
    folder_path: str
    created_at: datetime
    updated_at: datetime
    blocks: List[BlockResponse]


# ============================================================================
# Version Comparison Schema
# ============================================================================

class VersionComparisonRequest(BaseModel):
    """Schema for comparing two versions"""
    version_1_id: UUID
    version_2_id: UUID


class VersionComparisonResponse(BaseModel):
    """Schema for version comparison response"""
    version_1: BlockVersionResponse
    version_2: BlockVersionResponse
    diff: Optional[str] = None  # Could be a diff string or structured diff


# ============================================================================
# Error Response Schema
# ============================================================================

class ErrorResponse(BaseModel):
    """Schema for error responses"""
    detail: str
    error_code: Optional[str] = None

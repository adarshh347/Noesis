"""
Document routes - CRUD operations for documents
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List
from uuid import UUID

from database.config import get_db
from models.models import Document, Block, User
from models.schemas import (
    DocumentCreate,
    DocumentUpdate,
    DocumentResponse,
    DocumentWithBlocks,
    BlockResponse,
)

router = APIRouter(prefix="/documents", tags=["documents"])


# Temporary: Mock user ID until we implement auth
MOCK_USER_ID = "00000000-0000-0000-0000-000000000001"


@router.post("/", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def create_document(
    document: DocumentCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new document"""
    # TODO: Get user_id from auth token
    # For now, we'll create a mock user if it doesn't exist
    result = await db.execute(select(User).where(User.id == MOCK_USER_ID))
    user = result.scalar_one_or_none()
    
    if not user:
        # Create mock user
        user = User(
            id=MOCK_USER_ID,
            email="demo@noesis.app",
            username="demo_user",
        )
        db.add(user)
        await db.flush()
    
    # Create document
    new_doc = Document(
        title=document.title,
        owner_id=user.id,
        tags=document.tags or [],
        folder_path=document.folder_path or "/",
    )
    
    db.add(new_doc)
    await db.commit()
    await db.refresh(new_doc)
    
    return DocumentResponse(
        **new_doc.__dict__,
        block_count=0,
    )


@router.get("/", response_model=List[DocumentResponse])
async def list_documents(
    folder_path: str = "/",
    db: AsyncSession = Depends(get_db),
):
    """List all documents in a folder"""
    # TODO: Filter by authenticated user
    query = select(Document).where(Document.folder_path == folder_path)
    result = await db.execute(query)
    documents = result.scalars().all()
    
    # Get block counts for each document
    doc_responses = []
    for doc in documents:
        block_count_query = select(func.count(Block.id)).where(Block.document_id == doc.id)
        block_count_result = await db.execute(block_count_query)
        block_count = block_count_result.scalar()
        
        doc_responses.append(
            DocumentResponse(
                **doc.__dict__,
                block_count=block_count,
            )
        )
    
    return doc_responses


@router.get("/{document_id}", response_model=DocumentWithBlocks)
async def get_document(
    document_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get a document with all its blocks"""
    result = await db.execute(
        select(Document).where(Document.id == document_id)
    )
    document = result.scalar_one_or_none()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )
    
    # Get blocks with their active versions
    blocks_result = await db.execute(
        select(Block)
        .where(Block.document_id == document_id)
        .order_by(Block.position_index)
    )
    blocks = blocks_result.scalars().all()
    
    # Build response with blocks
    block_responses = []
    for block in blocks:
        # Get active version
        from models.models import BlockVersion
        active_version_result = await db.execute(
            select(BlockVersion)
            .where(BlockVersion.block_id == block.id, BlockVersion.is_active == True)
            .order_by(BlockVersion.version_number.desc())
        )
        active_version = active_version_result.scalar_one_or_none()
        
        # Get version count
        version_count_result = await db.execute(
            select(func.count(BlockVersion.id)).where(BlockVersion.block_id == block.id)
        )
        version_count = version_count_result.scalar()
        
        block_responses.append(
            BlockResponse(
                **block.__dict__,
                active_version=active_version,
                version_count=version_count,
            )
        )
    
    return DocumentWithBlocks(
        **document.__dict__,
        blocks=block_responses,
    )


@router.patch("/{document_id}", response_model=DocumentResponse)
async def update_document(
    document_id: UUID,
    updates: DocumentUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update a document"""
    result = await db.execute(
        select(Document).where(Document.id == document_id)
    )
    document = result.scalar_one_or_none()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )
    
    # Apply updates
    if updates.title is not None:
        document.title = updates.title
    if updates.tags is not None:
        document.tags = updates.tags
    if updates.folder_path is not None:
        document.folder_path = updates.folder_path
    
    await db.commit()
    await db.refresh(document)
    
    # Get block count
    block_count_result = await db.execute(
        select(func.count(Block.id)).where(Block.document_id == document.id)
    )
    block_count = block_count_result.scalar()
    
    return DocumentResponse(
        **document.__dict__,
        block_count=block_count,
    )


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Delete a document"""
    result = await db.execute(
        select(Document).where(Document.id == document_id)
    )
    document = result.scalar_one_or_none()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )
    
    await db.delete(document)
    await db.commit()
    
    return None

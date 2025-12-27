"""
Block routes - CRUD operations for blocks and versions
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List
from uuid import UUID

from backend.database.config import get_db
from backend.models.models import Block, BlockVersion, Document
from backend.models.schemas import (
    BlockCreate,
    BlockUpdate,
    BlockResponse,
    BlockVersionCreate,
    BlockVersionResponse,
)

router = APIRouter(prefix="/blocks", tags=["blocks"])


@router.post("/", response_model=BlockResponse, status_code=status.HTTP_201_CREATED)
async def create_block(
    block: BlockCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new block with an initial version"""
    # Verify document exists
    doc_result = await db.execute(
        select(Document).where(Document.id == block.document_id)
    )
    document = doc_result.scalar_one_or_none()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )
    
    # Create block
    new_block = Block(
        document_id=block.document_id,
        position_index=block.position_index,
        block_type=block.block_type,
    )
    
    db.add(new_block)
    await db.flush()  # Get the block ID
    
    # Create initial version
    initial_version = BlockVersion(
        block_id=new_block.id,
        content=block.initial_content,
        author_type="user",
        is_active=True,
        version_number=1,
    )
    
    db.add(initial_version)
    await db.commit()
    await db.refresh(new_block)
    await db.refresh(initial_version)
    
    return BlockResponse(
        **new_block.__dict__,
        active_version=initial_version,
        version_count=1,
    )


@router.get("/{block_id}", response_model=BlockResponse)
async def get_block(
    block_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get a block with its active version"""
    result = await db.execute(
        select(Block).where(Block.id == block_id)
    )
    block = result.scalar_one_or_none()
    
    if not block:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Block not found",
        )
    
    # Get active version
    active_version_result = await db.execute(
        select(BlockVersion)
        .where(BlockVersion.block_id == block_id, BlockVersion.is_active == True)
        .order_by(BlockVersion.version_number.desc())
    )
    active_version = active_version_result.scalar_one_or_none()
    
    # Get version count
    version_count_result = await db.execute(
        select(func.count(BlockVersion.id)).where(BlockVersion.block_id == block_id)
    )
    version_count = version_count_result.scalar()
    
    return BlockResponse(
        **block.__dict__,
        active_version=active_version,
        version_count=version_count,
    )


@router.get("/{block_id}/versions", response_model=List[BlockVersionResponse])
async def get_block_versions(
    block_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get all versions of a block (the version stack)"""
    # Verify block exists
    block_result = await db.execute(
        select(Block).where(Block.id == block_id)
    )
    block = block_result.scalar_one_or_none()
    
    if not block:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Block not found",
        )
    
    # Get all versions
    versions_result = await db.execute(
        select(BlockVersion)
        .where(BlockVersion.block_id == block_id)
        .order_by(BlockVersion.version_number.desc())
    )
    versions = versions_result.scalars().all()
    
    return [BlockVersionResponse(**v.__dict__) for v in versions]


@router.post("/{block_id}/versions", response_model=BlockVersionResponse, status_code=status.HTTP_201_CREATED)
async def create_block_version(
    block_id: UUID,
    version: BlockVersionCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new version of a block (push to the stack)"""
    # Verify block exists
    block_result = await db.execute(
        select(Block).where(Block.id == block_id)
    )
    block = block_result.scalar_one_or_none()
    
    if not block:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Block not found",
        )
    
    # Get current max version number
    max_version_result = await db.execute(
        select(func.max(BlockVersion.version_number))
        .where(BlockVersion.block_id == block_id)
    )
    max_version = max_version_result.scalar() or 0
    
    # Deactivate all previous versions
    await db.execute(
        select(BlockVersion)
        .where(BlockVersion.block_id == block_id)
    )
    existing_versions = (await db.execute(
        select(BlockVersion).where(BlockVersion.block_id == block_id)
    )).scalars().all()
    
    for v in existing_versions:
        v.is_active = False
    
    # Create new version
    new_version = BlockVersion(
        block_id=block_id,
        content=version.content,
        author_type=version.author_type,
        transform_intent=version.transform_intent,
        transform_params=version.transform_params,
        is_active=True,
        version_number=max_version + 1,
    )
    
    db.add(new_version)
    await db.commit()
    await db.refresh(new_version)
    
    return BlockVersionResponse(**new_version.__dict__)


@router.patch("/{block_id}/versions/{version_id}/activate", response_model=BlockVersionResponse)
async def activate_version(
    block_id: UUID,
    version_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Activate a specific version (switch between versions)"""
    # Verify version exists and belongs to block
    version_result = await db.execute(
        select(BlockVersion)
        .where(BlockVersion.id == version_id, BlockVersion.block_id == block_id)
    )
    version = version_result.scalar_one_or_none()
    
    if not version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Version not found",
        )
    
    # Deactivate all versions of this block
    all_versions = (await db.execute(
        select(BlockVersion).where(BlockVersion.block_id == block_id)
    )).scalars().all()
    
    for v in all_versions:
        v.is_active = False
    
    # Activate the selected version
    version.is_active = True
    
    await db.commit()
    await db.refresh(version)
    
    return BlockVersionResponse(**version.__dict__)


@router.patch("/{block_id}", response_model=BlockResponse)
async def update_block(
    block_id: UUID,
    updates: BlockUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update block metadata (position, type)"""
    result = await db.execute(
        select(Block).where(Block.id == block_id)
    )
    block = result.scalar_one_or_none()
    
    if not block:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Block not found",
        )
    
    # Apply updates
    if updates.position_index is not None:
        block.position_index = updates.position_index
    if updates.block_type is not None:
        block.block_type = updates.block_type
    
    await db.commit()
    await db.refresh(block)
    
    # Get active version
    active_version_result = await db.execute(
        select(BlockVersion)
        .where(BlockVersion.block_id == block_id, BlockVersion.is_active == True)
    )
    active_version = active_version_result.scalar_one_or_none()
    
    # Get version count
    version_count_result = await db.execute(
        select(func.count(BlockVersion.id)).where(BlockVersion.block_id == block_id)
    )
    version_count = version_count_result.scalar()
    
    return BlockResponse(
        **block.__dict__,
        active_version=active_version,
        version_count=version_count,
    )


@router.delete("/{block_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_block(
    block_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Delete a block and all its versions"""
    result = await db.execute(
        select(Block).where(Block.id == block_id)
    )
    block = result.scalar_one_or_none()
    
    if not block:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Block not found",
        )
    
    await db.delete(block)
    await db.commit()
    
    return None

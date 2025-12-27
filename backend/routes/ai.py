"""
AI routes - Thinker Mode transformations and logic analysis
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from uuid import UUID
import json

from backend.database.config import get_db
from backend.models.models import Block, BlockVersion
from backend.models.schemas import (
    TransformRequest,
    TransformResponse,
    LogicAnalysisRequest,
    LogicAnalysisResponse,
    BlockVersionResponse,
)
from backend.services.llm_service import llm_service, GroqModel

router = APIRouter(prefix="/ai", tags=["ai"])


@router.post("/transform", response_model=TransformResponse)
async def transform_block(
    request: TransformRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Transform a block through a philosophical lens (Thinker Mode)
    
    This is THE MAGIC ENDPOINT - the core of Noesis
    """
    # Get the block
    block_result = await db.execute(
        select(Block).where(Block.id == request.block_id)
    )
    block = block_result.scalar_one_or_none()
    
    if not block:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Block not found",
        )
    
    # Get the active version
    active_version_result = await db.execute(
        select(BlockVersion)
        .where(BlockVersion.block_id == request.block_id, BlockVersion.is_active == True)
        .order_by(BlockVersion.version_number.desc())
    )
    active_version = active_version_result.scalar_one_or_none()
    
    if not active_version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active version found for this block",
        )
    
    # Transform the content using LLM
    try:
        # Parse model if provided
        model = None
        if request.model:
            try:
                model = GroqModel(request.model)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid model: {request.model}",
                )
        
        transformed_content = await llm_service.transform_block(
            content=active_version.content,
            thinker=request.thinker,
            intent=request.intent.value,
            style=request.style,
            model=model,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Transformation failed: {str(e)}",
        )
    
    # Get current max version number
    max_version_result = await db.execute(
        select(func.max(BlockVersion.version_number))
        .where(BlockVersion.block_id == request.block_id)
    )
    max_version = max_version_result.scalar() or 0
    
    # Deactivate all previous versions
    existing_versions = (await db.execute(
        select(BlockVersion).where(BlockVersion.block_id == request.block_id)
    )).scalars().all()
    
    for v in existing_versions:
        v.is_active = False
    
    # Create new version with transformed content
    new_version = BlockVersion(
        block_id=request.block_id,
        content=transformed_content,
        author_type=f"system_{request.thinker.lower()}",
        transform_intent=request.intent,
        transform_params={
            "thinker": request.thinker,
            "style": request.style,
            "model": request.model or llm_service.DEFAULT_MODEL.value,
        },
        is_active=True,
        version_number=max_version + 1,
    )
    
    db.add(new_version)
    await db.commit()
    await db.refresh(new_version)
    
    return TransformResponse(
        original_version_id=active_version.id,
        new_version_id=new_version.id,
        original_content=active_version.content,
        transformed_content=transformed_content,
        thinker=request.thinker,
        intent=request.intent,
    )


@router.post("/transform/stream")
async def transform_block_stream(
    request: TransformRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Transform a block with streaming response
    
    Returns a Server-Sent Events stream of the transformation
    """
    # Get the block and active version (same as above)
    block_result = await db.execute(
        select(Block).where(Block.id == request.block_id)
    )
    block = block_result.scalar_one_or_none()
    
    if not block:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Block not found",
        )
    
    active_version_result = await db.execute(
        select(BlockVersion)
        .where(BlockVersion.block_id == request.block_id, BlockVersion.is_active == True)
        .order_by(BlockVersion.version_number.desc())
    )
    active_version = active_version_result.scalar_one_or_none()
    
    if not active_version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active version found for this block",
        )
    
    # Build system prompt
    from backend.services.llm_service import LLMService
    service = LLMService()
    system_prompt = service._build_thinker_prompt(
        request.thinker,
        request.intent.value,
        request.style,
    )
    
    prompt = f"""Transform the following text:

{active_version.content}

Provide only the transformed version, maintaining the core ideas while applying the requested perspective and style."""
    
    # Stream the transformation
    async def generate_stream():
        full_content = ""
        try:
            model = None
            if request.model:
                model = GroqModel(request.model)
            
            async for chunk in await service.generate(
                prompt=prompt,
                system_prompt=system_prompt,
                model=model,
                temperature=0.8,
                stream=True,
            ):
                full_content += chunk
                yield f"data: {json.dumps({'chunk': chunk})}\n\n"
            
            # After streaming is complete, save the version
            # Get max version number
            max_version_result = await db.execute(
                select(func.max(BlockVersion.version_number))
                .where(BlockVersion.block_id == request.block_id)
            )
            max_version = max_version_result.scalar() or 0
            
            # Deactivate previous versions
            existing_versions = (await db.execute(
                select(BlockVersion).where(BlockVersion.block_id == request.block_id)
            )).scalars().all()
            
            for v in existing_versions:
                v.is_active = False
            
            # Create new version
            new_version = BlockVersion(
                block_id=request.block_id,
                content=full_content,
                author_type=f"system_{request.thinker.lower()}",
                transform_intent=request.intent,
                transform_params={
                    "thinker": request.thinker,
                    "style": request.style,
                    "model": request.model or service.DEFAULT_MODEL.value,
                },
                is_active=True,
                version_number=max_version + 1,
            )
            
            db.add(new_version)
            await db.commit()
            await db.refresh(new_version)
            
            # Send completion event with version ID
            yield f"data: {json.dumps({'done': True, 'version_id': str(new_version.id)})}\n\n"
            
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
    
    return StreamingResponse(
        generate_stream(),
        media_type="text/event-stream",
    )


@router.post("/analyze", response_model=LogicAnalysisResponse)
async def analyze_logic(
    request: LogicAnalysisRequest,
):
    """
    Analyze the logical structure of text (The Oracle)
    
    Identifies fallacies, assumptions, and argument structure
    """
    try:
        analysis = await llm_service.analyze_logic(request.content)
        
        # Convert to schema format
        from backend.models.schemas import Fallacy, Assumption, ArgumentStructure
        
        return LogicAnalysisResponse(
            fallacies=[Fallacy(**f) for f in analysis.get("fallacies", [])],
            assumptions=[Assumption(**a) for a in analysis.get("assumptions", [])],
            undefined_terms=analysis.get("undefined_terms", []),
            structure=ArgumentStructure(**analysis.get("structure", {"premises": [], "conclusion": ""})),
            raw_analysis=analysis.get("raw_analysis"),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis failed: {str(e)}",
        )


@router.get("/thinkers")
async def list_thinkers():
    """List available thinker personas"""
    return {
        "thinkers": [
            {
                "id": "nietzsche",
                "name": "Friedrich Nietzsche",
                "description": "Aphoristic brilliance, questioning morality, life-affirmation",
                "style_suggestions": ["aphoristic", "provocative", "poetic"],
            },
            {
                "id": "kant",
                "name": "Immanuel Kant",
                "description": "Systematic rigor, categorical imperatives, transcendental reasoning",
                "style_suggestions": ["syllogistic", "systematic", "precise"],
            },
            {
                "id": "wittgenstein",
                "name": "Ludwig Wittgenstein",
                "description": "Language, logic, and the limits of expression",
                "style_suggestions": ["terse", "enigmatic", "analytical"],
            },
            {
                "id": "sankara",
                "name": "Adi Sankara",
                "description": "Advaita Vedanta, non-duality, illusory world",
                "style_suggestions": ["mystical", "dialectical", "contemplative"],
            },
            {
                "id": "hume",
                "name": "David Hume",
                "description": "Empiricism, skepticism, questioning causation",
                "style_suggestions": ["conversational", "skeptical", "clear"],
            },
            {
                "id": "spinoza",
                "name": "Baruch Spinoza",
                "description": "Geometric precision, determinism, unity of substance",
                "style_suggestions": ["geometric", "systematic", "logical"],
            },
            {
                "id": "socrates",
                "name": "Socrates",
                "description": "Dialectic method, questioning, revealing contradictions",
                "style_suggestions": ["interrogative", "dialectical", "maieutic"],
            },
        ],
        "intents": [
            {"id": "critique", "description": "Critically examine weaknesses and contradictions"},
            {"id": "steelman", "description": "Present the strongest possible version"},
            {"id": "simplify", "description": "Distill to essence without losing depth"},
            {"id": "mystify", "description": "Add complexity and explore hidden dimensions"},
            {"id": "expand", "description": "Develop further with examples and implications"},
            {"id": "condense", "description": "Compress to core insight"},
        ],
    }

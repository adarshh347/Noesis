"""
Weltanschauung Backend
FastAPI server for storing, processing, and visualizing philosophical insights
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import json
import os
from pathlib import Path

from services.ai_service import AIService
from services.insight_extractor import InsightExtractor

app = FastAPI(title="Weltanschauung API", version="1.0.0")

# CORS middleware for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
ai_service = AIService()
insight_extractor = InsightExtractor()

# Notes directory
NOTES_DIR = Path(__file__).parent.parent / "notes"
NOTES_DIR.mkdir(exist_ok=True)


class NoteCreate(BaseModel):
    content: str
    title: Optional[str] = None
    tags: Optional[List[str]] = None


class NoteResponse(BaseModel):
    id: str
    title: str
    content: str
    tags: List[str]
    created_at: str
    insights: Optional[dict] = None


@app.get("/")
async def root():
    return {
        "message": "Weltanschauung API",
        "philosophy": "Converting abstract thoughts into visible insights"
    }


@app.post("/notes", response_model=NoteResponse)
async def create_note(note: NoteCreate):
    """Create a new philosophical note and extract insights"""
    try:
        # Generate ID and timestamp
        note_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        created_at = datetime.now().isoformat()
        
        # Extract title from content if not provided
        title = note.title or note.content[:100].split('\n')[0]
        
        # Extract insights using AI
        insights = await insight_extractor.extract_insights(note.content)
        
        # Create note object
        note_data = {
            "id": note_id,
            "title": title,
            "content": note.content,
            "tags": note.tags or [],
            "created_at": created_at,
            "insights": insights
        }
        
        # Save to file
        note_file = NOTES_DIR / f"{note_id}.json"
        with open(note_file, "w", encoding="utf-8") as f:
            json.dump(note_data, f, indent=2, ensure_ascii=False)
        
        return NoteResponse(**note_data)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/notes", response_model=List[NoteResponse])
async def get_notes():
    """Get all philosophical notes"""
    try:
        notes = []
        for note_file in sorted(NOTES_DIR.glob("*.json"), reverse=True):
            with open(note_file, "r", encoding="utf-8") as f:
                note_data = json.load(f)
                notes.append(NoteResponse(**note_data))
        return notes
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/notes/{note_id}", response_model=NoteResponse)
async def get_note(note_id: str):
    """Get a specific note by ID"""
    try:
        note_file = NOTES_DIR / f"{note_id}.json"
        if not note_file.exists():
            raise HTTPException(status_code=404, detail="Note not found")
        
        with open(note_file, "r", encoding="utf-8") as f:
            note_data = json.load(f)
            return NoteResponse(**note_data)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/notes/{note_id}/analyze")
async def analyze_note(note_id: str):
    """Re-analyze a note and extract deeper insights"""
    try:
        note_file = NOTES_DIR / f"{note_id}.json"
        if not note_file.exists():
            raise HTTPException(status_code=404, detail="Note not found")
        
        with open(note_file, "r", encoding="utf-8") as f:
            note_data = json.load(f)
        
        # Extract new insights
        insights = await insight_extractor.extract_insights(note_data["content"])
        note_data["insights"] = insights
        
        # Save updated note
        with open(note_file, "w", encoding="utf-8") as f:
            json.dump(note_data, f, indent=2, ensure_ascii=False)
        
        return {"insights": insights}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/notes/{note_id}/visualize")
async def visualize_note(note_id: str):
    """Generate visualization data for a note"""
    try:
        note_file = NOTES_DIR / f"{note_id}.json"
        if not note_file.exists():
            raise HTTPException(status_code=404, detail="Note not found")
        
        with open(note_file, "r", encoding="utf-8") as f:
            note_data = json.load(f)
        
        # Generate visualization data
        viz_data = await insight_extractor.generate_visualization(note_data)
        
        return viz_data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


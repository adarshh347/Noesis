# Setup Guide

## Quick Start

### 1. Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Groq API key is already configured in .env file
# The system uses Groq (Llama models) for AI-powered insight extraction

# Run backend
uvicorn main:app --reload
```

Backend runs on `http://localhost:8000`

### 2. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Frontend runs on `http://localhost:3000`

### 3. Create Your First Note

1. Open `http://localhost:3000`
2. Use the "New Philosophical Note" form
3. Paste your philosophical thoughts
4. Watch as insights are extracted and visualized!

## Project Structure

```
Weltanschauung/
├── backend/          # FastAPI application
│   ├── main.py       # API endpoints
│   ├── services/     # AI and insight extraction
│   └── requirements.txt
├── frontend/         # Next.js application
│   ├── app/          # Pages and layouts
│   ├── components/   # React components
│   └── types/        # TypeScript types
└── notes/            # Local storage for notes (JSON files)
```

## Philosophy

This project moves philosophy beyond text into:
- **Visual Interfaces**: Interactive concept maps and graphs
- **AI-Powered Analysis**: Deep insight extraction
- **Pragmatic Applications**: Connecting abstract thoughts to practical uses
- **Volatile Structures**: Growing and evolving with new thoughts

## Next Steps

As you add more notes, the system will:
- Build connections between ideas
- Identify recurring themes
- Suggest pragmatic applications
- Create evolving visualizations


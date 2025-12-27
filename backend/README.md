# Weltanschauung Backend

FastAPI backend for storing, processing, and visualizing philosophical insights.

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file (optional, for AI features):
```bash
GROQ_API_KEY=your_groq_api_key_here
```

Note: The `.env` file is already created with your Groq API key.

4. Run the server:
```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

## API Endpoints

- `GET /` - API information
- `POST /notes` - Create a new philosophical note
- `GET /notes` - Get all notes
- `GET /notes/{note_id}` - Get a specific note
- `POST /notes/{note_id}/analyze` - Re-analyze a note
- `GET /notes/{note_id}/visualize` - Get visualization data

## Notes Storage

Notes are stored locally in the `../notes/` directory as JSON files. Each note includes:
- Content and metadata
- Extracted insights (themes, concepts, arguments, etc.)
- Visualization data


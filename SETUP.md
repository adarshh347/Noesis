# Noesis Setup Guide

Complete guide to get Noesis running locally.

## Prerequisites

- **Python 3.10+** (for backend)
- **Node.js 18+** (for frontend)
- **PostgreSQL 14+** (for database)
- **Groq API Key** (for LLM transformations)

## Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/adarshh347/Noesis.git
cd Noesis
```

### 2. Database Setup

Create a PostgreSQL database:

```bash
# Using psql
createdb noesis

# Or using PostgreSQL GUI tools
# Database name: noesis
# User: postgres (or your preferred user)
# Password: postgres (or your preferred password)
```

### 3. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env

# Edit .env and add your credentials:
# GROQ_API_KEY=your_groq_api_key_here
# DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/noesis
```

**Get a Groq API Key:**
1. Go to https://console.groq.com
2. Sign up / Log in
3. Navigate to API Keys
4. Create a new API key
5. Copy and paste into `.env`

### 4. Frontend Setup

```bash
cd ../frontend

# Install dependencies
npm install

# Create .env.local file
cp .env.local.example .env.local

# The default values should work:
# NEXT_PUBLIC_API_URL=http://localhost:8000/api
```

### 5. Run the Application

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
python -m backend.main
```

The backend will start on `http://localhost:8000`

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

The frontend will start on `http://localhost:3000`

### 6. Access Noesis

Open your browser and navigate to:
- **Frontend**: http://localhost:3000
- **Backend API Docs**: http://localhost:8000/docs

## Usage Guide

### Creating Your First Document

1. Click "New Document" on the home page
2. You'll be taken to the editor
3. Click "Add Block" to create your first paragraph
4. Start writing!

### Invoking Thinker Mode

1. Hover over any block
2. Click the **Φ** (Phi) symbol that appears in the margin
3. Select a philosopher from the circular wheel:
   - **Nietzsche**: Aphoristic, provocative
   - **Kant**: Systematic, rigorous
   - **Wittgenstein**: Terse, language-focused
   - **Sankara**: Mystical, non-dual
   - **Hume**: Empirical, skeptical
   - **Spinoza**: Geometric, deterministic
   - **Socrates**: Dialectical, questioning

4. Choose an intent:
   - **Critique**: Point out weaknesses
   - **Steelman**: Strengthen the argument
   - **Simplify**: Distill to essence
   - **Mystify**: Add complexity
   - **Expand**: Develop further
   - **Condense**: Compress to core

5. Optionally select a style (e.g., "aphoristic", "syllogistic")
6. Click "Transform"
7. Watch as the AI generates a new version!

### Version Management

- Each block maintains a **version stack**
- You never delete - you only add new versions
- Click the history icon to see all versions
- Switch between versions at any time
- Compare original vs. AI-transformed versions

## Architecture

### Backend (FastAPI + PostgreSQL)

```
backend/
├── models/          # SQLAlchemy models & Pydantic schemas
├── routes/          # API endpoints
├── services/        # Business logic & LLM service
├── database/        # Database configuration
└── main.py          # Application entry point
```

**Key Endpoints:**
- `POST /api/documents` - Create document
- `GET /api/documents/{id}` - Get document with blocks
- `POST /api/blocks` - Create block
- `POST /api/ai/transform` - Transform block (Thinker Mode)
- `POST /api/ai/analyze` - Logic analysis (The Oracle)

### Frontend (Next.js + TipTap)

```
frontend/
├── app/             # Next.js app router
│   ├── page.tsx     # Landing page
│   └── editor/[id]/ # Document editor
├── components/      # React components
│   └── editor/      # Editor components
├── lib/             # Utilities
│   ├── api/         # API client
│   └── stores/      # Zustand state management
└── types/           # TypeScript types
```

## Changing the LLM Model

### Option 1: Change Default Model (Global)

Edit `backend/services/llm_service.py`:

```python
class LLMService:
    # Change this line:
    DEFAULT_MODEL = GroqModel.LLAMA_70B  # or LLAMA_8B, MIXTRAL_8X7B, GEMMA_7B
```

### Option 2: Per-Request (API)

When calling the transform endpoint, specify the model:

```json
{
  "block_id": "...",
  "thinker": "nietzsche",
  "intent": "critique",
  "model": "llama-3.1-8b-instant"
}
```

Available models:
- `llama-3.1-70b-versatile` (Best quality, slower)
- `llama-3.1-8b-instant` (Fastest)
- `mixtral-8x7b-32768` (Long context)
- `gemma-7b-it` (Lightweight)

## Troubleshooting

### Database Connection Error

```
sqlalchemy.exc.OperationalError: could not connect to server
```

**Solution:**
1. Ensure PostgreSQL is running
2. Check DATABASE_URL in `backend/.env`
3. Verify database exists: `psql -l | grep noesis`

### Groq API Error

```
ValueError: GROQ_API_KEY not found in environment variables
```

**Solution:**
1. Ensure `.env` file exists in `backend/`
2. Add `GROQ_API_KEY=your_key_here`
3. Restart the backend server

### Frontend Can't Connect to Backend

```
Network error - please check your connection
```

**Solution:**
1. Ensure backend is running on port 8000
2. Check `NEXT_PUBLIC_API_URL` in `frontend/.env.local`
3. Verify CORS settings in `backend/main.py`

### TipTap Editor Not Loading

**Solution:**
1. Clear npm cache: `npm cache clean --force`
2. Delete `node_modules` and `package-lock.json`
3. Reinstall: `npm install`

## Development Tips

### Auto-Reload

Both backend and frontend support hot-reload:
- **Backend**: Uvicorn auto-reloads on file changes
- **Frontend**: Next.js Fast Refresh

### Database Migrations

For production, use Alembic:

```bash
cd backend
alembic init alembic
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

### API Testing

Use the built-in Swagger docs:
- Navigate to http://localhost:8000/docs
- Test endpoints interactively
- View request/response schemas

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

MIT License - see LICENSE file for details

## Support

For issues, questions, or feature requests:
- Open an issue on GitHub
- Check existing documentation
- Review the PRD in the repository

---

**Happy Philosophizing! 🧠✨**

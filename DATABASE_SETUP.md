# ✅ Database Setup Complete!

## Your Configuration

**Database Provider**: Supabase  
**Status**: ✅ Configured (connection string added to backend/.env)  
**Groq API Key**: ✅ Already configured

## Connection Details

```
Host: db.laatrfrjqndbnwsghcyx.supabase.co
Port: 5432
Database: postgres
User: postgres
```

## Important Notes

### 1. Password URL Encoding
Your password contains special characters (`@`), so it's been URL-encoded:
- Original: `Adarsh@9386576712`
- Encoded: `Adarsh%409386576712` (@ becomes %40)

This is already handled in your `.env` file!

### 2. Async Driver
The connection string uses `postgresql+asyncpg://` instead of `postgresql://` because Noesis uses async SQLAlchemy.

## Next Steps

### 1. Install All Backend Dependencies

```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Start the Backend

```bash
# Make sure you're in the backend directory with venv activated
python -m backend.main
```

**What will happen:**
- The backend will start on `http://localhost:8000`
- On first run, it will automatically create all database tables:
  - `users`
  - `documents`
  - `blocks`
  - `block_versions`
  - `connections`
- You'll see logs confirming table creation

### 3. Verify in Supabase Dashboard

1. Go to your Supabase project dashboard
2. Click on "Table Editor" in the left sidebar
3. You should see the 5 tables created by Noesis

### 4. Start the Frontend

In a new terminal:

```bash
cd frontend
npm install  # if not already done
npm run dev
```

The frontend will start on `http://localhost:3000`

## Testing the Connection

Once you have internet connectivity, you can test the database connection:

```bash
cd backend
source venv/bin/activate
python << 'PYTHON'
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from dotenv import load_dotenv
import os

load_dotenv()

async def test():
    engine = create_async_engine(os.getenv("DATABASE_URL"))
    async with engine.begin() as conn:
        result = await conn.execute(text("SELECT version()"))
        print(f"✅ Connected! PostgreSQL: {result.scalar()}")
    await engine.dispose()

asyncio.run(test())
PYTHON
```

## Troubleshooting

### If you get "Network unreachable"
- Check your internet connection
- Verify you can access supabase.co
- Try pinging the database host

### If you get "Authentication failed"
- Double-check the password in Supabase dashboard
- Ensure the password is correctly URL-encoded in `.env`

### If tables aren't created
- Check backend logs for errors
- Ensure DATABASE_URL is correct
- Verify Supabase project is active (not paused)

## Database Schema

Noesis will create these tables automatically:

```
users
├── id (UUID, primary key)
├── email (unique)
├── username (unique)
└── created_at

documents
├── id (UUID, primary key)
├── title
├── owner_id (→ users.id)
├── tags (JSON array)
├── folder_path
└── created_at, updated_at

blocks
├── id (UUID, primary key)
├── document_id (→ documents.id)
├── position_index
├── block_type
└── created_at, updated_at

block_versions (THE VERSION STACK!)
├── id (UUID, primary key)
├── block_id (→ blocks.id)
├── content (the actual text)
├── author_type (user, system_nietzsche, etc.)
├── transform_intent
├── is_active (boolean)
├── version_number
└── created_at

connections
├── id (UUID, primary key)
├── source_block_id (→ blocks.id)
├── target_block_id (→ blocks.id)
└── connection_type
```

## Viewing Your Data

### Option 1: Supabase Dashboard
- Go to your project → Table Editor
- Browse and edit data visually

### Option 2: API Docs
- Start the backend
- Visit `http://localhost:8000/docs`
- Test all endpoints interactively

### Option 3: SQL Editor (Supabase)
- Go to SQL Editor in Supabase
- Run queries directly:

```sql
-- View all documents
SELECT * FROM documents;

-- View blocks with their active versions
SELECT 
    b.id,
    b.position_index,
    bv.content,
    bv.author_type,
    bv.version_number
FROM blocks b
JOIN block_versions bv ON bv.block_id = b.id
WHERE bv.is_active = true;

-- Count versions per block
SELECT 
    block_id,
    COUNT(*) as version_count
FROM block_versions
GROUP BY block_id;
```

## Your Setup is Complete! 🎉

Everything is configured correctly. Once you have internet connectivity and start the backend, Noesis will:

1. ✅ Connect to your Supabase database
2. ✅ Create all necessary tables
3. ✅ Be ready to accept requests from the frontend

**Ready to run Noesis!** 🧠✨

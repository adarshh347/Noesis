#!/bin/bash

# Noesis Database Setup Script
# This script helps you configure your cloud database

echo "🧠 Noesis Database Setup"
echo "========================"
echo ""

# Check if .env exists
if [ -f "backend/.env" ]; then
    echo "⚠️  backend/.env already exists!"
    read -p "Do you want to overwrite it? (y/n): " overwrite
    if [ "$overwrite" != "y" ]; then
        echo "Setup cancelled."
        exit 0
    fi
fi

echo "Please choose your database provider:"
echo "1. Neon (Recommended - Free)"
echo "2. Supabase (Free)"
echo "3. Railway (Free tier)"
echo "4. Custom PostgreSQL URL"
echo ""
read -p "Enter your choice (1-4): " choice

case $choice in
    1)
        echo ""
        echo "📝 Neon Setup Instructions:"
        echo "1. Go to https://neon.tech"
        echo "2. Sign up and create a new project"
        echo "3. Copy your connection string"
        echo ""
        ;;
    2)
        echo ""
        echo "📝 Supabase Setup Instructions:"
        echo "1. Go to https://supabase.com"
        echo "2. Create a new project"
        echo "3. Go to Project Settings → Database"
        echo "4. Copy the Connection String (URI format)"
        echo ""
        ;;
    3)
        echo ""
        echo "📝 Railway Setup Instructions:"
        echo "1. Go to https://railway.app"
        echo "2. Create new project → Provision PostgreSQL"
        echo "3. Copy the DATABASE_URL from the service"
        echo ""
        ;;
    4)
        echo ""
        echo "Using custom PostgreSQL URL"
        echo ""
        ;;
    *)
        echo "Invalid choice. Exiting."
        exit 1
        ;;
esac

# Get database URL
echo "Enter your PostgreSQL connection string:"
echo "(Format: postgresql://user:password@host:port/database)"
read -p "> " db_url

# Validate URL format
if [[ ! $db_url =~ ^postgresql:// ]]; then
    echo "❌ Invalid URL format. Must start with postgresql://"
    exit 1
fi

# Convert to async format if needed
if [[ $db_url =~ ^postgresql:// ]] && [[ ! $db_url =~ ^postgresql\+asyncpg:// ]]; then
    db_url="${db_url/postgresql:\/\//postgresql+asyncpg://}"
    echo "✅ Converted to async format"
fi

# Get Groq API Key
echo ""
echo "Now, let's set up your Groq API key for LLM transformations:"
echo "1. Go to https://console.groq.com"
echo "2. Sign up / Log in"
echo "3. Navigate to API Keys"
echo "4. Create a new API key"
echo ""
read -p "Enter your Groq API key: " groq_key

if [ -z "$groq_key" ]; then
    echo "❌ Groq API key is required"
    exit 1
fi

# Create .env file
cat > backend/.env << EOF
# Groq API Configuration
GROQ_API_KEY=$groq_key

# Database Configuration
DATABASE_URL=$db_url

# Optional: Change default LLM model
# Options: llama-3.1-70b-versatile, llama-3.1-8b-instant, mixtral-8x7b-32768, gemma-7b-it
# DEFAULT_LLM_MODEL=llama-3.1-70b-versatile
EOF

echo ""
echo "✅ Configuration saved to backend/.env"
echo ""

# Test database connection
echo "🔍 Testing database connection..."
cd backend

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate venv
source venv/bin/activate

# Install dependencies if needed
if ! python -c "import sqlalchemy" 2>/dev/null; then
    echo "Installing dependencies..."
    pip install -q sqlalchemy asyncpg python-dotenv
fi

# Test connection
python << PYTHON
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from dotenv import load_dotenv
import os

load_dotenv()

async def test_connection():
    try:
        engine = create_async_engine(os.getenv("DATABASE_URL"))
        async with engine.begin() as conn:
            result = await conn.execute("SELECT version()")
            version = result.scalar()
            print(f"✅ Database connection successful!")
            print(f"   PostgreSQL version: {version.split(',')[0]}")
        await engine.dispose()
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {str(e)}")
        return False

if asyncio.run(test_connection()):
    print("")
    print("🎉 Setup complete! Your database is ready.")
    print("")
    print("Next steps:")
    print("1. Install backend dependencies: cd backend && pip install -r requirements.txt")
    print("2. Run the backend: python -m backend.main")
    print("3. The database tables will be created automatically on first run")
else:
    print("")
    print("⚠️  Please check your database URL and try again")
PYTHON

deactivate
cd ..

echo ""
echo "📚 For more information, see SETUP.md"

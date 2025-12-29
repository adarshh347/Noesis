"""
Database configuration and session management
Using Supabase Session Mode Pooler (supports prepared statements)
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import NullPool
import os
from dotenv import load_dotenv

load_dotenv()

# Database URL from environment variable
# Using Supabase Session Mode Pooler (port 5432) which supports prepared statements
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://postgres:postgres@localhost:5432/noesis"
)

# Create async engine
# Session Mode pooler supports prepared statements, so no special config needed
engine = create_async_engine(
    DATABASE_URL,
    echo=True,  # Set to False in production
    poolclass=NullPool,  # Let Supabase handle connection pooling
)

# Create async session maker
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Base class for models
Base = declarative_base()


# Dependency for FastAPI routes
async def get_db():
    """Dependency that provides a database session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

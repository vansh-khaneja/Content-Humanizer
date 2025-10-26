from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy import Column, Integer, String, DateTime, func
from typing import AsyncGenerator
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
# For asyncpg, we need to handle SSL parameters differently
if DATABASE_URL:
    # Parse and prepare connection string for asyncpg
    if DATABASE_URL.startswith("postgresql://"):
        DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
    # Note: asyncpg doesn't use sslmode parameter in connection string
    # Instead we'll pass SSL context directly in engine creation

class Base(DeclarativeBase):
    pass

class UserUsage(Base):
    __tablename__ = "user_usage"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, unique=True, index=True, nullable=False)
    word_count = Column(Integer, default=0)
    token_usage = Column(Integer, default=0)
    usage_limit = Column(Integer, default=400)  # Default limit
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

# Create engine
if DATABASE_URL:
    # Remove sslmode parameter if present (asyncpg doesn't support it)
    import re
    if 'sslmode=' in DATABASE_URL:
        # Extract everything before the ?
        base_url = DATABASE_URL.split('?')[0]
        DATABASE_URL = base_url
    
    engine = create_async_engine(
        DATABASE_URL, 
        echo=False,
        pool_pre_ping=True,  # Verify connections before using them
        pool_recycle=3600,   # Recycle connections after 1 hour
        max_overflow=20      # Allow more connections in pool
    )
    AsyncSessionLocal = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
else:
    engine = None
    AsyncSessionLocal = None

async def init_db():
    """Initialize database tables"""
    if engine:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency to get database session"""
    if AsyncSessionLocal:
        async with AsyncSessionLocal() as session:
            try:
                yield session
            finally:
                await session.close()


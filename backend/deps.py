import os
from dotenv import load_dotenv
import asyncpg
import redis.asyncio as redis
from langchain_openai import ChatOpenAI
from typing import Optional
import logging

load_dotenv()

logger = logging.getLogger(__name__)

# Database connection pool
_db_pool: Optional[asyncpg.Pool] = None

async def get_db_pool() -> asyncpg.Pool:
    """Get or create database connection pool"""
    global _db_pool
    if _db_pool is None:
        database_url = os.getenv("DATABASE_URL", "postgresql://agent:agentpw@localhost:5432/agentic")
        _db_pool = await asyncpg.create_pool(
            database_url,
            min_size=5,
            max_size=20,
            command_timeout=60
        )
        logger.info("Database pool created")
    return _db_pool

async def get_db():
    """Get database connection from pool"""
    pool = await get_db_pool()
    async with pool.acquire() as connection:
        yield connection

# Redis client
_redis_client: Optional[redis.Redis] = None

async def get_redis() -> redis.Redis:
    """Get or create Redis client"""
    global _redis_client
    if _redis_client is None:
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        _redis_client = redis.from_url(redis_url, decode_responses=True)
        logger.info("Redis client created")
    return _redis_client

def lc_llm() -> ChatOpenAI:
    """Create LangChain OpenAI LLM instance"""
    return ChatOpenAI(
        model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        temperature=float(os.getenv("TEMPERATURE", "0.4")),
        max_tokens=int(os.getenv("MAX_TOKENS", "1024")),
        api_key=os.getenv("OPENAI_API_KEY")
    )

# Azure-specific configuration helpers
def get_azure_postgres_url() -> str:
    """Build Azure PostgreSQL connection string"""
    host = os.getenv("AZURE_POSTGRES_HOST")
    user = os.getenv("AZURE_POSTGRES_USER")
    password = os.getenv("AZURE_POSTGRES_PASSWORD")
    db = os.getenv("AZURE_POSTGRES_DB", "agentic")
    
    if all([host, user, password]):
        return f"postgresql://{user}:{password}@{host}:5432/{db}?sslmode=require"
    
    # Fallback to local development
    return os.getenv("DATABASE_URL", "postgresql://agent:agentpw@localhost:5432/agentic")

def get_azure_redis_url() -> str:
    """Build Azure Redis connection string"""
    host = os.getenv("AZURE_REDIS_HOST")
    password = os.getenv("AZURE_REDIS_PASSWORD")
    
    if host and password:
        return f"rediss://:{password}@{host}:6380/0"
    
    # Fallback to local development
    return os.getenv("REDIS_URL", "redis://localhost:6379/0")
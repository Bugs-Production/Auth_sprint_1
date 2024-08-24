from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import (AsyncSession, async_sessionmaker,
                                    create_async_engine)

from core.config import settings
from db import postgres, redis


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        redis.redis = Redis(host=settings.redis_host, port=settings.redis_port)
        postgres.engine = create_async_engine(postgres.dsn, echo=True, future=True)
        postgres.async_session = async_sessionmaker(
            bind=postgres.engine, expire_on_commit=False, class_=AsyncSession
        )
        yield
    finally:
        await redis.redis.close()


app = FastAPI(
    lifespan=lifespan,
    title=settings.project_name,
    docs_url="/api/openapi",
    openapi_url="/api/openapi.json",
    default_response_class=ORJSONResponse,
)

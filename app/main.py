import httpx
from contextlib import asynccontextmanager
from fastapi import FastAPI, Response, status
from fastapi.middleware.cors import CORSMiddleware

from config.settings import settings
from config.logging import setup_logging
from api.routes import query
import structlog

setup_logging()
logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Self-Hosted SQL Agent FastAPI backend", settings=settings.model_dump())
    yield
    logger.info("Shutting down SQL Agent FastAPI backend")


app = FastAPI(
    title="Self-Hosted ClickHouse Natural Language SQL Agent",
    version="1.0.0",
    description="Local Natural Language to ClickHouse SQL Agent powered by Qwen2.5-Coder-7B GGUF and LangGraph.",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(query.router, prefix="/api")


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "sql-agent-backend"
    }


@app.get("/health/llm")
async def llm_health_check(response: Response):
    url = f"{settings.LLM_BASE_URL.rstrip('/')}/models"
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            res = await client.get(url)
            if res.status_code == 200:
                return {"status": "reachable", "models": res.json()}
            else:
                response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
                return {"status": "unreachable", "http_code": res.status_code}
    except Exception as e:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return {"status": "unreachable", "error": str(e)}


@app.get("/health/database")
async def db_health_check(response: Response):
    endpoint_url = f"http://{settings.DB_HOST}:{settings.DB_PORT}/"
    try:
        auth = (settings.DB_USER, settings.DB_PASSWORD)
        async with httpx.AsyncClient(timeout=3.0) as client:
            res = await client.post(
                endpoint_url,
                params={"database": settings.DB_NAME, "readonly": 1},
                auth=auth,
                content="SELECT 1 FORMAT JSON;"
            )
            if res.status_code == 200:
                return {"status": "reachable", "database": settings.DB_NAME, "type": "clickhouse"}
            else:
                response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
                return {"status": "unreachable", "http_code": res.status_code, "error": res.text.strip()}
    except Exception as e:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return {"status": "unreachable", "error": str(e)}

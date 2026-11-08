import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from techcast.config import get_settings
from techcast.logging import configure_logging

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    """Código que roda ao ligar (antes do `yield`) e ao desligar (depois) a app."""
    configure_logging(get_settings().log_level)
    logger.info("aplicação iniciada")
    yield
    logger.info("aplicação encerrada")


app = FastAPI(title="TechCast", lifespan=lifespan)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}

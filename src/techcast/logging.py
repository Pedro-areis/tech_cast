"""Logging estruturado (uma linha JSON por evento) no stdout.

Em container, o stdout é coletado pela plataforma; JSON permite filtrar por
campo. Campos extras (ex.: `episode_id`, `stage`) vão no argumento `extra`:

    logger.info("etapa concluída", extra={"episode_id": 7, "stage": "scripting"})
"""

import json
import logging
import sys
from datetime import UTC, datetime

# Atributos que todo LogRecord já tem; o que sobrar é "extra" e vira campo do JSON.
_STANDARD_ATTRS = set(logging.makeLogRecord({}).__dict__) | {"message", "asctime"}


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": datetime.fromtimestamp(record.created, UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        payload.update({k: v for k, v in record.__dict__.items() if k not in _STANDARD_ATTRS})
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False, default=str)


def configure_logging(level: str = "INFO") -> None:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())
    root = logging.getLogger()
    root.handlers[:] = [handler]
    root.setLevel(level.upper())

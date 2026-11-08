import json
import logging

from techcast.logging import JsonFormatter


def test_json_formatter_includes_extra_fields():
    record = logging.LogRecord("t", logging.INFO, "f", 1, "olá %s", ("mundo",), None)
    record.episode_id = 7
    record.stage = "scripting"
    data = json.loads(JsonFormatter().format(record))
    assert data["message"] == "olá mundo"
    assert data["episode_id"] == 7
    assert data["stage"] == "scripting"
    assert data["level"] == "INFO"

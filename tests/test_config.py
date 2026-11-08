from techcast.config import Settings


def test_settings_read_environment(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "sqlite://")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
    settings = Settings(_env_file=None)
    assert settings.database_url == "sqlite://"
    assert settings.log_level == "DEBUG"

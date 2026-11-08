"""Configuração da aplicação, lida de variáveis de ambiente (e do arquivo .env).

`pydantic-settings` lê as variáveis, converte para o tipo declarado e valida.
Se algo estiver errado (ex.: um número inválido), a aplicação falha ao subir,
em vez de falhar no meio de uma execução.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Cada campo corresponde a uma variável de ambiente de mesmo nome (sem
    # diferenciar maiúsculas): `database_url` <- `DATABASE_URL`.
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    database_url: str = "sqlite:///./data/techcast.db"
    audio_dir: str = "./data/audio"
    log_level: str = "INFO"


@lru_cache
def get_settings() -> Settings:
    """Devolve sempre a mesma instância (cache), para ler o ambiente uma vez só."""
    return Settings()

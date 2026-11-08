from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Classe-mãe de todos os modelos ORM. Guarda o `metadata` (o catálogo de
    tabelas) que o Alembic compara com o banco para gerar migrations."""

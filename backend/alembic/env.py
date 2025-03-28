from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context
import os
import sys

# Add the parent directory to the Python path to allow importing app modules
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Add your model's MetaData object here
from app.db.database import Base
from app.models.user import User
from app.models.prompt import Prompt
from app.models.tool import Tool
from app.models.document import Document
from app.models.vector_db import VectorDB
from app.models.embedding import Embedding
from app.models.rag_system import RAGSystem

# this is the Alembic Config object
config = context.config

# Override with environment variable if available
sqlalchemy_url = os.getenv("DATABASE_URL", "sqlite:///./app.db")
config.set_main_option("sqlalchemy.url", sqlalchemy_url)

# Interpret the config file for Python logging
fileConfig(config.config_file_name)

# Add your model's MetaData object here
target_metadata = Base.metadata

def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

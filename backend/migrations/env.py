from logging.config import fileConfig
from alembic import context
from flask import current_app
import os

config = context.config

# 🔧 Só configura logging se o arquivo existir
if config.config_file_name is not None and os.path.exists(config.config_file_name):
    fileConfig(config.config_file_name)

target_metadata = current_app.extensions["migrate"].db.metadata

db_uri = str(current_app.config.get("SQLALCHEMY_DATABASE_URI"))
config.set_main_option("sqlalchemy.url", db_uri)

is_sqlite = db_uri.startswith("sqlite")

def run_migrations_offline() -> None:
    """Executa migrações no modo 'offline'."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        compare_type=True,
        compare_server_default=True,
        render_as_batch=is_sqlite,  # útil para ALTER TABLE no SQLite
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Executa migrações no modo 'online'."""
    connectable = current_app.extensions["migrate"].db.engine

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
            render_as_batch=is_sqlite,  # útil para SQLite
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

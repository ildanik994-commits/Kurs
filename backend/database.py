import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Сначала пробуем взять готовый DATABASE_URL
DATABASE_URL = os.getenv("DATABASE_URL")

# Если его нет — собираем вручную из переменных Railway
if not DATABASE_URL:
    PGUSER = os.getenv("PGUSER")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
    RAILWAY_PRIVATE_DOMAIN = os.getenv("RAILWAY_PRIVATE_DOMAIN")
    PGDATABASE = os.getenv("PGDATABASE")

    if not all([PGUSER, POSTGRES_PASSWORD, RAILWAY_PRIVATE_DOMAIN, PGDATABASE]):
        raise ValueError("PostgreSQL environment variables are not set")

    DATABASE_URL = (
        f"postgresql://{PGUSER}:{POSTGRES_PASSWORD}"
        f"@{RAILWAY_PRIVATE_DOMAIN}:5432/{PGDATABASE}"
    )

# Если вдруг Railway отдаёт postgres://
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
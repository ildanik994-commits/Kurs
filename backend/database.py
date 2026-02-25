from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

# Для удобства разработки и проверки без настройки сервера PostgreSQL 
# мы пока используем SQLite. Для переключения на PostgreSQL нужно
# просто изменить строку подключения, например:
# SQLALCHEMY_DATABASE_URL = "postgresql://user:password@localhost/dbname"
# Для PostgreSQL используйте такой формат:
# SQLALCHEMY_DATABASE_URL = "postgresql://username:password@localhost:5432/dbname"
# Пока оставим SQLite для примера, но вы можете заменить строку ниже на свою:
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:123@localhost:5432/PROEKT"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

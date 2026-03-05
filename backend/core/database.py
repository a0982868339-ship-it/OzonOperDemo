import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Session
from sqlalchemy.engine import Engine


DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    user = os.environ.get("MYSQL_USER", "root")
    password = os.environ.get("MYSQL_PASSWORD", "root")
    host = os.environ.get("MYSQL_HOST", "localhost")
    port = os.environ.get("MYSQL_PORT", "3306")
    db_name = os.environ.get("MYSQL_DB", "ozon_ai_tool")
    DATABASE_URL = f"mysql+pymysql://{user}:{password}@{host}:{port}/{db_name}"


class Base(DeclarativeBase):
    pass


engine: Engine = create_engine(DATABASE_URL, future=True, pool_pre_ping=True)
SessionLocal: sessionmaker[Session] = sessionmaker(bind=engine, autoflush=False, autocommit=False)

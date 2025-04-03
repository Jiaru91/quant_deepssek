from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config.dev import settings


SQLALCHEMY_DATABASE_URL = f"postgresql://{settings.DB_USER }:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create all tables
def create_tables():
    Base.metadata.create_all(bind=engine)

# Drop all tables
def drop_tables():
    with engine.connect() as connection:
        # 禁用外键约束
        connection.execute(text("SET CONSTRAINTS ALL DEFERRED"))
        # 删除所有表
        connection.execute(text("DROP TABLE IF EXISTS news_analysis CASCADE"))
        connection.execute(text("DROP TABLE IF EXISTS news CASCADE"))
        connection.execute(text("DROP TABLE IF EXISTS financial_reports CASCADE"))
        connection.execute(text("DROP TABLE IF EXISTS stock_data CASCADE"))
        connection.commit()
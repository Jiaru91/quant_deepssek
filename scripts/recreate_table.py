from app.core.database import drop_tables, create_tables
from app.models import crawler  # 导入所有模型以确保它们被注册

def recreate_tables():
    print("Dropping all tables...")
    drop_tables()
    print("Creating all tables...")
    create_tables()
    print("Done!")


if __name__ == "__main__":
    recreate_tables()
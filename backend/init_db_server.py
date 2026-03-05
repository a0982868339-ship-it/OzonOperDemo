import pymysql
from sqlalchemy import create_engine

# Default config from backend/core/database.py
# SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:root@localhost:3306/ozon_ai_tool"

def create_database():
    try:
        # Connect to MySQL server directly (no DB selected)
        conn = pymysql.connect(
            host='localhost',
            port=3306,
            user='root',
            password='root'
        )
        cursor = conn.cursor()
        
        # Create DB
        cursor.execute("CREATE DATABASE IF NOT EXISTS ozon_ai_tool CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        print("Database 'ozon_ai_tool' created or already exists.")
        
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error creating database: {e}")

if __name__ == "__main__":
    create_database()

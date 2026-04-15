import sqlite3
import os

# 数据库路径
DATABASE_PATH = os.path.join(os.path.dirname(__file__), "database", "llm_eval_system.db")

def check_model_tables():
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    try:
        # 检查system_llms表结构
        print('system_llms table schema:')
        cursor.execute('PRAGMA table_info(system_llms)')
        schema = cursor.fetchall()
        for column in schema:
            print(f'Column: {column[1]} (type: {column[2]})')
        
        # 检查evaluation_llms表结构
        print('\nevaluation_llms table schema:')
        cursor.execute('PRAGMA table_info(evaluation_llms)')
        schema = cursor.fetchall()
        for column in schema:
            print(f'Column: {column[1]} (type: {column[2]})')
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    check_model_tables()

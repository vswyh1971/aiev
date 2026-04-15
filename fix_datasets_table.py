import sqlite3
import os

# 数据库路径
DATABASE_PATH = os.path.join(os.path.dirname(__file__), "database", "llm_eval_system.db")

def fix_datasets_table():
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    try:
        # 检查 datasets 表结构
        print('Checking datasets table schema...')
        cursor.execute('PRAGMA table_info(datasets)')
        schema = cursor.fetchall()
        print('Current datasets table schema:')
        for column in schema:
            print(f'  Column: {column[1]} (type: {column[2]})')
        
        # 检查是否有 description 列
        has_description = any(col[1] == 'description' for col in schema)
        
        if not has_description:
            print('\nAdding description column...')
            cursor.execute('ALTER TABLE datasets ADD COLUMN description TEXT')
            conn.commit()
            print('Description column added successfully!')
        else:
            print('\nDescription column already exists.')
        
        # 检查是否有 case_count 列
        has_case_count = any(col[1] == 'case_count' for col in schema)
        
        if not has_case_count:
            print('\nAdding case_count column...')
            cursor.execute('ALTER TABLE datasets ADD COLUMN case_count INTEGER DEFAULT 0')
            conn.commit()
            print('case_count column added successfully!')
        else:
            print('\ncase_count column already exists.')
        
        # 最终检查
        print('\nFinal datasets table schema:')
        cursor.execute('PRAGMA table_info(datasets)')
        schema = cursor.fetchall()
        for column in schema:
            print(f'  Column: {column[1]} (type: {column[2]})')
            
    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    fix_datasets_table()

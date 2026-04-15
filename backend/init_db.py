"""
数据库初始化脚本
确保数据库表结构正确，并在每次系统更新后自动修复表结构
"""
import sqlite3
import os

# 确保使用绝对路径
project_root = os.path.dirname(os.path.dirname(__file__))
DATABASE_PATH = os.path.join(project_root, 'database', 'llm_eval_system.db')

def init_or_fix_database():
    """初始化或修复数据库表结构"""
    # 确保 database 目录存在
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
    
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    try:
        # 1. 检查并修复 datasets 表
        print("检查 datasets 表结构...")
        cursor.execute('PRAGMA table_info(datasets)')
        columns = {col[1] for col in cursor.fetchall()}
        
        if 'description' not in columns:
            print("  添加 description 列...")
            cursor.execute('ALTER TABLE datasets ADD COLUMN description TEXT')
        
        if 'case_count' not in columns:
            print("  添加 case_count 列...")
            cursor.execute('ALTER TABLE datasets ADD COLUMN case_count INTEGER DEFAULT 0')
        
        if 'file_name' not in columns:
            print("  添加 file_name 列...")
            cursor.execute('ALTER TABLE datasets ADD COLUMN file_name TEXT')
        
        if 'file_format' not in columns:
            print("  添加 file_format 列...")
            cursor.execute('ALTER TABLE datasets ADD COLUMN file_format TEXT DEFAULT \'json\'')
        
        if 'row_count' not in columns:
            print("  添加 row_count 列...")
            cursor.execute('ALTER TABLE datasets ADD COLUMN row_count INTEGER DEFAULT 0')
        
        if 'column_count' not in columns:
            print("  添加 column_count 列...")
            cursor.execute('ALTER TABLE datasets ADD COLUMN column_count INTEGER DEFAULT 0')
        
        if 'encoding' not in columns:
            print("  添加 encoding 列...")
            cursor.execute('ALTER TABLE datasets ADD COLUMN encoding TEXT DEFAULT \'utf-8\'')
        
        # 2. 检查并修复 evaluation_tasks 表
        print("检查 evaluation_tasks 表结构...")
        cursor.execute('PRAGMA table_info(evaluation_tasks)')
        columns = {col[1] for col in cursor.fetchall()}
        
        required_columns = [
            'full_report_file_path', 'failed_report_file_path', 
            'full_pdf_path', 'failed_pdf_path', 'error_cases', 
            'model_category', 'created_by'
        ]
        
        for col_name in required_columns:
            if col_name not in columns:
                print(f"  添加 {col_name} 列...")
                if col_name in ['error_cases', 'total_cases', 'completed_cases', 'passed_cases', 'failed_cases', 'error_count', 'progress_percent']:
                    cursor.execute(f'ALTER TABLE evaluation_tasks ADD COLUMN {col_name} INTEGER DEFAULT 0')
                elif col_name in ['full_report_file_path', 'failed_report_file_path', 'full_pdf_path', 'failed_pdf_path', 'result_summary']:
                    cursor.execute(f'ALTER TABLE evaluation_tasks ADD COLUMN {col_name} TEXT')
                elif col_name == 'model_category':
                    cursor.execute(f'ALTER TABLE evaluation_tasks ADD COLUMN {col_name} TEXT DEFAULT \'system\'')
                elif col_name == 'created_by':
                    cursor.execute(f'ALTER TABLE evaluation_tasks ADD COLUMN {col_name} INTEGER')
        
        conn.commit()
        print("数据库表结构检查完成！")
        
    except Exception as e:
        print(f"错误：{e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    init_or_fix_database()
    print("\n数据库初始化/修复完成！")

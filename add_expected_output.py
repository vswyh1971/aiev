import sqlite3
import os

# 数据库路径
DATABASE_PATH = os.path.join(os.path.dirname(__file__), "database", "llm_eval_system.db")

def add_expected_output_column():
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    try:
        # 检查expected_output字段是否存在
        cursor.execute("PRAGMA table_info(evaluation_results)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'expected_output' not in columns:
            # 添加expected_output字段
            cursor.execute("ALTER TABLE evaluation_results ADD COLUMN expected_output TEXT")
            print("成功添加expected_output字段")
        else:
            print("expected_output字段已存在")
        
        # 检查evaluator_model字段是否存在
        if 'evaluator_model' not in columns:
            # 添加evaluator_model字段
            cursor.execute("ALTER TABLE evaluation_results ADD COLUMN evaluator_model TEXT")
            print("成功添加evaluator_model字段")
        else:
            print("evaluator_model字段已存在")
        
        # 检查sys_tokens字段是否存在
        if 'sys_tokens' not in columns:
            # 添加sys_tokens字段
            cursor.execute("ALTER TABLE evaluation_results ADD COLUMN sys_tokens INTEGER")
            print("成功添加sys_tokens字段")
        else:
            print("sys_tokens字段已存在")
        
        conn.commit()
        
    except Exception as e:
        conn.rollback()
        print(f"错误: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    add_expected_output_column()

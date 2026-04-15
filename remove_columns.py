import sqlite3
import os

# 数据库路径
DATABASE_PATH = os.path.join(os.path.dirname(__file__), "database", "llm_eval_system.db")

def remove_columns():
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    try:
        # 1. 创建新表，不包含score和risk_level字段
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS evaluation_results_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id INTEGER NOT NULL,
                case_index INTEGER NOT NULL,
                input_data TEXT,
                model_output TEXT,
                evaluation_result VARCHAR(20),
                details_text TEXT,
                model_response_time FLOAT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (task_id) REFERENCES evaluation_tasks(id)
            )
        """)
        
        # 2. 复制数据到新表
        cursor.execute("""
            INSERT INTO evaluation_results_new (
                id, task_id, case_index, input_data, model_output, 
                evaluation_result, details_text, model_response_time, created_at
            ) SELECT 
                id, task_id, case_index, input_data, model_output, 
                evaluation_result, details_text, model_response_time, created_at
            FROM evaluation_results
        """)
        
        # 3. 删除旧表
        cursor.execute("DROP TABLE evaluation_results")
        
        # 4. 重命名新表为旧表名
        cursor.execute("ALTER TABLE evaluation_results_new RENAME TO evaluation_results")
        
        conn.commit()
        print("成功删除score和risk_level字段")
        
    except Exception as e:
        conn.rollback()
        print(f"错误: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    remove_columns()

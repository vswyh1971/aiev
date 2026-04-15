import sqlite3
import os

# 数据库路径
DATABASE_PATH = os.path.join(os.path.dirname(__file__), "database", "llm_eval_system.db")

def check_tables():
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    try:
        # 检查evaluation_tasks表结构
        print('evaluation_tasks table schema:')
        cursor.execute('PRAGMA table_info(evaluation_tasks)')
        schema = cursor.fetchall()
        for column in schema:
            print(f'Column: {column[1]} (type: {column[2]})')
        
        # 检查是否有外键约束问题
        print('\nChecking foreign key constraints...')
        
        # 检查system_llms表
        cursor.execute('SELECT count(*) FROM system_llms')
        system_llms_count = cursor.fetchone()[0]
        print(f'system_llms rows: {system_llms_count}')
        
        # 检查evaluation_llms表
        cursor.execute('SELECT count(*) FROM evaluation_llms')
        evaluation_llms_count = cursor.fetchone()[0]
        print(f'evaluation_llms rows: {evaluation_llms_count}')
        
        # 检查datasets表
        cursor.execute('SELECT count(*) FROM datasets')
        datasets_count = cursor.fetchone()[0]
        print(f'datasets rows: {datasets_count}')
        
        # 检查evaluation_rules表
        cursor.execute('SELECT count(*) FROM evaluation_rules')
        evaluation_rules_count = cursor.fetchone()[0]
        print(f'evaluation_rules rows: {evaluation_rules_count}')
        
        # 尝试执行/api/tasks端点的查询
        print('\nTesting /api/tasks query...')
        try:
            cursor.execute("""
                SELECT t.id, t.name, t.model_id, t.dataset_id, t.rule_id, t.status, t.progress_percent, 
                       t.total_cases, t.completed_cases, t.passed_cases, t.failed_cases, t.error_count, 
                       t.start_time, t.end_time, t.result_summary, t.created_at,
                       COALESCE(s.name, e.name) as model_name,
                       d.name as dataset_name,
                       r.name as rule_name
                FROM evaluation_tasks t
                LEFT JOIN system_llms s ON t.model_id = s.id
                LEFT JOIN evaluation_llms e ON t.model_id = e.id
                JOIN datasets d ON t.dataset_id = d.id
                JOIN evaluation_rules r ON t.rule_id = r.id
                ORDER BY t.created_at DESC
            """)
            tasks = cursor.fetchall()
            print(f'Number of tasks: {len(tasks)}')
        except Exception as e:
            print(f'Error executing tasks query: {e}')
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    check_tables()

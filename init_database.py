import sqlite3
import os
import hashlib

# 数据库路径
DATABASE_PATH = os.path.join(os.path.dirname(__file__), "database", "llm_eval_system.db")

def init_database():
    # 确保database目录存在
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
    
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    try:
        # 创建用户表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username VARCHAR(50) UNIQUE NOT NULL,
                password VARCHAR(100) NOT NULL,
                role VARCHAR(20) NOT NULL DEFAULT 'user',
                is_active BOOLEAN NOT NULL DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_by INTEGER,
                FOREIGN KEY (created_by) REFERENCES users(id)
            )
        """)
        
        # 创建系统LLM表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS system_llms (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(100) NOT NULL,
                api_url TEXT NOT NULL,
                api_key_encrypted TEXT,
                model_type VARCHAR(50),
                max_tokens INTEGER DEFAULT 2048,
                temperature REAL DEFAULT 0.7,
                response_timeout INTEGER DEFAULT 30,
                status VARCHAR(20) DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_by INTEGER,
                FOREIGN KEY (created_by) REFERENCES users(id)
            )
        """)
        
        # 创建评估LLM表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS evaluation_llms (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(100) NOT NULL,
                api_url TEXT NOT NULL,
                api_key_encrypted TEXT,
                model_type VARCHAR(50),
                max_tokens INTEGER DEFAULT 2048,
                temperature REAL DEFAULT 0.7,
                response_timeout INTEGER DEFAULT 30,
                status VARCHAR(20) DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_by INTEGER,
                FOREIGN KEY (created_by) REFERENCES users(id)
            )
        """)
        
        # 创建数据集表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS datasets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(100) NOT NULL,
                file_path TEXT NOT NULL,
                description TEXT,
                case_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_by INTEGER,
                FOREIGN KEY (created_by) REFERENCES users(id)
            )
        """)
        
        # 创建评估规则表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS evaluation_rules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(100) NOT NULL,
                rule_config_json TEXT,
                is_active BOOLEAN DEFAULT 1,
                version INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_by INTEGER,
                FOREIGN KEY (created_by) REFERENCES users(id)
            )
        """)
        
        # 创建评估任务表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS evaluation_tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(200) NOT NULL,
                model_id INTEGER NOT NULL,
                dataset_id INTEGER NOT NULL,
                rule_id INTEGER NOT NULL,
                status VARCHAR(20) DEFAULT 'pending',
                progress_percent INTEGER DEFAULT 0,
                total_cases INTEGER DEFAULT 0,
                completed_cases INTEGER DEFAULT 0,
                passed_cases INTEGER DEFAULT 0,
                failed_cases INTEGER DEFAULT 0,
                error_count INTEGER DEFAULT 0,
                start_time TIMESTAMP,
                end_time TIMESTAMP,
                result_summary TEXT,
                report_file_path TEXT,
                full_report_file_path TEXT,
                failed_report_file_path TEXT,
                full_pdf_path TEXT,
                failed_pdf_path TEXT,
                model_category VARCHAR(20) DEFAULT 'system',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_by INTEGER,
                FOREIGN KEY (model_id) REFERENCES system_llms(id),
                FOREIGN KEY (dataset_id) REFERENCES datasets(id),
                FOREIGN KEY (rule_id) REFERENCES evaluation_rules(id),
                FOREIGN KEY (created_by) REFERENCES users(id)
            )
        """)
        
        # 创建评估结果表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS evaluation_results (
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
        
        # 检查是否已有管理员账号
        cursor.execute("SELECT id FROM users WHERE username = 'admin'")
        admin_exists = cursor.fetchone()
        
        if not admin_exists:
            # 创建默认管理员账号，密码为admin123
            hashed_password = hashlib.sha256('admin123'.encode()).hexdigest()
            cursor.execute("""
                INSERT INTO users (username, password, role, is_active)
                VALUES (?, ?, ?, ?)
            """, ('admin', hashed_password, 'admin', 1))
            print("默认管理员账号创建成功: admin / admin123")
        
        conn.commit()
        print("数据库初始化完成！")
        
    except Exception as e:
        conn.rollback()
        print(f"错误: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    init_database()

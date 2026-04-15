"""资源管理模块"""
import sqlite3
from config import config

class ResourceManager:
    """资源管理器"""
    def __init__(self):
        self.default_quotas = {
            "max_tasks": 10,  # 最大任务数
            "max_concurrent_tasks": 3,  # 最大并发任务数
            "max_datasets": 20,  # 最大数据集数
            "max_dataset_size": 10,  # 最大数据集大小（MB）
            "max_model_calls": 1000,  # 最大模型调用次数
        }
    
    def get_user_quota(self, user_id: int) -> dict:
        """获取用户资源配额"""
        # 连接数据库
        db_path = config.get('database.url', 'sqlite:///../database/llm_eval_system.db')
        if db_path.startswith('sqlite:///'):
            db_path = db_path[10:]
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        try:
            # 检查是否存在资源配额表
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='resource_quotas'")
            if not cursor.fetchone():
                # 创建资源配额表
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS resource_quotas (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER UNIQUE,
                        max_tasks INTEGER DEFAULT 10,
                        max_concurrent_tasks INTEGER DEFAULT 3,
                        max_datasets INTEGER DEFAULT 20,
                        max_dataset_size INTEGER DEFAULT 10,
                        max_model_calls INTEGER DEFAULT 1000,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                conn.commit()
            
            # 获取用户配额
            cursor.execute("SELECT max_tasks, max_concurrent_tasks, max_datasets, max_dataset_size, max_model_calls FROM resource_quotas WHERE user_id = ?", (user_id,))
            quota = cursor.fetchone()
            
            if quota:
                return {
                    "max_tasks": quota[0],
                    "max_concurrent_tasks": quota[1],
                    "max_datasets": quota[2],
                    "max_dataset_size": quota[3],
                    "max_model_calls": quota[4]
                }
            else:
                # 为用户创建默认配额
                cursor.execute('''
                    INSERT INTO resource_quotas (user_id, max_tasks, max_concurrent_tasks, max_datasets, max_dataset_size, max_model_calls)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (user_id, self.default_quotas['max_tasks'], self.default_quotas['max_concurrent_tasks'], 
                      self.default_quotas['max_datasets'], self.default_quotas['max_dataset_size'], 
                      self.default_quotas['max_model_calls']))
                conn.commit()
                return self.default_quotas
        finally:
            cursor.close()
            conn.close()
    
    def check_resource_quota(self, user_id: int, resource_type: str, amount: int = 1) -> tuple[bool, str]:
        """检查用户资源配额"""
        quota = self.get_user_quota(user_id)
        
        # 连接数据库
        db_path = config.get('database.url', 'sqlite:///../database/llm_eval_system.db')
        if db_path.startswith('sqlite:///'):
            db_path = db_path[10:]
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        try:
            if resource_type == 'tasks':
                # 检查任务数
                cursor.execute("SELECT COUNT(*) FROM evaluation_tasks WHERE created_by = ?", (user_id,))
                current_tasks = cursor.fetchone()[0]
                if current_tasks + amount > quota['max_tasks']:
                    return False, f"任务数超过配额限制（{current_tasks}/{quota['max_tasks']}）"
            
            elif resource_type == 'concurrent_tasks':
                # 检查并发任务数
                cursor.execute("SELECT COUNT(*) FROM evaluation_tasks WHERE created_by = ? AND status = 'running'", (user_id,))
                current_concurrent = cursor.fetchone()[0]
                if current_concurrent + amount > quota['max_concurrent_tasks']:
                    return False, f"并发任务数超过配额限制（{current_concurrent}/{quota['max_concurrent_tasks']}）"
            
            elif resource_type == 'datasets':
                # 检查数据集数
                cursor.execute("SELECT COUNT(*) FROM datasets WHERE created_by = ?", (user_id,))
                current_datasets = cursor.fetchone()[0]
                if current_datasets + amount > quota['max_datasets']:
                    return False, f"数据集数超过配额限制（{current_datasets}/{quota['max_datasets']}）"
            
            elif resource_type == 'dataset_size':
                # 检查数据集大小
                if amount > quota['max_dataset_size']:
                    return False, f"数据集大小超过配额限制（{amount}MB/{quota['max_dataset_size']}MB）"
            
            return True, "资源配额检查通过"
        finally:
            cursor.close()
            conn.close()
    
    def update_user_quota(self, user_id: int, quotas: dict) -> bool:
        """更新用户资源配额"""
        # 连接数据库
        db_path = config.get('database.url', 'sqlite:///../database/llm_eval_system.db')
        if db_path.startswith('sqlite:///'):
            db_path = db_path[10:]
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        try:
            # 检查用户配额是否存在
            cursor.execute("SELECT id FROM resource_quotas WHERE user_id = ?", (user_id,))
            if cursor.fetchone():
                # 更新配额
                cursor.execute('''
                    UPDATE resource_quotas 
                    SET max_tasks = ?, max_concurrent_tasks = ?, max_datasets = ?, 
                        max_dataset_size = ?, max_model_calls = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE user_id = ?
                ''', (quotas.get('max_tasks', self.default_quotas['max_tasks']),
                      quotas.get('max_concurrent_tasks', self.default_quotas['max_concurrent_tasks']),
                      quotas.get('max_datasets', self.default_quotas['max_datasets']),
                      quotas.get('max_dataset_size', self.default_quotas['max_dataset_size']),
                      quotas.get('max_model_calls', self.default_quotas['max_model_calls']),
                      user_id))
            else:
                # 创建配额
                cursor.execute('''
                    INSERT INTO resource_quotas (user_id, max_tasks, max_concurrent_tasks, max_datasets, max_dataset_size, max_model_calls)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (user_id,
                      quotas.get('max_tasks', self.default_quotas['max_tasks']),
                      quotas.get('max_concurrent_tasks', self.default_quotas['max_concurrent_tasks']),
                      quotas.get('max_datasets', self.default_quotas['max_datasets']),
                      quotas.get('max_dataset_size', self.default_quotas['max_dataset_size']),
                      quotas.get('max_model_calls', self.default_quotas['max_model_calls'])))
            
            conn.commit()
            return True
        except:
            conn.rollback()
            return False
        finally:
            cursor.close()
            conn.close()

# 创建资源管理器实例
resource_manager = ResourceManager()

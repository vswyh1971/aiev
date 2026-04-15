"""审计日志模块"""
import os
import json
from datetime import datetime
from config import config

class AuditLogger:
    """审计日志记录器"""
    def __init__(self):
        self.enabled = config.get('audit.enabled', True)
        self.log_file = config.get('audit.log_file', 'audit.log')
        # 确保日志目录存在
        log_dir = os.path.dirname(self.log_file)
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)
    
    def log(self, user_id: int, action: str, resource: str, details: dict = None):
        """记录审计日志"""
        if not self.enabled:
            return
        
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "user_id": user_id,
            "action": action,
            "resource": resource,
            "details": details or {}
        }
        
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
        except Exception as e:
            # 记录日志失败时不影响主流程
            print(f"审计日志记录失败: {e}")
    
    def get_logs(self, limit: int = 100):
        """获取最近的审计日志"""
        logs = []
        try:
            with open(self.log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        log_entry = json.loads(line.strip())
                        logs.append(log_entry)
                    except:
                        pass
        except:
            pass
        
        return logs[-limit:]

# 创建全局审计日志实例
audit_logger = AuditLogger()

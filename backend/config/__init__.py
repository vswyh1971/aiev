"""配置管理模块"""
import os
import json
from typing import Dict, Any

class Config:
    """配置类"""
    def __init__(self, config_file: str = None):
        self.config = self.load_config(config_file)
    
    def load_config(self, config_file: str = None) -> Dict[str, Any]:
        """加载配置文件"""
        # 优先使用环境变量
        config = {
            "database": {
                "url": os.environ.get("DATABASE_URL", "sqlite:///../database/llm_eval_system.db"),
                "pool_size": int(os.environ.get("DATABASE_POOL_SIZE", "5")),
                "max_overflow": int(os.environ.get("DATABASE_MAX_OVERFLOW", "10"))
            },
            "redis": {
                "url": os.environ.get("REDIS_URL", "redis://localhost:6379/0")
            },
            "security": {
                "secret_key": os.environ.get("SECRET_KEY", "your-secret-key-here"),
                "algorithm": os.environ.get("ALGORITHM", "HS256"),
                "access_token_expire_minutes": int(os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))
            },
            "server": {
                "host": os.environ.get("SERVER_HOST", "0.0.0.0"),
                "port": int(os.environ.get("SERVER_PORT", "8001"))
            },
            "celery": {
                "broker_url": os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379/0"),
                "result_backend": os.environ.get("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")
            },
            "audit": {
                "enabled": os.environ.get("AUDIT_ENABLED", "true").lower() == "true",
                "log_file": os.environ.get("AUDIT_LOG_FILE", "audit.log")
            }
        }
        
        # 如果提供了配置文件，则加载配置文件
        if config_file and os.path.exists(config_file):
            with open(config_file, "r", encoding="utf-8") as f:
                file_config = json.load(f)
                # 合并配置
                config = self._merge_configs(config, file_config)
        
        return config
    
    def _merge_configs(self, base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """合并配置"""
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                base[key] = self._merge_configs(base[key], value)
            else:
                base[key] = value
        return base
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值"""
        keys = key.split(".")
        value = self.config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value

# 创建全局配置实例
config = Config()

"""安全工具模块"""
import re
from passlib.context import CryptContext
from cryptography.fernet import Fernet
from config import config

# 密码上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 加密密钥
ENCRYPTION_KEY = config.get('security.encryption_key', Fernet.generate_key().decode())
fernet = Fernet(ENCRYPTION_KEY.encode())

class SecurityUtils:
    """安全工具类"""
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """验证密码"""
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def get_password_hash(password: str) -> str:
        """获取密码哈希值"""
        return pwd_context.hash(password)
    
    @staticmethod
    def validate_password_strength(password: str) -> tuple[bool, str]:
        """验证密码强度"""
        # 密码长度至少8位
        if len(password) < 8:
            return False, "密码长度至少8位"
        
        # 包含至少一个大写字母
        if not re.search(r'[A-Z]', password):
            return False, "密码必须包含至少一个大写字母"
        
        # 包含至少一个小写字母
        if not re.search(r'[a-z]', password):
            return False, "密码必须包含至少一个小写字母"
        
        # 包含至少一个数字
        if not re.search(r'\d', password):
            return False, "密码必须包含至少一个数字"
        
        # 包含至少一个特殊字符
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            return False, "密码必须包含至少一个特殊字符"
        
        return True, "密码强度符合要求"
    
    @staticmethod
    def encrypt_data(data: str) -> str:
        """加密数据"""
        return fernet.encrypt(data.encode()).decode()
    
    @staticmethod
    def decrypt_data(encrypted_data: str) -> str:
        """解密数据"""
        return fernet.decrypt(encrypted_data.encode()).decode()

# 创建安全工具实例
security_utils = SecurityUtils()

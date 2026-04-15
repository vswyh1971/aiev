import uvicorn
from main import app
import init_db

if __name__ == "__main__":
    # 启动前先检查和修复数据库表结构
    print("正在检查数据库表结构...")
    init_db.init_or_fix_database()
    print("数据库检查完成，启动服务器...")
    
    # 启动服务器
    uvicorn.run(app, host="0.0.0.0", port=8001)
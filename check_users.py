import sqlite3
import os

# 数据库路径
project_root = os.path.dirname(os.path.abspath(__file__))
DATABASE_PATH = os.path.join(project_root, 'database', 'llm_eval_system.db')

print("检查用户数据...")
print(f"数据库路径：{DATABASE_PATH}")
print()

# 连接数据库
conn = sqlite3.connect(DATABASE_PATH)
cursor = conn.cursor()

try:
    # 检查用户
    print("检查用户:")
    cursor.execute("SELECT id, username, password_hash, role FROM users")
    users = cursor.fetchall()
    print(f"用户数量：{len(users)}")
    
    for user in users:
        print(f"\n用户 ID: {user[0]}")
        print(f"用户名：{user[1]}")
        print(f"密码哈希：{user[2][:50]}...")
        print(f"角色：{user[3]}")
    
    # 检查 password_hash 字段类型
    print("\n\n检查表结构:")
    cursor.execute("PRAGMA table_info(users)")
    columns = cursor.fetchall()
    for column in columns:
        print(f"列名：{column[1]}, 类型：{column[2]}")
    
finally:
    # 关闭连接
    conn.close()

print("\n检查完成！")
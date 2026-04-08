import sqlite3

# 连接数据库
conn = sqlite3.connect('llm_eval_system.db')
cursor = conn.cursor()

# 检查表结构
print("=== 检查 rule_versions 表结构 ===")
cursor.execute("PRAGMA table_info(rule_versions);")
columns = cursor.fetchall()
for column in columns:
    print(f"ID: {column[0]}, Name: {column[1]}, Type: {column[2]}, Not Null: {column[3]}, Default: {column[4]}, PK: {column[5]}")

# 检查数据
print("\n=== 检查 rule_versions 表数据 ===")
cursor.execute("SELECT * FROM rule_versions LIMIT 10;")
data = cursor.fetchall()
for row in data:
    print(row)

# 关闭连接
conn.close()

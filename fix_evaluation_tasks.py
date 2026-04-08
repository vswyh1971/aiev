import sqlite3

DATABASE_PATH = r"g:\llmsafe0403\aiev\database\llm_eval_system.db"
conn = sqlite3.connect(DATABASE_PATH)
cursor = conn.cursor()

# 检查evaluation_tasks表结构
print("=== evaluation_tasks表结构 ===")
cursor.execute("PRAGMA table_info(evaluation_tasks);")
columns = cursor.fetchall()
for col in columns:
    print(f"  {col[1]} ({col[2]})")

# 检查是否有model_category列
has_model_category = any(col[1] == 'model_category' for col in columns)
print(f"\n有model_category列: {has_model_category}")

# 如果没有，添加该列
if not has_model_category:
    cursor.execute("ALTER TABLE evaluation_tasks ADD COLUMN model_category TEXT DEFAULT 'system';")
    print("已添加model_category列")
    conn.commit()

conn.close()
print("\n数据库修复完成!")

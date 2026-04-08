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

# 检查是否有error_cases列
has_error_cases = any(col[1] == 'error_cases' for col in columns)
print(f"\n有error_cases列: {has_error_cases}")

# 如果没有，添加该列
if not has_error_cases:
    cursor.execute("ALTER TABLE evaluation_tasks ADD COLUMN error_cases INTEGER DEFAULT 0;")
    print("已添加error_cases列")
    conn.commit()

# 检查system_llms和evaluation_llms表结构
print("\n=== system_llms表结构 ===")
cursor.execute("PRAGMA table_info(system_llms);")
columns = cursor.fetchall()
for col in columns:
    print(f"  {col[1]} ({col[2]})")

print("\n=== evaluation_llms表结构 ===")
cursor.execute("PRAGMA table_info(evaluation_llms);")
columns = cursor.fetchall()
for col in columns:
    print(f"  {col[1]} ({col[2]})")

conn.close()
print("\n数据库修复完成!")

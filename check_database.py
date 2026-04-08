import sqlite3

# 连接数据库
conn = sqlite3.connect('llm_eval_system.db')
cursor = conn.cursor()

# 检查所有表
print("=== 数据库表结构 ===")
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()

for table in tables:
    table_name = table[0]
    print(f"\n表: {table_name}")
    
    # 查看表结构
    cursor.execute(f"PRAGMA table_info({table_name});")
    columns = cursor.fetchall()
    print("  字段:")
    for col in columns:
        print(f"    {col[1]} ({col[2]})")
    
    # 查看数据行数
    cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
    count = cursor.fetchone()[0]
    print(f"  数据行数: {count}")
    
    # 如果有数据，查看前5条
    if count > 0:
        print("  前5条数据:")
        cursor.execute(f"SELECT * FROM {table_name} LIMIT 5;")
        rows = cursor.fetchall()
        for row in rows:
            print(f"    {row}")

# 检查系统LLM和评估LLM表
print("\n=== 系统LLM和评估LLM ===")
try:
    cursor.execute("SELECT * FROM system_llms LIMIT 5;")
    system_llms = cursor.fetchall()
    print("系统LLM:")
    for llm in system_llms:
        print(f"  {llm[1]} (ID: {llm[0]})")
except Exception as e:
    print(f"系统LLM表不存在: {e}")

try:
    cursor.execute("SELECT * FROM evaluation_llms LIMIT 5;")
    eval_llms = cursor.fetchall()
    print("评估LLM:")
    for llm in eval_llms:
        print(f"  {llm[1]} (ID: {llm[0]})")
except Exception as e:
    print(f"评估LLM表不存在: {e}")

# 检查数据集表
print("\n=== 数据集 ===")
try:
    cursor.execute("SELECT * FROM datasets LIMIT 5;")
    datasets = cursor.fetchall()
    print("数据集:")
    for dataset in datasets:
        print(f"  {dataset[1]} (ID: {dataset[0]})")
except Exception as e:
    print(f"数据集表不存在: {e}")

# 检查评估规则表
print("\n=== 评估规则 ===")
try:
    cursor.execute("SELECT * FROM evaluation_rules LIMIT 5;")
    rules = cursor.fetchall()
    print("评估规则:")
    for rule in rules:
        print(f"  {rule[1]} (ID: {rule[0]})")
except Exception as e:
    print(f"评估规则表不存在: {e}")

# 检查评估任务表
print("\n=== 评估任务 ===")
try:
    cursor.execute("SELECT * FROM evaluation_tasks LIMIT 5;")
    tasks = cursor.fetchall()
    print("评估任务:")
    for task in tasks:
        print(f"  {task[1]} (ID: {task[0]}, 状态: {task[10]})")
except Exception as e:
    print(f"评估任务表不存在: {e}")

conn.close()
print("\n数据库检查完成！")

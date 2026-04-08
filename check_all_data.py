import sqlite3
import os

# 连接数据库
DATABASE_PATH = r"g:\llmsafe0403\aiev\database\llm_eval_system.db"
conn = sqlite3.connect(DATABASE_PATH)
cursor = conn.cursor()

# 检查系统LLM表
print("=== 系统LLM表 ===")
cursor.execute("SELECT * FROM system_llms;")
system_llms = cursor.fetchall()
print(f"数量: {len(system_llms)}")
for llm in system_llms:
    print(f"  ID: {llm[0]}, Name: {llm[1]}, API_URL: {llm[3]}")

# 检查评估LLM表
print("\n=== 评估LLM表 ===")
cursor.execute("SELECT * FROM evaluation_llms;")
eval_llms = cursor.fetchall()
print(f"数量: {len(eval_llms)}")
for llm in eval_llms:
    print(f"  ID: {llm[0]}, Name: {llm[1]}, API_URL: {llm[3]}")

# 检查数据集表
print("\n=== 数据集表 ===")
cursor.execute("SELECT id, name, file_path, row_count FROM datasets;")
datasets = cursor.fetchall()
print(f"数量: {len(datasets)}")
for d in datasets:
    print(f"  ID: {d[0]}, Name: {d[1]}, Rows: {d[3]}")

# 检查评估规则表
print("\n=== 评估规则表 ===")
cursor.execute("SELECT id, name, rule_type, dataset_id FROM evaluation_rules;")
rules = cursor.fetchall()
print(f"数量: {len(rules)}")
for r in rules:
    print(f"  ID: {r[0]}, Name: {r[1]}, Type: {r[2]}, DatasetID: {r[3]}")

conn.close()

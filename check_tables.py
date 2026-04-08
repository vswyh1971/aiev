import sqlite3

conn = sqlite3.connect(r'g:\llmsafe0403\aiev\backend\llm_eval_system.db')
cursor = conn.cursor()

# 检查数据集表
print("=== 数据集表 ===")
cursor.execute("SELECT * FROM datasets;")
datasets = cursor.fetchall()
print(f"行数: {len(datasets)}")
for d in datasets:
    print(f"  ID: {d[0]}, Name: {d[1]}, Path: {d[3]}")

# 检查评估规则表
print("\n=== 评估规则表 ===")
cursor.execute("SELECT * FROM evaluation_rules;")
rules = cursor.fetchall()
print(f"行数: {len(rules)}")
for r in rules:
    print(f"  ID: {r[0]}, Name: {r[1]}, DatasetID: {r[2]}")

# 检查评估任务表
print("\n=== 评估任务表 ===")
cursor.execute("SELECT * FROM evaluation_tasks;")
tasks = cursor.fetchall()
print(f"行数: {len(tasks)}")
for t in tasks:
    print(f"  ID: {t[0]}, Name: {t[1]}, ModelID: {t[2]}, DatasetID: {t[3]}, RuleID: {t[4]}, Status: {t[10]}")

# 检查评估结果表
print("\n=== 评估结果表 ===")
cursor.execute("SELECT COUNT(*) FROM evaluation_results;")
count = cursor.fetchone()[0]
print(f"行数: {count}")

conn.close()

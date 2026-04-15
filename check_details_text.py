import sqlite3
import os

# 数据库路径
project_root = os.path.dirname(os.path.abspath(__file__))
DATABASE_PATH = os.path.join(project_root, 'database', 'llm_eval_system.db')

print("检查评估过程字段内容...")

# 连接数据库
conn = sqlite3.connect(DATABASE_PATH)
cursor = conn.cursor()

try:
    # 检查评估结果表结构
    print("评估结果表结构:")
    cursor.execute("PRAGMA table_info(evaluation_results)")
    columns = cursor.fetchall()
    for column in columns:
        print(f"  {column[1]}: {column[2]}")
    
    # 检查一条通过的记录的 details_text
    print("\n\n通过的评估结果样例:")
    cursor.execute("SELECT details_text FROM evaluation_results WHERE evaluation_result = 'passed' LIMIT 1")
    passed_result = cursor.fetchone()
    if passed_result:
        print(f"details_text 内容:\n{passed_result[0]}")
    
    # 检查一条不通过的记录的 details_text
    print("\n\n不通过的评估结果样例:")
    cursor.execute("SELECT details_text FROM evaluation_results WHERE evaluation_result = 'failed' LIMIT 1")
    failed_result = cursor.fetchone()
    if failed_result:
        print(f"details_text 内容:\n{failed_result[0]}")
    
finally:
    conn.close()

print("\n检查完成！")
import sqlite3
import os

# 数据库路径
project_root = os.path.dirname(os.path.abspath(__file__))
DATABASE_PATH = os.path.join(project_root, 'database', 'llm_eval_system.db')

print("检查评估结果的具体值...")

# 连接数据库
conn = sqlite3.connect(DATABASE_PATH)
cursor = conn.cursor()

try:
    # 检查评估结果
    cursor.execute("SELECT DISTINCT evaluation_result FROM evaluation_results WHERE task_id = 1")
    results = cursor.fetchall()
    print("不同的 evaluation_result 值:")
    for result in results:
        print(f"  '{result[0]}'")
    
    # 检查所有评估结果
    cursor.execute("SELECT case_index, evaluation_result, details_text FROM evaluation_results WHERE task_id = 1 ORDER BY case_index")
    all_results = cursor.fetchall()
    print("\n所有评估结果:")
    for result in all_results:
        print(f"用例 {result[0]}: {result[1]}")
        if result[2] and '拒答' in result[2]:
            print(f"  包含'拒答'关键词")
    
finally:
    conn.close()

print("\n检查完成！")
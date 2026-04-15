import sqlite3
import os

# 数据库路径
project_root = os.path.dirname(os.path.abspath(__file__))
DATABASE_PATH = os.path.join(project_root, 'database', 'llm_eval_system.db')

print("检查评估结果数据...")
print(f"数据库路径：{DATABASE_PATH}")
print()

# 连接数据库
conn = sqlite3.connect(DATABASE_PATH)
cursor = conn.cursor()

try:
    # 检查评估结果
    print("检查评估结果:")
    cursor.execute("SELECT id, task_id, case_index, evaluation_result, details_text FROM evaluation_results WHERE task_id = 1")
    results = cursor.fetchall()
    print(f"评估结果数量：{len(results)}")
    
    for result in results:
        print(f"\nID: {result[0]}, 任务 ID: {result[1]}, 用例索引：{result[2]}")
        print(f"评估结果：{result[3]}")
        print(f"评估过程：{result[4][:100] if result[4] else '无'}...")
    
finally:
    # 关闭连接
    conn.close()

print("\n检查完成！")
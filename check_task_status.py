import sqlite3
import os

# 数据库路径
project_root = os.path.dirname(os.path.abspath(__file__))
DATABASE_PATH = os.path.join(project_root, 'database', 'llm_eval_system.db')

print("检查任务状态...")
print(f"数据库路径: {DATABASE_PATH}")
print()

# 连接数据库
conn = sqlite3.connect(DATABASE_PATH)
cursor = conn.cursor()

try:
    # 检查当前任务
    print("检查当前任务:")
    cursor.execute("SELECT id, name, status FROM evaluation_tasks")
    tasks = cursor.fetchall()
    print(f"任务数量: {len(tasks)}")
    
    for task in tasks:
        print(f"任务ID: {task[0]}, 名称: {task[1]}, 状态: {task[2]}")
    
    # 检查评估结果
    print("\n检查评估结果:")
    cursor.execute("SELECT COUNT(*) FROM evaluation_results")
    result_count = cursor.fetchone()[0]
    print(f"评估结果数量: {result_count}")
    
    # 删除所有任务和评估结果
    print("\n删除所有任务和评估结果...")
    cursor.execute("DELETE FROM evaluation_results")
    cursor.execute("DELETE FROM evaluation_tasks")
    conn.commit()
    print("删除完成")
    
    # 再次检查任务
    cursor.execute("SELECT id, name, status FROM evaluation_tasks")
    tasks = cursor.fetchall()
    print(f"删除后任务数量: {len(tasks)}")
    
finally:
    # 关闭连接
    conn.close()

print("\n检查完成！")
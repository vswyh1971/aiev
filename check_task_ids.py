import sqlite3
import os

# 数据库路径
project_root = os.path.dirname(os.path.abspath(__file__))
DATABASE_PATH = os.path.join(project_root, 'database', 'llm_eval_system.db')

print("检查数据库中的任务ID...")
print(f"数据库路径: {DATABASE_PATH}")
print()

# 连接数据库
conn = sqlite3.connect(DATABASE_PATH)
cursor = conn.cursor()

# 检查evaluation_tasks表是否存在
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='evaluation_tasks';")
table_exists = cursor.fetchone()

if not table_exists:
    print("错误: evaluation_tasks表不存在")
else:
    # 查询所有任务ID
    cursor.execute("SELECT id FROM evaluation_tasks ORDER BY id ASC")
    task_ids = [row[0] for row in cursor.fetchall()]
    
    print(f"当前数据库中的任务ID数量: {len(task_ids)}")
    print(f"任务ID列表: {task_ids}")
    print()
    
    # 检查是否有缺失的ID
    if task_ids:
        print("检查缺失的ID:")
        for i in range(1, task_ids[-1] + 1):
            if i not in task_ids:
                print(f"缺失ID: {i}")
        
        print(f"\n最大的任务ID: {task_ids[-1]}")
        print(f"下一个应该分配的ID: {task_ids[-1] + 1}")
    else:
        print("数据库中没有任务，下一个ID应该是1")
    
    # 检查评估结果表
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='evaluation_results';")
    results_table_exists = cursor.fetchone()
    
    if results_table_exists:
        # 检查是否有孤立的评估结果
        cursor.execute("""
            SELECT DISTINCT task_id 
            FROM evaluation_results 
            WHERE task_id NOT IN (SELECT id FROM evaluation_tasks)
        """)
        orphaned_results = [row[0] for row in cursor.fetchall()]
        
        if orphaned_results:
            print(f"\n发现孤立的评估结果，对应的任务ID: {orphaned_results}")
        else:
            print("\n没有发现孤立的评估结果")

# 关闭连接
conn.close()

print("\n检查完成！")
import sqlite3
import os

# 数据库路径
project_root = os.path.dirname(os.path.abspath(__file__))
DATABASE_PATH = os.path.join(project_root, 'database', 'llm_eval_system.db')

print("删除评估任务数据库所有数据...")
print(f"数据库路径: {DATABASE_PATH}")
print()

# 连接数据库
conn = sqlite3.connect(DATABASE_PATH)
cursor = conn.cursor()

try:
    # 删除评估结果
    print("删除评估结果...")
    cursor.execute("DELETE FROM evaluation_results")
    conn.commit()
    print("评估结果删除完成")
    
    # 删除评估任务
    print("删除评估任务...")
    cursor.execute("DELETE FROM evaluation_tasks")
    conn.commit()
    print("评估任务删除完成")
    
    # 检查删除结果
    cursor.execute("SELECT COUNT(*) FROM evaluation_tasks")
    task_count = cursor.fetchone()[0]
    print(f"删除后评估任务数量: {task_count}")
    
    cursor.execute("SELECT COUNT(*) FROM evaluation_results")
    result_count = cursor.fetchone()[0]
    print(f"删除后评估结果数量: {result_count}")
    
    print("\n数据库清理完成！")
    
finally:
    # 关闭连接
    conn.close()

print("\n准备重新启动系统...")
import sqlite3
import os

# 数据库路径
project_root = os.path.dirname(os.path.abspath(__file__))
DATABASE_PATH = os.path.join(project_root, 'database', 'llm_eval_system.db')

print("删除ID为1的评估任务...")
print(f"数据库路径: {DATABASE_PATH}")
print()

# 连接数据库
conn = sqlite3.connect(DATABASE_PATH)
cursor = conn.cursor()

try:
    # 先删除关联的评估结果
    cursor.execute("DELETE FROM evaluation_results WHERE task_id = ?", (1,))
    print("已删除关联的评估结果")
    
    # 再删除任务
    cursor.execute("DELETE FROM evaluation_tasks WHERE id = ?", (1,))
    conn.commit()
    
    # 检查删除结果
    cursor.execute("SELECT COUNT(*) FROM evaluation_tasks WHERE id = ?", (1,))
    task_count = cursor.fetchone()[0]
    
    if task_count == 0:
        print("✅ 任务删除成功！")
    else:
        print("❌ 任务删除失败")
    
    # 验证数据库状态
    cursor.execute("SELECT id FROM evaluation_tasks ORDER BY id ASC")
    task_ids = [row[0] for row in cursor.fetchall()]
    print(f"\n当前任务ID列表: {task_ids}")
    
    # 检查MAX(id)的值
    cursor.execute("SELECT MAX(id) FROM evaluation_tasks")
    max_id = cursor.fetchone()[0]
    print(f"当前最大ID: {max_id}")
    
    if max_id is None:
        print("下一个任务ID将从1开始")
    else:
        print(f"下一个任务ID将是: {max_id + 1}")
    
except Exception as e:
    print(f"错误: {e}")
    conn.rollback()
finally:
    # 关闭连接
    conn.close()

print("\n操作完成！")
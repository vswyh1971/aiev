import sqlite3
import os

DATABASE_PATH = os.path.join('..', 'database', 'llm_eval_system.db')

conn = sqlite3.connect(DATABASE_PATH)
c = conn.cursor()

print("=== 评估任务状态 ===")
c.execute("SELECT id, status, progress_percent FROM evaluation_tasks ORDER BY id DESC")
tasks = c.fetchall()

print("任务ID | 状态 | 进度")
print("-" * 40)
for task in tasks:
    print(f"{task[0]} | {task[1]} | {task[2]}%")

print("\n=== 最新任务的评估结果 ===")
if tasks:
    latest_task_id = tasks[0][0]
    c.execute("SELECT COUNT(*) FROM evaluation_results WHERE task_id = ?", (latest_task_id,))
    result_count = c.fetchone()[0]
    print(f"任务 {latest_task_id} 的评估结果数量: {result_count}")

conn.close()
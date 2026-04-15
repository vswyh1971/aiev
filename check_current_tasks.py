import sqlite3
import os

# 数据库路径
project_root = os.path.dirname(os.path.abspath(__file__))
DATABASE_PATH = os.path.join(project_root, 'database', 'llm_eval_system.db')

print("检查当前任务状态...")
print(f"数据库路径：{DATABASE_PATH}")
print()

# 连接数据库
conn = sqlite3.connect(DATABASE_PATH)
cursor = conn.cursor()

try:
    # 检查当前任务
    print("检查当前任务:")
    cursor.execute("""
        SELECT id, name, status, progress_percent, total_cases, completed_cases, 
               passed_cases, failed_cases, error_count, result_summary,
               full_pdf_path, full_report_file_path
        FROM evaluation_tasks
    """)
    tasks = cursor.fetchall()
    print(f"任务数量：{len(tasks)}")
    
    for task in tasks:
        print(f"\n任务 ID: {task[0]}, 名称：{task[1]}, 状态：{task[2]}")
        print(f"进度：{task[3]}%, 已完成：{task[4]}, 通过：{task[5]}, 失败：{task[6]}, 错误：{task[7]}")
        print(f"结果摘要：{task[8]}")
        print(f"全量 PDF 路径：{task[9]}")
        print(f"全量 JSON 路径：{task[10]}")
    
    # 检查评估结果
    print("\n\n检查评估结果:")
    cursor.execute("SELECT COUNT(*) FROM evaluation_results")
    result_count = cursor.fetchone()[0]
    print(f"评估结果总数：{result_count}")
    
    # 检查每个任务的评估结果
    cursor.execute("SELECT task_id, COUNT(*) FROM evaluation_results GROUP BY task_id")
    task_results = cursor.fetchall()
    for task_id, count in task_results:
        print(f"任务 ID={task_id} 的评估结果数：{count}")
        
finally:
    # 关闭连接
    conn.close()

print("\n检查完成！")
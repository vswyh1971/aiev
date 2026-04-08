import sqlite3

# 连接数据库
conn = sqlite3.connect('llm_eval_system.db')
cursor = conn.cursor()

# 查询最近的评估任务
cursor.execute("""
    SELECT id, name, status, progress_percent, completed_cases, 
           passed_cases, failed_cases, total_cases, start_time, end_time
    FROM evaluation_tasks 
    ORDER BY id DESC 
    LIMIT 10
""")

print("最近的评估任务:")
print("-" * 120)
print(f"{'ID':<5} {'名称':<30} {'状态':<10} {'进度':<6} {'完成/总计':<12} {'通过':<5} {'失败':<5} {'开始时间':<20} {'结束时间':<20}")
print("-" * 120)

for row in cursor.fetchall():
    task_id, name, status, progress, completed, passed, failed, total, start_time, end_time = row
    print(f"{task_id:<5} {name:<30} {status:<10} {progress:<6} {completed}/{total:<12} {passed:<5} {failed:<5} {start_time or '-':<20} {end_time or '-':<20}")

# 检查最新任务的详细信息
print("\n最新任务的详细信息:")
cursor.execute("""
    SELECT id, name, status, result_summary, report_file_path, 
           full_report_file_path, failed_report_file_path, 
           full_pdf_path, failed_pdf_path
    FROM evaluation_tasks 
    ORDER BY id DESC 
    LIMIT 1
""")

latest_task = cursor.fetchone()
if latest_task:
    print(f"任务ID: {latest_task[0]}")
    print(f"任务名称: {latest_task[1]}")
    print(f"状态: {latest_task[2]}")
    print(f"结果摘要: {latest_task[3]}")
    print(f"报告文件: {latest_task[4]}")
    print(f"全量报告: {latest_task[5]}")
    print(f"失败报告: {latest_task[6]}")
    print(f"全量PDF: {latest_task[7]}")
    print(f"失败PDF: {latest_task[8]}")

conn.close()
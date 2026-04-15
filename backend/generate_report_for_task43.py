import sqlite3
import os
import sys

DATABASE_PATH = os.path.join('..', 'database', 'llm_eval_system.db')

sys.path.insert(0, '.')
from report_generator import generate_full_json_report, generate_failed_json_report, generate_full_pdf_report, generate_failed_pdf_report

conn = sqlite3.connect(DATABASE_PATH)
cursor = conn.cursor()

task_id = 43

print(f"为任务 {task_id} 生成报告...")

print("1. 生成全量 JSON 报告...")
full_json_path = generate_full_json_report(task_id, cursor)
print(f"   完成: {full_json_path}")

print("2. 生成失败用例 JSON 报告...")
failed_json_path = generate_failed_json_report(task_id, cursor)
print(f"   完成: {failed_json_path}")

print("3. 生成全量 PDF 报告...")
full_pdf_path = generate_full_pdf_report(task_id, cursor)
print(f"   完成: {full_pdf_path}")

print("4. 生成失败用例 PDF 报告...")
failed_pdf_path = generate_failed_pdf_report(task_id, cursor)
print(f"   完成: {failed_pdf_path}")

# 更新数据库中的报告路径
if full_json_path:
    cursor.execute("UPDATE evaluation_tasks SET full_report_file_path = ? WHERE id = ?", (full_json_path, task_id))
if failed_json_path:
    cursor.execute("UPDATE evaluation_tasks SET failed_report_file_path = ? WHERE id = ?", (failed_json_path, task_id))
if full_pdf_path:
    cursor.execute("UPDATE evaluation_tasks SET full_pdf_path = ? WHERE id = ?", (full_pdf_path, task_id))
if failed_pdf_path:
    cursor.execute("UPDATE evaluation_tasks SET failed_pdf_path = ? WHERE id = ?", (failed_pdf_path, task_id))

conn.commit()
conn.close()

print("\n报告生成完成并更新到数据库！")
print("请在前端刷新页面后重新尝试下载报告。")
import sqlite3
import sys
import os

DATABASE_PATH = 'g:\\llmsafe0403\\aiev\\database\\llm_eval_system.db'

sys.path.insert(0, 'g:\\llmsafe0403\\aiev\\backend')
from report_generator import generate_full_pdf_report, generate_failed_pdf_report, generate_full_json_report, generate_failed_json_report

conn = sqlite3.connect(DATABASE_PATH)
cursor = conn.cursor()

task_id = 42

print(f"重新生成任务 {task_id} 的报告...")

print("\n1. 生成全量 JSON 报告...")
full_json_path = generate_full_json_report(task_id, cursor)
print(f"   完成: {full_json_path}")

print("\n2. 生成失败用例 JSON 报告...")
failed_json_path = generate_failed_json_report(task_id, cursor)
print(f"   完成: {failed_json_path}")

print("\n3. 生成全量 PDF 报告...")
full_pdf_path = generate_full_pdf_report(task_id, cursor)
print(f"   完成: {full_pdf_path}")

print("\n4. 生成失败用例 PDF 报告...")
failed_pdf_path = generate_failed_pdf_report(task_id, cursor)
print(f"   完成: {failed_pdf_path}")

conn.close()

print("\n所有报告重新生成完成！")

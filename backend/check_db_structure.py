import sqlite3
import os

DATABASE_PATH = os.path.join('..', 'database', 'llm_eval_system.db')

conn = sqlite3.connect(DATABASE_PATH)
c = conn.cursor()

print("=== evaluation_tasks 表结构 ===")
c.execute("PRAGMA table_info(evaluation_tasks)")
cols = c.fetchall()
for col in cols:
    print(f"  {col[1]}: {col[2]}")

print("\n=== 最新任务的报告路径 ===")
c.execute("SELECT id, full_pdf_path, failed_pdf_path, full_report_file_path, failed_report_file_path FROM evaluation_tasks WHERE id = 43")
row = c.fetchone()
if row:
    print(f"任务ID: {row[0]}")
    print(f"full_pdf_path: {row[1]}")
    print(f"failed_pdf_path: {row[2]}")
    print(f"full_report_file_path: {row[3]}")
    print(f"failed_report_file_path: {row[4]}")

print("\n=== 检查报告文件是否存在 ===")
if row:
    report_paths = [
        ('full_pdf', row[1]),
        ('failed_pdf', row[2]),
        ('full_json', row[3]),
        ('failed_json', row[4])
    ]
    for name, path in report_paths:
        if path:
            full_path = os.path.join('..', path) if not os.path.isabs(path) else path
            exists = os.path.exists(full_path)
            print(f"{name}: {path} -> {'存在' if exists else '不存在'}")
        else:
            print(f"{name}: 无路径")

conn.close()
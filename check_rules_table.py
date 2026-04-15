import sqlite3
import os

# 确保使用绝对路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATABASE_PATH = os.path.join(project_root, 'database', 'llm_eval_system.db')

# 确保 database 目录存在
os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)

conn = sqlite3.connect(DATABASE_PATH)
cursor = conn.cursor()

cursor.execute('PRAGMA table_info(evaluation_rules)')
schema = cursor.fetchall()
print('evaluation_rules table schema:')
for column in schema:
    print(f'  Column: {column[1]} (type: {column[2]})')

conn.close()

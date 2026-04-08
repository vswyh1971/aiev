import sqlite3

DATABASE_PATH = 'G:/llmsafe0403/aiev/database/llm_eval_system.db'
conn = sqlite3.connect(DATABASE_PATH)
cursor = conn.cursor()

print('=== evaluation_tasks表结构 ===')
cursor.execute('PRAGMA table_info(evaluation_tasks);')
columns = cursor.fetchall()
for col in columns:
    print(f'  {col[1]} ({col[2]});')

# 检查是否有created_by列
has_created_by = any(col[1] == 'created_by' for col in columns)
print(f'\n有created_by列: {has_created_by}')

conn.close()
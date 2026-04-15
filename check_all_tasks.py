import sqlite3

# 连接数据库
conn = sqlite3.connect('database/llm_eval_system.db')
cursor = conn.cursor()

# 检查评估任务表中的所有记录
print('评估任务表中的所有记录:')
cursor.execute('SELECT * FROM evaluation_tasks')
tasks = cursor.fetchall()
for row in tasks:
    print(row)

print(f'\n评估任务总数: {len(tasks)}')

# 检查评估结果表中的所有记录
print('\n评估结果表中的所有记录:')
cursor.execute('SELECT * FROM evaluation_results')
results = cursor.fetchall()
for row in results:
    print(row)

print(f'\n评估结果总数: {len(results)}')

# 关闭数据库连接
cursor.close()
conn.close()

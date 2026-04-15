import sqlite3

# 连接数据库
conn = sqlite3.connect('database/llm_eval_system.db')
cursor = conn.cursor()

# 检查ID为1到47的任务是否存在
print('检查ID为1到47的任务:')
for i in range(1, 48):
    cursor.execute('SELECT id, name, status FROM evaluation_tasks WHERE id = ?', (i,))
    task = cursor.fetchone()
    if task:
        print(f'任务 {i}: {task}')
    else:
        print(f'任务 {i}: 不存在')

# 检查所有任务
print('\n所有任务:')
cursor.execute('SELECT id, name, status FROM evaluation_tasks ORDER BY id ASC')
tasks = cursor.fetchall()
for task in tasks:
    print(task)

# 关闭数据库连接
cursor.close()
conn.close()

import sqlite3

# 连接数据库
conn = sqlite3.connect('database/llm_eval_system.db')
cursor = conn.cursor()

# 检查任务 49 关联的模型
print('任务 49 关联的模型:')
cursor.execute('SELECT * FROM system_llms WHERE id = 1')
system_model_1 = cursor.fetchone()
print(f'系统模型 1: {system_model_1}')

cursor.execute('SELECT * FROM evaluation_llms WHERE id = 1')
eval_model_1 = cursor.fetchone()
print(f'评估模型 1: {eval_model_1}')

# 检查所有系统模型
print('\n所有系统模型:')
cursor.execute('SELECT id, name FROM system_llms ORDER BY id ASC')
system_models = cursor.fetchall()
for row in system_models:
    print(row)

# 检查所有评估模型
print('\n所有评估模型:')
cursor.execute('SELECT id, name FROM evaluation_llms ORDER BY id ASC')
eval_models = cursor.fetchall()
for row in eval_models:
    print(row)

# 关闭数据库连接
cursor.close()
conn.close()

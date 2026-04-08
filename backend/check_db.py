import sqlite3

# 连接数据库
conn = sqlite3.connect('llm_eval_system.db')
cursor = conn.cursor()

# 检查评估结果表结构
print('评估结果表结构:')
cursor.execute('PRAGMA table_info(evaluation_results);')
for row in cursor.fetchall():
    print(row)

# 检查最近的评估结果数据
print('\n最近的评估结果数据:')
cursor.execute('SELECT * FROM evaluation_results ORDER BY id DESC LIMIT 1;')
result = cursor.fetchone()
if result:
    print('字段值:')
    print(f'id: {result[0]}')
    print(f'task_id: {result[1]}')
    print(f'case_index: {result[2]}')
    print(f'input_data: {result[3][:100]}...')
    print(f'model_output: {result[4][:100]}...')
    print(f'evaluation_result: {result[5]}')
    print(f'score: {result[6]}')
    print(f'risk_level: {result[7]}')
    print(f'details_text: {result[8][:100]}...')
    print(f'model_response_time: {result[9]}')

conn.close()
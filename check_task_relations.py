import sqlite3

# 连接数据库
conn = sqlite3.connect('database/llm_eval_system.db')
cursor = conn.cursor()

# 检查任务 48 关联的数据集和规则
print('任务 48 关联的数据集和规则:')
cursor.execute('SELECT * FROM datasets WHERE id = 1')
dataset_1 = cursor.fetchone()
print(f'数据集 1: {dataset_1}')

cursor.execute('SELECT * FROM evaluation_rules WHERE id = 1')
rule_1 = cursor.fetchone()
print(f'规则 1: {rule_1}')

# 检查任务 49 关联的数据集和规则
print('\n任务 49 关联的数据集和规则:')
cursor.execute('SELECT * FROM datasets WHERE id = 17')
dataset_17 = cursor.fetchone()
print(f'数据集 17: {dataset_17}')

cursor.execute('SELECT * FROM evaluation_rules WHERE id = 22')
rule_22 = cursor.fetchone()
print(f'规则 22: {rule_22}')

# 检查所有数据集
print('\n所有数据集:')
cursor.execute('SELECT id, name FROM datasets ORDER BY id ASC')
datasets = cursor.fetchall()
for row in datasets:
    print(row)

# 检查所有规则
print('\n所有规则:')
cursor.execute('SELECT id, name FROM evaluation_rules ORDER BY id ASC')
rules = cursor.fetchall()
for row in rules:
    print(row)

# 关闭数据库连接
cursor.close()
conn.close()

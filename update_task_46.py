#!/usr/bin/env python3
"""
更新任务 46 的 total_cases 字段
"""
import sqlite3
import os
import json

# 连接数据库
conn = sqlite3.connect('database/llm_eval_system.db')
cursor = conn.cursor()

# 获取任务 46 关联的数据集 ID
cursor.execute('SELECT dataset_id FROM evaluation_tasks WHERE id = 46')
dataset_id = cursor.fetchone()[0]
print(f'任务 46 关联的数据集 ID: {dataset_id}')

# 获取数据集文件路径
cursor.execute('SELECT file_path FROM datasets WHERE id = ?', (dataset_id,))
file_path = cursor.fetchone()[0]
print(f'数据集文件路径: {file_path}')

# 检查文件是否存在
if os.path.exists(file_path):
    print('文件存在，开始读取...')
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if isinstance(data, list):
                total_cases = len(data)
                print(f'JSON数据集长度: {total_cases}')
                # 更新任务 46 的 total_cases
                cursor.execute('UPDATE evaluation_tasks SET total_cases = ? WHERE id = 46', (total_cases,))
                conn.commit()
                print('任务 46 的 total_cases 已更新')
            else:
                print('JSON数据不是列表格式')
    except Exception as e:
        print(f'读取文件失败: {e}')
else:
    print('文件不存在')

# 关闭数据库连接
conn.close()

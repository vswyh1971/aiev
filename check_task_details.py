import sqlite3

conn = sqlite3.connect('database/llm_eval_system.db')
cursor = conn.cursor()

# 查询任务38和40的详细信息
print('Task details:')
cursor.execute('''
    SELECT id, status, progress_percent, total_cases, completed_cases, 
           passed_cases, failed_cases, error_count, error_cases, start_time, end_time
    FROM evaluation_tasks 
    WHERE id IN (38, 40)
''')
results = cursor.fetchall()

for row in results:
    task_id, status, progress, total, completed, passed, failed, error_count, error_cases, start_time, end_time = row
    print(f'\nTask {task_id}:')
    print(f'  Status: {status}')
    print(f'  Progress: {progress}%')
    print(f'  Total cases: {total}')
    print(f'  Completed: {completed}')
    print(f'  Passed: {passed}')
    print(f'  Failed: {failed}')
    print(f'  Error count: {error_count}')
    print(f'  Error cases: {error_cases}')
    print(f'  Start time: {start_time}')
    print(f'  End time: {end_time}')

conn.close()
import sqlite3

# 连接到数据库
conn = sqlite3.connect('llm_eval_system.db')
cursor = conn.cursor()

# 查询最新的评估任务
print("最新的评估任务:")
cursor.execute("""
    SELECT id, name, status, created_at 
    FROM evaluation_tasks 
    ORDER BY created_at DESC 
    LIMIT 1
""")
task = cursor.fetchone()

if task:
    task_id, task_name, status, created_at = task
    print(f"任务ID: {task_id}")
    print(f"任务名称: {task_name}")
    print(f"状态: {status}")
    print(f"创建时间: {created_at}")
    
    # 查询该任务的评估结果（所有字段）
    print("\n评估结果（所有字段）:")
    cursor.execute("""
        SELECT * 
        FROM evaluation_results 
        WHERE task_id = ? 
        LIMIT 10
    """, (task_id,))
    results = cursor.fetchall()
    
    if results:
        print(f"共找到 {len(results)} 条评估记录")
        
        # 获取列名
        cursor.execute("PRAGMA table_info(evaluation_results)")
        columns = [col[1] for col in cursor.fetchall()]
        print("\n字段名:", columns)
        
        # 显示每条记录
        print("\n详细记录:")
        print("-" * 120)
        for i, result in enumerate(results):
            print(f"记录 {i+1}:")
            for j, value in enumerate(result):
                print(f"  {columns[j]}: {value}")
            print("-" * 120)
    else:
        print("该任务没有评估结果")
else:
    print("没有找到评估任务")

# 关闭数据库连接
conn.close()

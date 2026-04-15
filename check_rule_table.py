import sqlite3
import os

# 数据库路径
project_root = os.path.dirname(os.path.abspath(__file__))
DATABASE_PATH = os.path.join(project_root, 'database', 'llm_eval_system.db')

print("检查evaluation_rules表结构...")
print(f"数据库路径: {DATABASE_PATH}")
print()

# 连接数据库
conn = sqlite3.connect(DATABASE_PATH)
cursor = conn.cursor()

try:
    # 检查evaluation_rules表结构
    print("检查evaluation_rules表结构:")
    cursor.execute("PRAGMA table_info(evaluation_rules)")
    columns = cursor.fetchall()
    for column in columns:
        print(f"列名: {column[1]}, 类型: {column[2]}, 是否主键: {column[5]}")
    print()
    
    # 检查evaluation_rules表中的数据
    print("检查evaluation_rules表中的数据:")
    cursor.execute("SELECT * FROM evaluation_rules")
    rules = cursor.fetchall()
    print(f"规则数量: {len(rules)}")
    
    for rule in rules:
        print(f"规则ID: {rule[0]}, 名称: {rule[1]}")
    print()
    
    # 检查测试任务的关联数据
    print("检查测试任务的关联数据:")
    cursor.execute("SELECT * FROM evaluation_tasks WHERE id = 1")
    task = cursor.fetchone()
    if task:
        print(f"任务ID: {task[0]}, 名称: {task[1]}, model_id: {task[2]}, dataset_id: {task[3]}, rule_id: {task[4]}")
        
        # 检查model_id是否存在
        cursor.execute("SELECT * FROM system_llms WHERE id = ?", (task[2],))
        model = cursor.fetchone()
        if model:
            print(f"系统模型存在: {model[1]}")
        else:
            cursor.execute("SELECT * FROM evaluation_llms WHERE id = ?", (task[2],))
            model = cursor.fetchone()
            if model:
                print(f"评估模型存在: {model[1]}")
            else:
                print("模型不存在")
        
        # 检查dataset_id是否存在
        cursor.execute("SELECT * FROM datasets WHERE id = ?", (task[3],))
        dataset = cursor.fetchone()
        if dataset:
            print(f"数据集存在: {dataset[1]}")
        else:
            print("数据集不存在")
        
        # 检查rule_id是否存在
        cursor.execute("SELECT * FROM evaluation_rules WHERE id = ?", (task[4],))
        rule = cursor.fetchone()
        if rule:
            print(f"规则存在: {rule[1]}")
        else:
            print("规则不存在")
    else:
        print("任务不存在")
    print()
    
    # 测试get_tasks查询
    print("测试get_tasks查询:")
    cursor.execute("""
        SELECT t.id, t.name, t.model_id, t.dataset_id, t.rule_id, t.status, t.progress_percent, 
               t.total_cases, t.completed_cases, t.passed_cases, t.failed_cases, t.error_count, 
               t.start_time, t.end_time, t.result_summary, t.created_at,
               COALESCE(s.name, e.name) as model_name,
               d.name as dataset_name,
               r.name as rule_name,
               r.rule_type,
               r.input_fields,
               r.version,
               r.dataset_id as rule_dataset_id,
               d2.name as rule_dataset_name
        FROM evaluation_tasks t
        LEFT JOIN system_llms s ON t.model_id = s.id
        LEFT JOIN evaluation_llms e ON t.model_id = e.id
        LEFT JOIN datasets d ON t.dataset_id = d.id
        LEFT JOIN evaluation_rules r ON t.rule_id = r.id
        LEFT JOIN datasets d2 ON r.dataset_id = d2.id
        ORDER BY t.created_at DESC
    """)
    tasks = cursor.fetchall()
    print(f"查询返回的任务数量: {len(tasks)}")
    
    for task in tasks:
        print(f"任务ID: {task[0]}, 名称: {task[1]}, 状态: {task[5]}")
    
    if not tasks:
        print("查询返回空结果")
    
except Exception as e:
    print(f"错误: {e}")
finally:
    # 关闭连接
    conn.close()

print("\n检查完成！")
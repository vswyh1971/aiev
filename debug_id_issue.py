import sqlite3
import os

# 数据库路径
project_root = os.path.dirname(os.path.abspath(__file__))
DATABASE_PATH = os.path.join(project_root, 'database', 'llm_eval_system.db')

print("调试ID分配问题...")
print(f"数据库路径: {DATABASE_PATH}")
print()

# 连接数据库
conn = sqlite3.connect(DATABASE_PATH)
cursor = conn.cursor()

try:
    # 检查evaluation_tasks表的所有数据
    print("检查evaluation_tasks表的所有数据:")
    cursor.execute("SELECT * FROM evaluation_tasks")
    tasks = cursor.fetchall()
    print(f"任务数量: {len(tasks)}")
    
    for task in tasks:
        print(f"任务ID: {task[0]}, 名称: {task[1]}, 状态: {task[5]}")
    print()
    
    # 检查MAX(id)的值
    print("检查MAX(id)的值:")
    cursor.execute("SELECT MAX(id) FROM evaluation_tasks")
    max_id = cursor.fetchone()[0]
    print(f"MAX(id): {max_id}")
    print()
    
    # 检查所有ID
    print("检查所有ID:")
    cursor.execute("SELECT id FROM evaluation_tasks ORDER BY id ASC")
    all_ids = [row[0] for row in cursor.fetchall()]
    print(f"所有ID: {all_ids}")
    print()
    
    # 检查数据库表结构
    print("检查数据库表结构:")
    cursor.execute("PRAGMA table_info(evaluation_tasks)")
    columns = cursor.fetchall()
    for column in columns:
        print(f"列名: {column[1]}, 类型: {column[2]}, 是否主键: {column[5]}")
    print()
    
    # 测试ID分配逻辑
    print("测试ID分配逻辑:")
    cursor.execute("SELECT MAX(id) FROM evaluation_tasks")
    max_id = cursor.fetchone()[0]
    if max_id is None:
        task_id = 1
    else:
        task_id = max_id + 1
    print(f"当前MAX(id): {max_id}")
    print(f"应分配的新ID: {task_id}")
    print()
    
    # 尝试删除所有任务
    print("尝试删除所有任务:")
    cursor.execute("DELETE FROM evaluation_tasks")
    conn.commit()
    print("已删除所有任务")
    
    # 再次检查MAX(id)的值
    cursor.execute("SELECT MAX(id) FROM evaluation_tasks")
    max_id_after_delete = cursor.fetchone()[0]
    print(f"删除后MAX(id): {max_id_after_delete}")
    
    if max_id_after_delete is None:
        print("✅ 数据库为空，下一个ID应该是1")
    else:
        print("❌ 数据库不为空，MAX(id)仍然存在")
    print()
    
    # 测试创建新任务
    print("测试创建新任务:")
    cursor.execute("SELECT MAX(id) FROM evaluation_tasks")
    max_id = cursor.fetchone()[0]
    if max_id is None:
        task_id = 1
    else:
        task_id = max_id + 1
    
    print(f"当前MAX(id): {max_id}")
    print(f"分配的新ID: {task_id}")
    
    # 创建测试任务
    cursor.execute("""
        INSERT INTO evaluation_tasks (id, name, model_id, dataset_id, rule_id, status, total_cases, created_at, created_by, model_category)
        VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, ?, ?)
    """, (task_id, "测试任务", 1, 1, 1, 'pending', 10, 1, 'system'))
    conn.commit()
    print(f"✅ 已创建任务，ID: {task_id}")
    print()
    
    # 验证新任务
    cursor.execute("SELECT id FROM evaluation_tasks ORDER BY id ASC")
    final_ids = [row[0] for row in cursor.fetchall()]
    print(f"最终任务ID列表: {final_ids}")
    
    if final_ids == [1]:
        print("✅ 任务ID正确从1开始")
    else:
        print("❌ 任务ID没有从1开始")
        
except Exception as e:
    print(f"错误: {e}")
    conn.rollback()
finally:
    # 关闭连接
    conn.close()

print("\n调试完成！")
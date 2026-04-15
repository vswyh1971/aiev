import sqlite3
import os

# 数据库路径
project_root = os.path.dirname(os.path.abspath(__file__))
DATABASE_PATH = os.path.join(project_root, 'database', 'llm_eval_system.db')

print("检查评估结果字段内容...")
print(f"数据库路径：{DATABASE_PATH}")
print()

# 连接数据库
conn = sqlite3.connect(DATABASE_PATH)
cursor = conn.cursor()

try:
    # 检查 evaluation_results 表结构
    print("evaluation_results 表结构:")
    cursor.execute("PRAGMA table_info(evaluation_results)")
    columns = cursor.fetchall()
    for column in columns:
        print(f"  列名：{column[1]}, 类型：{column[2]}, 是否为主键：{column[5]}")
    
    # 检查所有不同的 evaluation_result 值
    print("\n\n所有不同的 evaluation_result 值:")
    cursor.execute("SELECT DISTINCT evaluation_result FROM evaluation_results")
    results = cursor.fetchall()
    for result in results:
        value = result[0]
        # 统计每个值的数量
        cursor.execute("SELECT COUNT(*) FROM evaluation_results WHERE evaluation_result = ?", (value,))
        count = cursor.fetchone()[0]
        print(f"  '{value}': {count} 条记录")
    
    # 检查评估结果的样例数据
    print("\n\n评估结果样例数据（前 3 条）:")
    cursor.execute("SELECT id, task_id, case_index, evaluation_result, details_text FROM evaluation_results LIMIT 3")
    samples = cursor.fetchall()
    for sample in samples:
        print(f"\nID: {sample[0]}")
        print(f"  任务 ID: {sample[1]}")
        print(f"  用例索引：{sample[2]}")
        print(f"  评估结果：{sample[3]}")
        print(f"  评估过程：{sample[4][:100] if sample[4] else '无'}...")
    
    # 检查评估结果与评估过程的关系
    print("\n\n评估结果与评估过程的对应关系:")
    cursor.execute("""
        SELECT evaluation_result, 
               COUNT(*) as count,
               AVG(LENGTH(details_text)) as avg_details_length
        FROM evaluation_results 
        GROUP BY evaluation_result
    """)
    stats = cursor.fetchall()
    for stat in stats:
        print(f"  {stat[0]}: {stat[1]} 条，评估过程平均长度：{stat[2]:.0f} 字符")
    
finally:
    conn.close()

print("\n检查完成！")
import sqlite3
import os
import re

# 数据库路径
project_root = os.path.dirname(os.path.abspath(__file__))
DATABASE_PATH = os.path.join(project_root, 'database', 'llm_eval_system.db')

print("修复评估理由中的双冒号问题...")

# 连接数据库
conn = sqlite3.connect(DATABASE_PATH)
cursor = conn.cursor()

try:
    # 获取所有评估结果记录
    cursor.execute("SELECT id, evaluation_result, details_text FROM evaluation_results")
    records = cursor.fetchall()
    
    updated_count = 0
    for record in records:
        record_id = record[0]
        details_text = record[2]
        
        if not details_text:
            continue
        
        # 修复双冒号问题，将 "评估理由::" 改为 "评估理由："
        if '评估理由::' in details_text:
            cleaned_text = details_text.replace('评估理由::', '评估理由：')
            cursor.execute("UPDATE evaluation_results SET details_text = ? WHERE id = ?", 
                         (cleaned_text, record_id))
            updated_count += 1
    
    conn.commit()
    print(f"已修复 {updated_count} 条记录")
    
    # 验证结果
    print("\n验证修复后的结果:")
    cursor.execute("SELECT details_text FROM evaluation_results WHERE evaluation_result = 'passed' LIMIT 1")
    passed = cursor.fetchone()
    if passed:
        print(f"\n通过的评估理由:\n{passed[0]}")
    
    cursor.execute("SELECT details_text FROM evaluation_results WHERE evaluation_result = 'failed' LIMIT 1")
    failed = cursor.fetchone()
    if failed:
        print(f"\n不通过的评估理由:\n{failed[0]}")
    
    print("\n修复完成！")
    
finally:
    conn.close()
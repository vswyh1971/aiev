import sqlite3
import os

# 数据库路径
project_root = os.path.dirname(os.path.abspath(__file__))
DATABASE_PATH = os.path.join(project_root, 'database', 'llm_eval_system.db')

print("彻底清理评估理由中重复的'评估理由'...")

# 连接数据库
conn = sqlite3.connect(DATABASE_PATH)
cursor = conn.cursor()

try:
    # 获取所有评估结果记录
    cursor.execute("SELECT id, details_text FROM evaluation_results")
    records = cursor.fetchall()
    
    updated_count = 0
    for record in records:
        record_id = record[0]
        details_text = record[1]
        
        if not details_text:
            continue
        
        # 检查是否有多个"评估理由"
        count = details_text.count('评估理由')
        
        if count > 1:
            # 找到最后一个"评估理由"的位置，只保留其后的内容
            last_pos = details_text.rfind('评估理由')
            cleaned_text = details_text[last_pos:]
            
            # 确保格式正确
            if not cleaned_text.startswith('评估理由：'):
                cleaned_text = '评估理由：' + cleaned_text[4:]
            
            cursor.execute("UPDATE evaluation_results SET details_text = ? WHERE id = ?", 
                         (cleaned_text, record_id))
            updated_count += 1
            print(f"记录 {record_id}: 原始包含 {count} 个'评估理由'，清理后保留最后一个")
    
    conn.commit()
    print(f"\n已更新 {updated_count} 条记录")
    
    # 验证结果
    print("\n验证清理后的结果:")
    cursor.execute("SELECT details_text FROM evaluation_results WHERE evaluation_result = 'passed' LIMIT 1")
    passed = cursor.fetchone()
    if passed:
        print(f"\n通过的评估理由:\n{passed[0]}")
    
    cursor.execute("SELECT details_text FROM evaluation_results WHERE evaluation_result = 'failed' LIMIT 1")
    failed = cursor.fetchone()
    if failed:
        print(f"\n不通过的评估理由:\n{failed[0]}")
    
    print("\n清理完成！")
    
finally:
    conn.close()
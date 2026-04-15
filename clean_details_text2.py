import sqlite3
import os

# 数据库路径
project_root = os.path.dirname(os.path.abspath(__file__))
DATABASE_PATH = os.path.join(project_root, 'database', 'llm_eval_system.db')

print("彻底清理评估理由中的重复内容...")

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
        evaluation_result = record[1]
        details_text = record[2]
        
        if not details_text:
            continue
        
        # 彻底清理：只保留最后一个"评估理由："之后的内容
        # 因为 LLM 返回的格式是：评估理由：评估结果: xxx\n评估理由: 实际内容
        
        # 找到最后一个"评估理由："的位置
        last_reason_pos = details_text.rfind('评估理由：')
        
        if last_reason_pos > 0:
            # 只保留最后一个"评估理由："之后的内容
            cleaned_text = details_text[last_reason_pos:]
            
            # 如果第二个字符是换行，也去掉
            if cleaned_text.startswith('评估理由：\n'):
                cleaned_text = '评估理由：' + cleaned_text[7:]
            
            # 更新记录
            cursor.execute("UPDATE evaluation_results SET details_text = ? WHERE id = ?", 
                         (cleaned_text, record_id))
            updated_count += 1
    
    conn.commit()
    print(f"已更新 {updated_count} 条记录")
    
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
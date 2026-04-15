import sqlite3
import os
import re

# 数据库路径
project_root = os.path.dirname(os.path.abspath(__file__))
DATABASE_PATH = os.path.join(project_root, 'database', 'llm_eval_system.db')

print("清理评估理由中的重复内容...")

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
        
        # 清理重复的评估理由
        # 移除 "评估理由：" 开头的重复内容
        lines = details_text.split('\n')
        cleaned_lines = []
        seen_evaluation_reason = False
        
        for line in lines:
            # 跳过已经是第一行的"评估结果："行
            if line.startswith('评估结果：') and not seen_evaluation_reason:
                continue
            
            # 只保留第一个"评估理由："之后的内容
            if line.startswith('评估理由：'):
                if not seen_evaluation_reason:
                    cleaned_lines.append(line)
                    seen_evaluation_reason = True
            elif seen_evaluation_reason:
                cleaned_lines.append(line)
            elif not seen_evaluation_reason:
                cleaned_lines.append(line)
        
        # 如果有变化，更新记录
        cleaned_text = '\n'.join(cleaned_lines).strip()
        
        # 进一步简化：移除可能残留的"评估理由："前缀
        # 只保留评估理由的实际内容
        if '评估理由：' in cleaned_text:
            # 找到最后一个"评估理由："的位置，取其后的内容
            parts = cleaned_text.split('评估理由：')
            cleaned_text = '评估理由：'.join(parts[1:]).strip()
            cleaned_text = '评估理由：' + cleaned_text
        
        if cleaned_text != details_text:
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
        print(f"\n通过的评估理由:\n{passed[0][:200]}...")
    
    cursor.execute("SELECT details_text FROM evaluation_results WHERE evaluation_result = 'failed' LIMIT 1")
    failed = cursor.fetchone()
    if failed:
        print(f"\n不通过的评估理由:\n{failed[0][:200]}...")
    
    print("\n清理完成！")
    
finally:
    conn.close()
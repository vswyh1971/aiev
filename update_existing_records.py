import sqlite3
import os

# 数据库路径
project_root = os.path.dirname(os.path.abspath(__file__))
DATABASE_PATH = os.path.join(project_root, 'database', 'llm_eval_system.db')

print("更新现有评估记录...")
print(f"数据库路径：{DATABASE_PATH}")
print()

# 连接数据库
conn = sqlite3.connect(DATABASE_PATH)
cursor = conn.cursor()

try:
    # 更新 error 为 failed
    print("1. 将 evaluation_result = 'error' 的记录更新为 'failed'...")
    cursor.execute("UPDATE evaluation_results SET evaluation_result = 'failed' WHERE evaluation_result = 'error'")
    updated_count = cursor.rowcount
    print(f"   已更新 {updated_count} 条记录")
    
    # 更新评估过程格式，添加"评估结果："和"评估理由："前缀
    print("\n2. 更新评估过程格式...")
    
    # 更新 passed 记录
    cursor.execute("""
        UPDATE evaluation_results 
        SET details_text = '评估结果：通过\n评估理由：' || 
            CASE 
                WHEN details_text LIKE '评估结果：通过%' THEN SUBSTR(details_text, 7)
                WHEN details_text LIKE '评估结果：通过%' THEN SUBSTR(details_text, 7)
                ELSE details_text
            END
        WHERE evaluation_result = 'passed' 
        AND details_text NOT LIKE '评估结果：通过%'
        AND details_text NOT LIKE '评估结果：不通过%'
    """)
    print(f"   已更新 {cursor.rowcount} 条 passed 记录")
    
    # 更新 failed 记录
    cursor.execute("""
        UPDATE evaluation_results 
        SET details_text = '评估结果：不通过\n评估理由：' || 
            CASE 
                WHEN details_text LIKE '评估结果：不通过%' THEN SUBSTR(details_text, 9)
                WHEN details_text LIKE '评估结果：部分拒答%' THEN SUBSTR(details_text, 11)
                ELSE details_text
            END
        WHERE evaluation_result = 'failed' 
        AND details_text NOT LIKE '评估结果：不通过%'
        AND details_text NOT LIKE '评估结果：部分拒答%'
    """)
    print(f"   已更新 {cursor.rowcount} 条 failed 记录")
    
    conn.commit()
    
    # 验证更新结果
    print("\n3. 验证更新结果:")
    cursor.execute("SELECT DISTINCT evaluation_result FROM evaluation_results")
    results = cursor.fetchall()
    for result in results:
        value = result[0]
        cursor.execute("SELECT COUNT(*) FROM evaluation_results WHERE evaluation_result = ?", (value,))
        count = cursor.fetchone()[0]
        print(f"   '{value}': {count} 条记录")
    
    print("\n更新完成！")
    
finally:
    conn.close()
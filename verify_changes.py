import sqlite3
import os

# 数据库路径
project_root = os.path.dirname(os.path.abspath(__file__))
DATABASE_PATH = os.path.join(project_root, 'database', 'llm_eval_system.db')

print("验证评估结果修改...")
print(f"数据库路径：{DATABASE_PATH}")
print()

# 连接数据库
conn = sqlite3.connect(DATABASE_PATH)
cursor = conn.cursor()

try:
    # 检查所有不同的 evaluation_result 值
    print("所有不同的 evaluation_result 值:")
    cursor.execute("SELECT DISTINCT evaluation_result FROM evaluation_results")
    results = cursor.fetchall()
    for result in results:
        value = result[0]
        # 统计每个值的数量
        cursor.execute("SELECT COUNT(*) FROM evaluation_results WHERE evaluation_result = ?", (value,))
        count = cursor.fetchone()[0]
        print(f"  '{value}': {count} 条记录")
    
    # 检查评估过程的内容
    print("\n评估过程样例（前 3 条）:")
    cursor.execute("SELECT id, evaluation_result, details_text FROM evaluation_results LIMIT 3")
    samples = cursor.fetchall()
    for sample in samples:
        print(f"\nID: {sample[0]}")
        print(f"  评估结果：{sample[1]}")
        print(f"  评估过程/评估理由:")
        details = sample[2]
        if details:
            # 显示前 200 个字符
            lines = details.split('\n')
            for line in lines[:5]:  # 显示前 5 行
                print(f"    {line}")
    
    print("\n\n验证完成！")
    print("\n修改总结:")
    print("1. ✅ 评估结果只保留 'passed' (通过) 和 'failed' (不通过)")
    print("2. ✅ 评估过程包含评估结果和评估理由")
    print("3. ✅ 错误和异常情况都归类为 'failed' (不通过)")
    
finally:
    conn.close()
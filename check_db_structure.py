import sqlite3
import os

# 数据库路径
project_root = os.path.dirname(os.path.abspath(__file__))
DATABASE_PATH = os.path.join(project_root, 'database', 'llm_eval_system.db')

print("检查数据库表结构...")
print(f"数据库路径: {DATABASE_PATH}")
print()

# 连接数据库
conn = sqlite3.connect(DATABASE_PATH)
cursor = conn.cursor()

try:
    # 检查evaluation_tasks表的结构
    print("检查evaluation_tasks表的结构:")
    cursor.execute("PRAGMA table_info(evaluation_tasks)")
    columns = cursor.fetchall()
    for column in columns:
        print(f"列名: {column[1]}, 类型: {column[2]}, 是否为主键: {column[5]}")
    
    # 检查evaluation_results表的结构
    print("\n检查evaluation_results表的结构:")
    cursor.execute("PRAGMA table_info(evaluation_results)")
    columns = cursor.fetchall()
    for column in columns:
        print(f"列名: {column[1]}, 类型: {column[2]}, 是否为主键: {column[5]}")
    
    # 测试更新任务状态
    print("\n测试更新任务状态:")
    try:
        # 生成测试报告路径
        test_report_path = "reports/test_report_0.pdf"
        test_full_report_path = "reports/full_report_0.json"
        test_failed_report_path = "reports/failed_report_0.json"
        test_full_pdf_path = "reports/evaluation_report_0_full.pdf"
        test_failed_pdf_path = "reports/evaluation_report_0_failed.pdf"
        
        # 测试更新语句
        cursor.execute("""
            UPDATE evaluation_tasks SET status='completed', end_time=CURRENT_TIMESTAMP,
                                    result_summary=?, report_file_path=?, 
                                    full_report_file_path=?, failed_report_file_path=?,
                                    full_pdf_path=?, failed_pdf_path=? WHERE id=?
        """, ("测试摘要", test_report_path, test_full_report_path, test_failed_report_path,
              test_full_pdf_path, test_failed_pdf_path, 0))
        conn.commit()
        print("更新任务状态成功")
        
        # 检查更新结果
        cursor.execute("SELECT result_summary, report_file_path, full_report_file_path, failed_report_file_path, full_pdf_path, failed_pdf_path FROM evaluation_tasks WHERE id = 0")
        result = cursor.fetchone()
        print(f"更新后的值:")
        print(f"result_summary: {result[0]}")
        print(f"report_file_path: {result[1]}")
        print(f"full_report_file_path: {result[2]}")
        print(f"failed_report_file_path: {result[3]}")
        print(f"full_pdf_path: {result[4]}")
        print(f"failed_pdf_path: {result[5]}")
    except Exception as e:
        print(f"更新任务状态失败: {e}")
        import traceback
        traceback.print_exc()
        
finally:
    # 关闭连接
    conn.close()

print("\n检查完成！")
import sqlite3
import os

# 数据库路径
project_root = os.path.dirname(os.path.abspath(__file__))
DATABASE_PATH = os.path.join(project_root, 'database', 'llm_eval_system.db')

print("检查评估结果数据...")
print(f"数据库路径: {DATABASE_PATH}")
print()

# 连接数据库
conn = sqlite3.connect(DATABASE_PATH)
cursor = conn.cursor()

try:
    # 检查评估任务
    print("检查评估任务:")
    cursor.execute("SELECT id, name, status, result_summary, full_pdf_path, failed_pdf_path, full_report_file_path, failed_report_file_path FROM evaluation_tasks")
    tasks = cursor.fetchall()
    print(f"任务数量: {len(tasks)}")
    
    for task in tasks:
        task_id, name, status, result_summary, full_pdf_path, failed_pdf_path, full_report_path, failed_report_path = task
        print(f"\n任务ID: {task_id}, 名称: {name}, 状态: {status}")
        print(f"结果摘要: {result_summary}")
        print(f"全量PDF路径: {full_pdf_path}")
        print(f"未通过PDF路径: {failed_pdf_path}")
        print(f"全量JSON路径: {full_report_path}")
        print(f"未通过JSON路径: {failed_report_path}")
        
        # 检查文件是否存在
        if full_pdf_path:
            if not os.path.isabs(full_pdf_path):
                full_pdf_path = os.path.join(project_root, 'backend', full_pdf_path)
            if os.path.exists(full_pdf_path):
                print(f"全量PDF文件存在: {full_pdf_path}")
            else:
                print(f"全量PDF文件不存在: {full_pdf_path}")
        
        if failed_pdf_path:
            if not os.path.isabs(failed_pdf_path):
                failed_pdf_path = os.path.join(project_root, 'backend', failed_pdf_path)
            if os.path.exists(failed_pdf_path):
                print(f"未通过PDF文件存在: {failed_pdf_path}")
            else:
                print(f"未通过PDF文件不存在: {failed_pdf_path}")
        
        if full_report_path:
            if not os.path.isabs(full_report_path):
                full_report_path = os.path.join(project_root, 'backend', full_report_path)
            if os.path.exists(full_report_path):
                print(f"全量JSON文件存在: {full_report_path}")
            else:
                print(f"全量JSON文件不存在: {full_report_path}")
        
        if failed_report_path:
            if not os.path.isabs(failed_report_path):
                failed_report_path = os.path.join(project_root, 'backend', failed_report_path)
            if os.path.exists(failed_report_path):
                print(f"未通过JSON文件存在: {failed_report_path}")
            else:
                print(f"未通过JSON文件不存在: {failed_report_path}")
    
    # 检查评估结果
    print("\n检查评估结果:")
    cursor.execute("SELECT COUNT(*) FROM evaluation_results")
    result_count = cursor.fetchone()[0]
    print(f"评估结果数量: {result_count}")
    
    if result_count > 0:
        cursor.execute("SELECT task_id, case_index, evaluation_result, model_output FROM evaluation_results LIMIT 5")
        results = cursor.fetchall()
        print("前5条评估结果:")
        for result in results:
            task_id, case_index, evaluation_result, model_output = result
            print(f"任务ID: {task_id}, 用例索引: {case_index}, 评估结果: {evaluation_result}")
    else:
        print("没有评估结果数据")
    
    # 检查特定任务的评估结果
    print("\n检查任务ID=0的评估结果:")
    cursor.execute("SELECT COUNT(*) FROM evaluation_results WHERE task_id = 0")
    task0_results = cursor.fetchone()[0]
    print(f"任务ID=0的评估结果数量: {task0_results}")
    
    if task0_results > 0:
        cursor.execute("SELECT case_index, evaluation_result, model_output FROM evaluation_results WHERE task_id = 0")
        task0_data = cursor.fetchall()
        for data in task0_data:
            case_index, evaluation_result, model_output = data
            print(f"用例索引: {case_index}, 评估结果: {evaluation_result}")
    else:
        print("任务ID=0没有评估结果数据")
        
finally:
    # 关闭连接
    conn.close()

print("\n检查完成！")
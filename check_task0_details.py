import sqlite3
import os

# 数据库路径
project_root = os.path.dirname(os.path.abspath(__file__))
DATABASE_PATH = os.path.join(project_root, 'database', 'llm_eval_system.db')

print("检查任务ID=0的详细信息...")
print(f"数据库路径: {DATABASE_PATH}")
print()

# 连接数据库
conn = sqlite3.connect(DATABASE_PATH)
cursor = conn.cursor()

try:
    # 检查任务ID=0的信息
    print("检查任务ID=0的信息:")
    cursor.execute("""
        SELECT t.id, t.name, t.model_id, t.dataset_id, t.rule_id, t.status, t.result_summary, 
               t.full_pdf_path, t.failed_pdf_path, t.full_report_file_path, t.failed_report_file_path,
               COALESCE(s.name, e.name) as model_name,
               d.name as dataset_name, d.file_path as dataset_file_path,
               r.name as rule_name
        FROM evaluation_tasks t
        LEFT JOIN system_llms s ON t.model_id = s.id
        LEFT JOIN evaluation_llms e ON t.model_id = e.id
        LEFT JOIN datasets d ON t.dataset_id = d.id
        LEFT JOIN evaluation_rules r ON t.rule_id = r.id
        WHERE t.id = 0
    """)
    task = cursor.fetchone()
    
    if task:
        print(f"任务ID: {task[0]}")
        print(f"任务名称: {task[1]}")
        print(f"模型ID: {task[2]}")
        print(f"数据集ID: {task[3]}")
        print(f"规则ID: {task[4]}")
        print(f"状态: {task[5]}")
        print(f"结果摘要: {task[6]}")
        print(f"全量PDF路径: {task[7]}")
        print(f"未通过PDF路径: {task[8]}")
        print(f"全量JSON路径: {task[9]}")
        print(f"未通过JSON路径: {task[10]}")
        print(f"模型名称: {task[11]}")
        print(f"数据集名称: {task[12]}")
        print(f"数据集文件路径: {task[13]}")
        print(f"规则名称: {task[14]}")
        
        # 检查数据集文件是否存在
        if task[13]:
            dataset_file_path = task[13]
            if not os.path.isabs(dataset_file_path):
                dataset_file_path = os.path.join(project_root, dataset_file_path)
            if os.path.exists(dataset_file_path):
                print(f"数据集文件存在: {dataset_file_path}")
            else:
                print(f"数据集文件不存在: {dataset_file_path}")
    else:
        print("任务ID=0不存在")
    
    # 检查评估结果
    print("\n检查评估结果:")
    cursor.execute("SELECT COUNT(*) FROM evaluation_results WHERE task_id = 0")
    result_count = cursor.fetchone()[0]
    print(f"评估结果数量: {result_count}")
    
    if result_count > 0:
        cursor.execute("SELECT id, case_index, input_data, model_output, evaluation_result, details_text FROM evaluation_results WHERE task_id = 0 LIMIT 3")
        results = cursor.fetchall()
        print("前3条评估结果:")
        for result in results:
            print(f"ID: {result[0]}, 用例索引: {result[1]}, 评估结果: {result[4]}")
            print(f"  输入: {result[2][:50]}...")
            print(f"  输出: {result[3][:50]}...")
            print(f"  评估过程: {result[5][:50]}...")
    
    # 测试报告生成
    print("\n测试报告生成:")
    try:
        from backend.report_generator import generate_full_json_report
        report_path = generate_full_json_report(0, cursor)
        print(f"生成全量JSON报告: {report_path}")
        if report_path and os.path.exists(report_path):
            print(f"报告文件存在: {report_path}")
        else:
            print("报告文件不存在")
    except Exception as e:
        print(f"生成报告失败: {e}")
        import traceback
        traceback.print_exc()
        
finally:
    # 关闭连接
    conn.close()

print("\n检查完成！")
import sqlite3
import os
import json

DATABASE_PATH = 'g:\\llmsafe0403\\aiev\\database\\llm_eval_system.db'

conn = sqlite3.connect(DATABASE_PATH)
c = conn.cursor()

print("=== 查看任务 42 的数据集信息 ===")
c.execute("SELECT id, dataset_id, name FROM evaluation_tasks WHERE id=42")
task = c.fetchone()
print(f"任务: {task}")

if task:
    c.execute("SELECT id, name, file_path FROM datasets WHERE id=?", (task[1],))
    dataset = c.fetchone()
    print(f"数据集: {dataset}")
    
    if dataset and dataset[2]:
        file_path = dataset[2]
        print(f"\n数据集文件: {file_path}")
        print(f"文件存在: {os.path.exists(file_path)}")
        
        if os.path.exists(file_path):
            if file_path.endswith('.json'):
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                if isinstance(data, list):
                    print(f"数据集用例数: {len(data)}")
                    print(f"\n第一个用例:")
                    for k, v in data[0].items():
                        print(f"  {k}: {str(v)[:100]}")
            elif file_path.endswith('.csv'):
                import pandas as pd
                df = pd.read_csv(file_path)
                print(f"列名: {list(df.columns)}")
                print(f"行数: {len(df)}")

conn.close()

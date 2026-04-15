import sqlite3
import os

project_root = os.path.dirname(os.path.abspath(__file__))
DATABASE_PATH = os.path.join(project_root, 'database', 'llm_eval_system.db')

conn = sqlite3.connect(DATABASE_PATH)
cursor = conn.cursor()

cursor.execute("SELECT id, name, file_path, file_name FROM datasets WHERE id IN (12, 13)")
datasets = cursor.fetchall()

for ds in datasets:
    print(f"\n数据集 ID={ds[0]}, 名称：{ds[1]}")
    print(f"  file_path: {ds[2]}")
    print(f"  file_name: {ds[3]}")
    
    # 检查文件是否存在
    file_path = ds[2]
    if not os.path.isabs(file_path):
        # 尝试多个可能的位置
        possible_paths = [
            os.path.join(project_root, file_path),
            os.path.join(project_root, 'backend', file_path),
            os.path.join(project_root, 'datasets', ds[3])
        ]
        for path in possible_paths:
            if os.path.exists(path):
                print(f"  文件存在：{path}")
                break
        else:
            print(f"  文件不存在，尝试路径:")
            for path in possible_paths:
                print(f"    {path} - {'存在' if os.path.exists(path) else '不存在'}")

conn.close()
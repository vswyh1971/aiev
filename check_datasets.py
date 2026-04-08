import sqlite3
import os

# 连接数据库
DATABASE_PATH = r"g:\llmsafe0403\aiev\database\llm_eval_system.db"
conn = sqlite3.connect(DATABASE_PATH)
cursor = conn.cursor()

# 检查数据集表
print("=== 数据集表 ===")
cursor.execute("SELECT id, name, file_path FROM datasets;")
datasets = cursor.fetchall()

print(f"数据集数量: {len(datasets)}")
for d in datasets:
    dataset_id, name, file_path = d
    print(f"\n数据集 ID: {dataset_id}")
    print(f"  名称: {name}")
    print(f"  路径: {file_path}")
    
    # 检查文件是否存在
    if file_path:
        # 尝试多个可能的路径
        possible_paths = [
            file_path,  # 原始路径
            os.path.join(r"g:\llmsafe0403\aiev", file_path),  # 根目录
            os.path.join(r"g:\llmsafe0403\aiev\backend", file_path),  # backend目录
        ]
        
        found = False
        for p in possible_paths:
            if os.path.exists(p):
                print(f"  ✅ 文件存在: {p}")
                found = True
                break
        
        if not found:
            print(f"  ❌ 文件不存在 (尝试了: {possible_paths})")

conn.close()

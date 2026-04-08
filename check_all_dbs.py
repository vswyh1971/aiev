import sqlite3
import os

# 检查所有可能的数据库
databases = [
    r"g:\llmsafe0403\aiev\database\llm_eval_system.db",
    r"g:\llmsafe0403\aiev\llm_eval_system.db",
    r"g:\llmsafe0403\aiev\backend\llm_eval_system.db"
]

for db_path in databases:
    if os.path.exists(db_path):
        size = os.path.getsize(db_path)
        print(f"\n=== 数据库: {db_path} ({size} bytes) ===")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 检查数据集
        cursor.execute("SELECT id, name, file_path FROM datasets ORDER BY id")
        datasets = cursor.fetchall()
        print(f"数据集数量: {len(datasets)}")
        for d in datasets:
            print(f"  ID: {d[0]}, Name: {d[1]}, Path: {d[2]}")
        
        conn.close()
    else:
        print(f"\n数据库不存在: {db_path}")

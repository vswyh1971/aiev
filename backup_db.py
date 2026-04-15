#!/usr/bin/env python3
"""
数据库备份脚本
用于备份SQLite数据库，为后续迁移做准备
"""
import os
import shutil
from datetime import datetime

# 数据库路径
DB_PATH = os.path.join('database', 'llm_eval_system.db')
# 备份目录
BACKUP_DIR = 'database_backup'

# 创建备份目录
os.makedirs(BACKUP_DIR, exist_ok=True)

# 生成备份文件名
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
backup_file = os.path.join(BACKUP_DIR, f'llm_eval_system_{timestamp}.db')

# 执行备份
if os.path.exists(DB_PATH):
    shutil.copy2(DB_PATH, backup_file)
    print(f"数据库备份成功: {backup_file}")
    print(f"备份文件大小: {os.path.getsize(backup_file) / 1024:.2f} KB")
else:
    print(f"数据库文件不存在: {DB_PATH}")

# 列出所有备份文件
print("\n所有备份文件:")
for file in sorted(os.listdir(BACKUP_DIR)):
    if file.endswith('.db'):
        file_path = os.path.join(BACKUP_DIR, file)
        size = os.path.getsize(file_path) / 1024
        print(f"  - {file} ({size:.2f} KB)")

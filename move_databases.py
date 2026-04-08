import os
import shutil

# 项目根目录
PROJECT_ROOT = r"g:\llmsafe0403\aiev"
DATABASE_DIR = os.path.join(PROJECT_ROOT, "database")
BACKEND_DIR = os.path.join(PROJECT_ROOT, "backend")

# 1. 创建数据库目录
os.makedirs(DATABASE_DIR, exist_ok=True)
print(f"已创建数据库目录: {DATABASE_DIR}")

# 2. 查找并迁移所有数据库文件
db_files = []

# 检查根目录下的数据库
root_db = os.path.join(PROJECT_ROOT, "llm_eval_system.db")
if os.path.exists(root_db):
    db_files.append(("根目录", root_db))

# 检查backend目录下的数据库
backend_db = os.path.join(BACKEND_DIR, "llm_eval_system.db")
if os.path.exists(backend_db):
    db_files.append(("backend目录", backend_db))

# 检查其他可能的数据库文件
for root, dirs, files in os.walk(PROJECT_ROOT):
    # 跳过venv和其他不需要的目录
    if 'venv' in root or '__pycache__' in root or '.git' in root:
        continue
    for file in files:
        if file.endswith('.db'):
            full_path = os.path.join(root, file)
            if full_path not in [root_db, backend_db]:
                db_files.append((root, full_path))

print(f"\n找到 {len(db_files)} 个数据库文件:")
for location, path in db_files:
    if os.path.exists(path):
        size = os.path.getsize(path)
        print(f"  {location}: {path} ({size} bytes)")

# 3. 迁移数据库文件到database目录
# 首先找出最大的数据库（通常是主数据库）
main_db = None
main_db_size = 0

for location, path in db_files:
    if os.path.exists(path):
        size = os.path.getsize(path)
        if size > main_db_size:
            main_db_size = size
            main_db = path

print(f"\n主数据库: {main_db} ({main_db_size} bytes)")

# 复制主数据库到database目录
if main_db:
    target_db = os.path.join(DATABASE_DIR, "llm_eval_system.db")
    shutil.copy2(main_db, target_db)
    print(f"已复制主数据库到: {target_db}")

# 4. 更新后端main.py中的数据库路径
main_py = os.path.join(BACKEND_DIR, "main.py")
if os.path.exists(main_py):
    with open(main_py, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 使用相对路径
    new_db_path = 'os.path.join(os.path.dirname(os.path.dirname(__file__)), "database", "llm_eval_system.db")'
    
    # 替换原有的数据库路径配置
    old_pattern = 'DATABASE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "llm_eval_system.db")'
    content = content.replace(old_pattern, f'DATABASE_PATH = {new_db_path}')
    
    with open(main_py, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"\n已更新后端main.py中的数据库路径为相对路径:")
    print(f"  {new_db_path}")

# 5. 验证
print(f"\n=== 验证 ===")
final_db = os.path.join(DATABASE_DIR, "llm_eval_system.db")
if os.path.exists(final_db):
    size = os.path.getsize(final_db)
    print(f"✅ 数据库文件存在于: {final_db}")
    print(f"✅ 数据库文件大小: {size} bytes")
else:
    print(f"❌ 数据库文件不存在!")

print(f"\n=== 最终文件结构 ===")
print(f"项目根目录: {PROJECT_ROOT}")
print(f"数据库目录: {DATABASE_DIR}")
print(f"后端目录: {BACKEND_DIR}")

print("\n操作完成!")

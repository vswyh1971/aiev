import os

# 读取main.py文件
main_py_path = r"g:\llmsafe0403\aiev\backend\main.py"

with open(main_py_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 替换DATABASE_PATH配置
old_config = 'DATABASE_PATH = "llm_eval_system.db"'
new_config = '''# 配置 - 使用绝对路径确保始终读取正确的数据库
import os
DATABASE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "llm_eval_system.db")'''

# 检查是否已经修改过
if old_config in content:
    content = content.replace(old_config, new_config)

    # 写回文件
    with open(main_py_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print("数据库路径配置已修复！")
else:
    print("数据库路径已经是绝对路径或格式不同")

# 复制最新的数据库到backend目录
source_db = r"g:\llmsafe0403\aiev\llm_eval_system.db"
target_db = r"g:\llmsafe0403\aiev\backend\llm_eval_system.db"

if os.path.exists(source_db):
    # 备份旧的数据库
    if os.path.exists(target_db):
        backup_db = r"g:\llmsafe0403\aiev\backend\llm_eval_system.db.backup"
        import shutil
        shutil.copy(target_db, backup_db)
        print(f"已备份旧数据库到: {backup_db}")

    # 复制新数据库
    import shutil
    shutil.copy(source_db, target_db)
    print(f"已复制数据库到: {target_db}")
else:
    print(f"源数据库不存在: {source_db}")

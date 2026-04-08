import os
import shutil

# 项目根目录
PROJECT_ROOT = r"g:\llmsafe0403\aiev"
BACKEND_DIR = os.path.join(PROJECT_ROOT, "backend")
REPORTS_DIR = os.path.join(PROJECT_ROOT, "reports")

# 1. 创建项目根目录下的reports目录
os.makedirs(REPORTS_DIR, exist_ok=True)
print(f"已创建报告目录: {REPORTS_DIR}")

# 2. 迁移现有报告文件
backend_reports = os.path.join(BACKEND_DIR, "reports")
if os.path.exists(backend_reports):
    for filename in os.listdir(backend_reports):
        src = os.path.join(backend_reports, filename)
        dst = os.path.join(REPORTS_DIR, filename)
        shutil.move(src, dst)
        print(f"迁移报告文件: {filename}")

# 3. 清理后端reports目录
if os.path.exists(backend_reports):
    for item in os.listdir(backend_reports):
        item_path = os.path.join(backend_reports, item)
        if os.path.isfile(item_path):
            os.remove(item_path)
            print(f"删除后端报告: {item}")

# 4. 检查并更新后端main.py中的报告路径
main_py = os.path.join(BACKEND_DIR, "main.py")
if os.path.exists(main_py):
    with open(main_py, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查是否需要更新
    if 'reports/evaluation_report_' in content:
        print("\n后端main.py中的报告路径已经是相对路径 'reports/'")
        print("由于后端从backend目录启动，报告将输出到: backend/reports/")
        print("现在需要修改为项目根目录下的reports目录")
    
    # 修改报告路径为项目根目录下的reports
    content = content.replace('reports/evaluation_report_', f'{REPORTS_DIR}\\evaluation_report_')
    content = content.replace('reports/full_report_', f'{REPORTS_DIR}\\full_report_')
    content = content.replace('reports/failed_report_', f'{REPORTS_DIR}\\failed_report_')
    content = content.replace("os.makedirs('reports', exist_ok=True)", f"os.makedirs(r'{REPORTS_DIR}', exist_ok=True)")
    
    with open(main_py, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("\n已更新后端main.py中的报告路径为项目根目录下的reports目录")

# 5. 检查数据库路径配置
DATABASE_PATH_LINE = 'DATABASE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "llm_eval_system.db")'
CURRENT_DATABASE_PATH = os.path.join(PROJECT_ROOT, "llm_eval_system.db")

print(f"\n=== 数据库配置 ===")
print(f"数据库路径配置: {DATABASE_PATH_LINE}")
print(f"实际数据库文件: {CURRENT_DATABASE_PATH}")
print(f"数据库文件存在: {os.path.exists(CURRENT_DATABASE_PATH)}")

if os.path.exists(CURRENT_DATABASE_PATH):
    size = os.path.getsize(CURRENT_DATABASE_PATH)
    print(f"数据库文件大小: {size} bytes")

print("\n=== 文件结构 ===")
print(f"项目根目录: {PROJECT_ROOT}")
print(f"后端目录: {BACKEND_DIR}")
print(f"报告目录: {REPORTS_DIR}")
print(f"前端目录: {os.path.join(PROJECT_ROOT, 'frontend')}")

print("\n操作完成！")

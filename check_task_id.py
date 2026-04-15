import sqlite3
import os

# 数据库路径
DATABASE_PATH = os.path.join(os.path.dirname(__file__), "database", "llm_eval_system.db")

def check_task_id():
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    try:
        # 检查ID为38的任务数量
        cursor.execute("SELECT COUNT(*) FROM evaluation_tasks WHERE id = 38")
        count = cursor.fetchone()[0]
        
        print(f"ID为38的任务数量: {count}")
        
        if count > 1:
            print("警告：存在多个ID为38的任务！")
            # 查看详细信息
            cursor.execute("SELECT * FROM evaluation_tasks WHERE id = 38")
            tasks = cursor.fetchall()
            for task in tasks:
                print(f"任务详情: {task}")
        else:
            print("正常：ID为38的任务数量正常")
            if count == 1:
                # 查看任务详情
                cursor.execute("SELECT * FROM evaluation_tasks WHERE id = 38")
                task = cursor.fetchone()
                print(f"任务详情: {task}")
        
    except Exception as e:
        print(f"错误: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    check_task_id()

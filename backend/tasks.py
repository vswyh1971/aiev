"""Celery任务定义"""
import time
import sqlite3
import os
from config import config

# 尝试导入 Celery
celery_available = False
try:
    from celery import shared_task
    celery_available = True
except ImportError:
    pass

# 定义共享任务装饰器
def shared_task(func=None, **kwargs):
    """共享任务装饰器"""
    if celery_available:
        from celery import shared_task as celery_shared_task
        if func is None:
            return celery_shared_task(**kwargs)
        else:
            return celery_shared_task(func, **kwargs)
    else:
        # 如果 Celery 不可用，直接返回原函数
        if func is None:
            def decorator(f):
                return f
            return decorator
        else:
            return func

@shared_task(bind=True)
def evaluate_task(self, task_id):
    """评估任务"""
    # 处理本地执行和Celery执行的不同情况
    if not isinstance(self, type):  # 如果是Celery任务调用
        return _evaluate_task(task_id)
    else:  # 如果是本地直接调用
        return _evaluate_task(self)  # 这里self实际上是task_id

def _evaluate_task(task_id):
    """实际执行评估任务的函数"""
    try:
        print(f"开始执行任务 {task_id}")
        # 连接数据库
        db_path = config.get('database.url', 'sqlite:///../database/llm_eval_system.db')
        if db_path.startswith('sqlite:///'):
            db_path = db_path[10:]
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 更新任务状态为运行中
        cursor.execute(
            "UPDATE evaluation_tasks SET status = 'running', start_time = CURRENT_TIMESTAMP WHERE id = ?",
            (task_id,)
        )
        conn.commit()
        print(f"任务 {task_id} 状态更新为运行中")
        
        # 获取任务信息
        cursor.execute(
            "SELECT model_id, dataset_id, rule_id, total_cases FROM evaluation_tasks WHERE id = ?",
            (task_id,)
        )
        task_info = cursor.fetchone()
        if not task_info:
            raise Exception("任务信息不存在")
        
        model_id, dataset_id, rule_id, total_cases = task_info
        print(f"任务 {task_id} 总案例数: {total_cases}")
        
        # 模拟评估过程
        completed_cases = 0
        passed_cases = 0
        failed_cases = 0
        
        for i in range(total_cases):
            # 模拟评估结果
            import random
            evaluation_result = random.choice(['passed', 'failed'])
            
            # 生成评估结果数据
            input_data = {"question": f"测试问题 {i+1}"}
            model_output = f"模型输出 {i+1}"
            details_text = f"评估过程: 测试案例 {i+1} 的评估详情"
            
            # 插入评估结果
            cursor.execute(
                """
                INSERT INTO evaluation_results (task_id, case_index, input_data, model_output, evaluation_result, details_text)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (task_id, i, str(input_data), model_output, evaluation_result, details_text)
            )
            
            # 更新统计数据
            completed_cases += 1
            if evaluation_result == 'passed':
                passed_cases += 1
            else:
                failed_cases += 1
            
            # 更新进度
            progress = int((i + 1) / total_cases * 100)
            cursor.execute(
                "UPDATE evaluation_tasks SET progress_percent = ?, completed_cases = ?, passed_cases = ?, failed_cases = ? WHERE id = ?",
                (progress, completed_cases, passed_cases, failed_cases, task_id)
            )
            conn.commit()
            print(f"任务 {task_id} 进度: {progress}%, 已完成: {completed_cases}, 通过: {passed_cases}, 失败: {failed_cases}")
            
            # 模拟评估时间
            time.sleep(0.5)
        
        # 更新任务状态为完成
        cursor.execute(
            "UPDATE evaluation_tasks SET status = 'completed', end_time = CURRENT_TIMESTAMP, completed_cases = ?, passed_cases = ?, failed_cases = ? WHERE id = ?",
            (completed_cases, passed_cases, failed_cases, task_id)
        )
        conn.commit()
        print(f"任务 {task_id} 状态更新为完成")
        
        cursor.close()
        conn.close()
        
        return f"任务 {task_id} 评估完成，共 {completed_cases} 个案例，{passed_cases} 个通过，{failed_cases} 个失败"
    except Exception as e:
        print(f"执行任务 {task_id} 失败: {e}")
        # 更新任务状态为失败
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE evaluation_tasks SET status = 'failed' WHERE id = ?",
                (task_id,)
            )
            conn.commit()
            cursor.close()
            conn.close()
            print(f"任务 {task_id} 状态更新为失败")
        except:
            pass
        
        # 本地执行时直接抛出异常，不使用Celery的retry
        raise

@shared_task
def generate_report(task_id):
    """生成报告任务"""
    try:
        # 这里应该调用实际的报告生成逻辑
        time.sleep(5)
        return f"报告生成完成: {task_id}"
    except Exception as e:
        raise

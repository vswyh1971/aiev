import os
import json
import sqlite3
import threading
import queue
import time
import hashlib
import socket
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List, Tuple

from fastapi import FastAPI, Depends, HTTPException, Query, UploadFile, File, Form
from fastapi.responses import StreamingResponse
import asyncio
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt

# 数据库配置
import os
project_root = os.path.dirname(os.path.dirname(__file__))
DATABASE_PATH = os.path.join(project_root, 'database', 'llm_eval_system.db')

# 前端服务配置
FRONTEND_PORTS = [8080, 3000, 5000, 8001]  # 常见前端端口
BACKEND_PORT = 8000

def check_startup_config():
    """启动时检查配置参数"""
    print("\n" + "="*50)
    print("  系统启动配置检查")
    print("="*50)
    
    # 1. 检查数据库
    print("\n[1] 数据库配置检查:")
    print(f"    数据库路径: {DATABASE_PATH}")
    if os.path.exists(DATABASE_PATH):
        try:
            conn = sqlite3.connect(DATABASE_PATH)
            cur = conn.cursor()
            cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cur.fetchall()
            print(f"    ✓ 数据库连接成功")
            print(f"    ✓ 数据表数量: {len(tables)}")
            for t in tables:
                cur.execute(f"SELECT COUNT(*) FROM {t[0]}")
                count = cur.fetchone()[0]
                print(f"      - {t[0]}: {count} 条记录")
            conn.close()
        except Exception as e:
            print(f"    ✗ 数据库连接失败: {e}")
    else:
        print(f"    ✗ 数据库文件不存在!")
    
    # 2. 检查前端端口
    print("\n[2] 前端服务端口检测:")
    detected_ports = []
    for port in FRONTEND_PORTS:
        if is_port_in_use(port):
            detected_ports.append(port)
            print(f"    ✓ 检测到前端服务运行在端口: {port}")
        else:
            print(f"    - 端口 {port} 未使用")
    
    # 3. 检查后端端口
    print("\n[3] 后端服务端口检查:")
    print(f"    后端端口: {BACKEND_PORT}")
    if is_port_in_use(BACKEND_PORT):
        print(f"    ✓ 后端服务运行正常")
    else:
        print(f"    ✗ 后端端口未启用!")
    
    # 4. CORS配置建议
    print("\n[4] CORS跨域配置建议:")
    if detected_ports:
        cors_origins = [f"http://localhost:{p}" for p in detected_ports]
        print(f"    建议CORS配置: {cors_origins}")
        print(f"    当前代码中的CORS配置需要包含这些端口")
    else:
        print(f"    未检测到前端服务，请确保前端已启动")
    
    # 5. 项目目录结构检查
    print("\n[5] 项目目录结构检查:")
    dirs_to_check = ['database', 'datasets', 'reports', 'uploads']
    for d in dirs_to_check:
        path = os.path.join(project_root, d)
        if os.path.exists(path):
            print(f"    ✓ {d}/ 目录存在")
        else:
            print(f"    ✗ {d}/ 目录不存在，将被创建")
            os.makedirs(path, exist_ok=True)
    
    print("\n" + "="*50)
    print("  配置检查完成")
    print("="*50 + "\n")

def is_port_in_use(port):
    """检查端口是否被占用"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

# 安全配置
SECRET_KEY = "your-secret-key-here"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440  # 24小时

# 评估队列
evaluation_queue = queue.Queue()
evaluation_workers = []

# 导入Celery配置
from celery_config import celery
from tasks import evaluate_task

# 导入PDF生成模块
from report_generator import generate_full_pdf_report, generate_failed_pdf_report, generate_full_json_report, generate_failed_json_report

# 导入LLM测试模块
from llm_test import test_llm_connection, call_llm, evaluate_with_system_llm, find_available_system_llm

# 导入日志配置
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 导入工具函数
from utils import get_dataset_file_path, load_sensitive_words, check_sensitive_content

# 导入审计日志和安全工具
from audit import audit_logger
from security import security_utils

# 导入资源管理器
from resource_manager import resource_manager

# 导入任务模块
try:
    from tasks import evaluate_task
    # 暂时禁用Celery，避免Redis连接错误
    celery_available = False
except ImportError:
    celery_available = False

# 本地任务执行器
import threading
import queue

local_task_queue = queue.Queue()
local_task_thread = None

class LocalTaskWorker(threading.Thread):
    """本地任务执行器"""
    def __init__(self, queue):
        super().__init__()
        self.queue = queue
        self.daemon = True
    
    def run(self):
        while True:
            task_id = self.queue.get()
            try:
                # 导入任务函数
                from tasks import evaluate_task
                # 直接执行任务
                evaluate_task(task_id)
            except Exception as e:
                print(f"执行任务失败: {e}")
            finally:
                self.queue.task_done()

# 启动本地任务执行器
def start_local_task_worker():
    global local_task_thread
    if local_task_thread is None:
        local_task_thread = LocalTaskWorker(local_task_queue)
        local_task_thread.start()

# 启动本地任务执行器
start_local_task_worker()

# 初始化FastAPI应用
app = FastAPI(
    title="智能大模型安全评估系统",
    description="一个功能完备、安全可靠的LLM安全性能评估平台",
    version="1.0.0"
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000", "http://localhost:8080", "null"],  # 指定前端域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# OAuth2密码承载令牌
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

# Server-Sent Events 客户端连接管理
sse_clients = set()

def notify_task_complete(task_id: int, status: str):
    """通知所有客户端任务状态更新"""
    for client in sse_clients:
        try:
            client.put_nowait({"task_id": task_id, "status": status})
        except:
            pass

# 初始化敏感词库
load_sensitive_words()

# 初始化评估工作线程
class EvaluationWorker(threading.Thread):
    def __init__(self, worker_id):
        super().__init__()
        self.worker_id = worker_id
        self.daemon = True
        
    def run(self):
        while True:
            task_id = evaluation_queue.get()
            try:
                run_evaluation(task_id)
            except Exception as e:
                print(f"Worker {self.worker_id} error: {e}")
                # 记录详细错误日志
                logger.error(f"Worker {self.worker_id} error processing task {task_id}: {str(e)}")
                # 更新任务状态为失败
                try:
                    conn = sqlite3.connect(DATABASE_PATH)
                    cursor = conn.cursor()
                    cursor.execute("UPDATE evaluation_tasks SET status='failed', result_summary=? WHERE id=?", 
                                  (f"执行失败: {str(e)}", task_id))
                    conn.commit()
                    conn.close()
                except Exception as db_error:
                    logger.error(f"Failed to update task {task_id} status: {str(db_error)}")
            finally:
                evaluation_queue.task_done()

def initialize_evaluation_workers(num_workers=3):
    """初始化评估工作线程"""
    global evaluation_workers
    for i in range(num_workers):
        worker = EvaluationWorker(i)
        worker.start()
        evaluation_workers.append(worker)

# 工具函数
def verify_password(plain_password, hashed_password):
    """验证密码"""
    return hashlib.sha256(plain_password.encode()).hexdigest() == hashed_password

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """创建访问令牌"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=24)  # 延长过期时间到24小时
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    """获取当前用户"""
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, role FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()
    
    if user is None:
        raise credentials_exception
    
    return {"id": user[0], "username": user[1], "role": user[2]}

# 执行评估任务
def run_evaluation(task_id: int):
    """执行评估任务"""
    print(f"========== 开始执行评估任务 ID: {task_id} ==========")
    
    conn = None
    cursor = None
    total_cases = 0
    passed = 0
    failed = 0
    errors = 0
    report_path = None
    full_report_path = None
    failed_report_path = None
    full_pdf_path = None
    failed_pdf_path = None
    eval_model_name = None
    
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        # 获取任务信息
        cursor.execute("""
            SELECT t.id, t.name, t.model_id, t.dataset_id, t.rule_id,
                   COALESCE(s.api_url, e.api_url) as api_url, 
                   COALESCE(s.api_key_encrypted, e.api_key_encrypted) as api_key_encrypted, 
                   COALESCE(s.model_type, e.model_type) as model_type, 
                   COALESCE(s.max_tokens, e.max_tokens) as max_tokens, 
                   COALESCE(s.temperature, e.temperature) as temperature, 
                   COALESCE(s.response_timeout, e.response_timeout) as response_timeout, 
                   d.file_path, d.name as dataset_name, r.name as rule_name,
                   r.rule_config_json
            FROM evaluation_tasks t
            LEFT JOIN system_llms s ON t.model_id = s.id
            LEFT JOIN evaluation_llms e ON t.model_id = e.id
            JOIN datasets d ON t.dataset_id = d.id
            JOIN evaluation_rules r ON t.rule_id = r.id
            WHERE t.id = ?
        """, (task_id,))
        task = cursor.fetchone()
        
        if not task:
            logger.error(f"任务 {task_id} 不存在")
            # 更新任务状态为失败
            try:
                cursor.execute("UPDATE evaluation_tasks SET status='failed', result_summary=? WHERE id=?", 
                              ("任务不存在", task_id))
                conn.commit()
            except Exception as db_error:
                logger.error(f"更新任务状态失败: {str(db_error)}")
            return
        
        # 数据验证：检查任务数据完整性
        if len(task) < 15:
            logger.error(f"任务 {task_id} 数据不完整")
            # 更新任务状态为失败
            try:
                cursor.execute("UPDATE evaluation_tasks SET status='failed', result_summary=? WHERE id=?", 
                              ("任务数据不完整", task_id))
                conn.commit()
            except Exception as db_error:
                logger.error(f"更新任务状态失败: {str(db_error)}")
            return
        
        # 获取任务信息
        task_name = task[1]
        eval_model_id = task[2]
        
        logger.info(f"开始评估任务: {task_name} (ID: {task_id})")
        logger.info(f"评估LLM ID: {eval_model_id}")
        
        # ========== 步骤0: 删除现有评估结果 ==========
        logger.info("步骤0: 删除现有评估结果")
        try:
            # 删除该任务的所有现有评估结果
            cursor.execute("DELETE FROM evaluation_results WHERE task_id = ?", (task_id,))
            conn.commit()
            logger.info(f"成功删除任务 {task_id} 的现有评估结果")
        except Exception as e:
            logger.error(f"删除现有评估结果失败: {str(e)}")
        
        # ========== 步骤1: 测试评估LLM连接 ==========
        logger.info("步骤1: 测试评估LLM连接")
        
        cursor.execute("""
            SELECT id, name, api_url, api_key_encrypted, model_type, max_tokens, temperature, response_timeout
            FROM system_llms WHERE id = ?
        """, (eval_model_id,))
        eval_model = cursor.fetchone()
        
        if not eval_model:
            cursor.execute("""
                SELECT id, name, api_url, api_key_encrypted, model_type, max_tokens, temperature, response_timeout
                FROM evaluation_llms WHERE id = ?
            """, (eval_model_id,))
            eval_model = cursor.fetchone()
        
        if not eval_model:
            error_msg = f"评估LLM (ID: {eval_model_id}) 不存在"
            logger.error(error_msg)
            cursor.execute("UPDATE evaluation_tasks SET status='failed', result_summary=? WHERE id=?", 
                          (error_msg, task_id))
            conn.commit()
            return
        
        # 数据验证：检查评估模型数据完整性
        if len(eval_model) < 8:
            error_msg = f"评估LLM (ID: {eval_model_id}) 数据不完整"
            logger.error(error_msg)
            cursor.execute("UPDATE evaluation_tasks SET status='failed', result_summary=? WHERE id=?", 
                          (error_msg, task_id))
            conn.commit()
            return
        
        eval_model_id, eval_model_name, eval_api_url, eval_api_key, eval_model_type, eval_max_tokens, eval_temperature, eval_timeout = eval_model
        eval_timeout = eval_timeout or 30
        
        logger.info(f"测试评估LLM: {eval_model_name}")
        eval_success, eval_message = test_llm_connection(eval_api_url, eval_api_key, eval_model_type, eval_timeout)
        
        if not eval_success:
            error_msg = f"评估LLM连接失败: {eval_message} (模型: {eval_model_name})"
            logger.error(error_msg)
            cursor.execute("UPDATE evaluation_tasks SET status='failed', result_summary=? WHERE id=?", 
                          (error_msg, task_id))
            conn.commit()
            return
        
        logger.info(f"评估LLM [{eval_model_name}] 连接测试通过")
        print(f"评估LLM [{eval_model_name}] 连接测试通过")
        
        # ========== 步骤2: 查找可用的系统LLM ==========
        logger.info("步骤2: 查找可用的系统LLM")
        
        sys_success, sys_model, sys_message = find_available_system_llm()
        
        if not sys_success:
            error_msg = f"系统LLM连接失败: {sys_message}"
            logger.error(error_msg)
            cursor.execute("UPDATE evaluation_tasks SET status='failed', result_summary=? WHERE id=?", 
                          (error_msg, task_id))
            conn.commit()
            return
        
        logger.info(f"系统LLM [{sys_model['name']}] 选择成功")
        print(f"系统LLM [{sys_model['name']}] 选择成功")
        
        # ========== 步骤3: 双重验证通过，开始评估 ==========
        logger.info("步骤3: 双重验证通过，开始评估")
        
        # 更新任务状态为运行中
        cursor.execute("UPDATE evaluation_tasks SET status='running', start_time=CURRENT_TIMESTAMP WHERE id=?", (task_id,))
        conn.commit()
        
        # 解析规则配置
        task_rule_config = task[14] if len(task) > 14 else None
        try:
            rule_config = json.loads(task_rule_config) if task_rule_config else {}
        except Exception as e:
            logger.error(f"解析规则配置失败: {str(e)}")
            rule_config = {}
        
        # 数据验证：检查规则配置完整性
        if not rule_config.get('evaluation_criteria'):
            logger.warning("评估规则未设置，使用默认规则")
            rule_config['evaluation_criteria'] = '根据评估标准判断输出是否合规'
        
        logger.info(f"评估规则: {rule_config.get('evaluation_criteria')}")
        logger.info(f"输入字段: {rule_config.get('input_fields', [])}")
        logger.info(f"期望输出字段: {rule_config.get('expected_field', '')}")
        
        # 加载数据集
        file_path = task[11] if len(task) > 11 else None  # d.file_path
        dataset_name = task[12] if len(task) > 12 else '未知数据集'
        
        if not file_path:
            error_msg = "数据集文件路径无效"
            print(f"错误: {error_msg}")
            cursor.execute("UPDATE evaluation_tasks SET status='failed', result_summary=? WHERE id=?", 
                          (error_msg, task_id))
            conn.commit()
            return
        
        # 使用get_dataset_file_path函数解析正确的路径
        file_path = get_dataset_file_path(file_path)
        
        if not os.path.exists(file_path):
            error_msg = f"数据集文件不存在: {file_path}"
            print(f"错误: {error_msg}")
            cursor.execute("UPDATE evaluation_tasks SET status='failed', result_summary=? WHERE id=?", 
                          (error_msg, task_id))
            conn.commit()
            return
        
        # 读取数据集
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                dataset = json.load(f)
        except Exception as e:
            error_msg = f"加载数据集失败: {str(e)}"
            print(f"错误: {error_msg}")
            cursor.execute("UPDATE evaluation_tasks SET status='failed', result_summary=? WHERE id=?", 
                          (error_msg, task_id))
            conn.commit()
            return
        
        if not isinstance(dataset, list):
            error_msg = "数据集格式错误，应为列表"
            print(f"错误: {error_msg}")
            cursor.execute("UPDATE evaluation_tasks SET status='failed', result_summary=? WHERE id=?", 
                          (error_msg, task_id))
            conn.commit()
            return
        
        total_cases = len(dataset)
        logger.info(f"数据集加载成功，共 {total_cases} 个测试用例")
        
        # 初始化任务进度
        cursor.execute("UPDATE evaluation_tasks SET total_cases=?, progress_percent=0, completed_cases=0, passed_cases=0, failed_cases=0, error_count=0 WHERE id=?", 
                      (total_cases, task_id))
        conn.commit()
        
        # 遍历数据集执行评估
        for idx, case in enumerate(dataset):
            print(f"  [{idx+1}/{total_cases}] 评估中...")
            logger.info(f"评估用例 {idx+1}/{total_cases}")
            
            # 提取输入文本 - 支持多种字段名
            if isinstance(case, dict):
                input_text = case.get('prompt') or case.get('input') or case.get('text') or case.get('question') or case.get('query') or case.get('instruction') or ''
            else:
                input_text = str(case)
            
            if not input_text or not input_text.strip():
                print(f"  [{idx+1}/{total_cases}] 跳过：无输入文本")
                logger.warning(f"用例 {idx+1} 无输入文本，跳过")
                errors += 1
                continue
            
            # 调用评估LLM
            max_retries = 3
            retry_count = 0
            while retry_count < max_retries:
                try:
                    model_output, response_time = call_llm(eval_api_url, eval_api_key, input_text, 
                                                        eval_model_type, eval_max_tokens, 
                                                        eval_temperature, eval_timeout)
                    
                    if "Error:" in model_output:
                        print(f"  [{idx+1}/{total_cases}] 模型错误: {model_output}")
                        logger.error(f"模型错误: {model_output}")
                        errors += 1
                        try:
                            # 评估结果为不通过，评估过程记录错误信息
                            cursor.execute("""
                                INSERT INTO evaluation_results (task_id, case_index, evaluation_result, details_text, model_output, input_data, model_response_time)
                                VALUES (?, ?, ?, ?, ?, ?, ?)
                            """, (task_id, idx, 'failed', f'评估结果：不通过\n评估理由：模型执行错误 - {model_output}', model_output, input_text, response_time))
                            conn.commit()
                        except Exception as e2:
                            logger.error(f"保存错误记录失败: {str(e2)}")
                        break
                    
                    # 使用系统LLM进行评估
                    eval_result, eval_tokens, eval_process = evaluate_with_system_llm(
                        case, model_output, rule_config,
                        sys_model['api_url'], sys_model['api_key'], sys_model['model_type'],
                        sys_model.get('timeout', 30)
                    )
                    
                    # 解析评估结果
                    # 支持：不通过/部分拒答 -> failed，通过 -> passed
                    if "评估结果" in eval_result:
                        # 检查是否包含"通过"且不包含"不通过"
                        if "通过" in eval_result and "不通过" not in eval_result and "部分拒答" not in eval_result:
                            evaluation_result = "passed"
                            passed += 1
                            # 提取评估理由
                            details_text = eval_result
                            for pattern in ["评估结果：通过\n", "评估结果: 通过\n", "评估结果：通过", "评估结果: 通过"]:
                                details_text = details_text.replace(pattern, "")
                        else:
                            # 评估结果：不通过、部分拒答 或其他情况都归为不通过
                            evaluation_result = "failed"
                            failed += 1
                            # 提取评估理由
                            details_text = eval_result
                            for pattern in ["评估结果：不通过\n", "评估结果: 不通过\n", "评估结果：不通过", "评估结果: 不通过"]:
                                details_text = details_text.replace(pattern, "")
                            for pattern in ["评估结果：部分拒答\n", "评估结果: 部分拒答\n", "评估结果：部分拒答", "评估结果: 部分拒答"]:
                                details_text = details_text.replace(pattern, "")
                    
                    # 保存评估结果（只保存评估理由到 details_text）
                    try:
                        cursor.execute("""
                            INSERT INTO evaluation_results (task_id, case_index, evaluation_result, details_text, model_output, input_data, model_response_time)
                            VALUES (?, ?, ?, ?, ?, ?, ?)
                        """, (task_id, idx, evaluation_result, details_text.strip(), model_output, input_text, response_time))
                        conn.commit()
                    except Exception as e2:
                        logger.error(f"保存评估结果失败: {str(e2)}")
                    
                    # 计算并更新进度
                    progress = int((idx + 1) / total_cases * 100)
                    try:
                        cursor.execute("UPDATE evaluation_tasks SET progress_percent=?, completed_cases=?, passed_cases=?, failed_cases=?, error_count=? WHERE id=?",
                                    (progress, idx + 1, passed, failed, errors, task_id))
                        conn.commit()
                    except Exception as e2:
                        logger.error(f"更新任务进度失败: {str(e2)}")
                    
                    break
                except Exception as e:
                    retry_count += 1
                    print(f"  [{idx+1}/{total_cases}] 评估失败，重试 {retry_count}/{max_retries}: {str(e)}")
                    logger.error(f"评估失败，重试 {retry_count}/{max_retries}: {str(e)}")
                    
                    if retry_count >= max_retries:
                        print(f"  [{idx+1}/{total_cases}] 达到最大重试次数 ({max_retries})，停止重新评估")
                        errors += 1
                        try:
                            cursor.execute("""
                                INSERT INTO evaluation_results (task_id, case_index, evaluation_result, details_text, model_output, input_data)
                                VALUES (?, ?, ?, ?, ?, ?)
                            """, (task_id, idx, 'error', str(e), '', input_text))
                            conn.commit()
                        except Exception as e2:
                            logger.error(f"保存错误记录失败: {str(e2)}")
        
        # 生成报告
        logger.info("生成评估报告")
        
        try:
            # 生成全量PDF报告
            full_pdf_path = generate_full_pdf_report(task_id, cursor)
            logger.info(f"全量PDF报告已生成: {full_pdf_path}")
            
            # 生成不合格记录PDF报告
            failed_pdf_path = generate_failed_pdf_report(task_id, cursor)
            logger.info(f"不合格记录PDF报告已生成: {failed_pdf_path}")
            
            # 设置默认报告路径为全量报告
            report_path = full_pdf_path
        except Exception as e:
            logger.error(f"PDF报告生成失败: {str(e)}")
        
        # 生成全量JSON报告（仅管理员可访问）
        try:
            full_report_path = generate_full_json_report(task_id, cursor)
            logger.info(f"全量JSON报告已生成: {full_report_path}")
        except Exception as e:
            logger.error(f"全量JSON报告生成失败: {str(e)}")
        
        # 生成未通过评估报告（用户可访问）
        try:
            failed_report_path = generate_failed_json_report(task_id, cursor)
            logger.info(f"未通过JSON报告已生成: {failed_report_path}")
        except Exception as e:
            logger.error(f"未通过JSON报告生成失败: {str(e)}")
        
        # 更新最终状态
        try:
            cursor.execute("""
                UPDATE evaluation_tasks SET status='completed', end_time=CURRENT_TIMESTAMP,
                                        result_summary=?, report_file_path=?, 
                                        full_report_file_path=?, failed_report_file_path=?,
                                        full_pdf_path=?, failed_pdf_path=? WHERE id=?
            """, (f"总计{total_cases}例，通过{passed}例，失败{failed}例，异常{errors}例", 
                  report_path, full_report_path, failed_report_path,
                  full_pdf_path, failed_pdf_path, task_id))
            conn.commit()
            logger.info(f"评估任务状态已更新")
            # 通知前端任务已完成
            notify_task_complete(task_id, 'completed')
        except Exception as e:
            logger.error(f"更新评估任务状态失败: {str(e)}")
            # 重试机制
            import time
            for i in range(3):
                try:
                    time.sleep(1)
                    conn = sqlite3.connect(DATABASE_PATH)
                    cursor = conn.cursor()
                    cursor.execute("""
                        UPDATE evaluation_tasks SET status='completed', end_time=CURRENT_TIMESTAMP,
                                                result_summary=?, report_file_path=?, 
                                                full_report_file_path=?, failed_report_file_path=?,
                                                full_pdf_path=?, failed_pdf_path=? WHERE id=?
                    """, (f"总计{total_cases}例，通过{passed}例，失败{failed}例，异常{errors}例", 
                          report_path, full_report_path, failed_report_path,
                          full_pdf_path, failed_pdf_path, task_id))
                    conn.commit()
                    logger.info(f"评估任务状态已更新（重试 {i+1}")
                    break
                except Exception as retry_error:
                    logger.error(f"重试更新评估任务状态失败 {i+1}: {str(retry_error)}")
    except Exception as e:
        logger.error(f"执行评估任务失败: {str(e)}")
        # 更新任务状态为失败
        try:
            if conn and cursor:
                cursor.execute("UPDATE evaluation_tasks SET status='failed', result_summary=? WHERE id=?", 
                              (f"执行失败: {str(e)}", task_id))
                conn.commit()
        except Exception as db_error:
            logger.error(f"更新任务失败状态失败: {str(db_error)}")
    finally:
        if conn:
            conn.close()
    
    logger.info("评估任务完成")
    logger.info(f"总计: {total_cases}, 通过: {passed}, 失败: {failed}, 异常: {errors}")

# 认证相关 API
@app.post("/api/auth/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """用户登录"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, password_hash, role FROM users WHERE username = ?", (form_data.username,))
    user = cursor.fetchone()
    conn.close()
    
    # 使用 SHA256 验证密码（与数据库中的密码格式匹配）
    import hashlib
    hashed_password = hashlib.sha256(form_data.password.encode()).hexdigest()
    
    if not user or hashed_password != user[2]:
        # 记录登录失败审计日志
        audit_logger.log(0, "login_failed", "user", {"username": form_data.username, "reason": "用户名或密码错误"})
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=1440)
    access_token = create_access_token(
        data={"sub": user[1]}, expires_delta=access_token_expires
    )
    
    # 记录登录成功审计日志
    audit_logger.log(user[0], "login", "user", {"username": user[1], "role": user[3]})
    
    return {"access_token": access_token, "token_type": "bearer", "username": user[1], "role": user[3]}

# 用户管理API
@app.get("/api/users")
async def get_users(current_user = Depends(get_current_user)):
    """获取用户列表"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, role, created_at FROM users")
    users = cursor.fetchall()
    conn.close()
    
    return [{
        "id": user[0],
        "username": user[1],
        "role": user[2],
        "created_at": user[3]
    } for user in users]

# 系统LLM管理API
@app.get("/api/models")
async def get_models(category: Optional[str] = Query(None, description="模型类别: system 或 evaluation"), current_user = Depends(get_current_user)):
    """获取模型列表"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    if category == "system":
        cursor.execute("SELECT id, name, api_url, model_type, max_tokens, temperature, response_timeout, created_at FROM system_llms")
        models = cursor.fetchall()
        conn.close()
        return [{
            "id": model[0],
            "name": model[1],
            "api_url": model[2],
            "model_type": model[3],
            "max_tokens": model[4],
            "temperature": model[5],
            "response_timeout": model[6],
            "created_at": model[7]
        } for model in models]
    elif category == "evaluation":
        cursor.execute("SELECT id, name, api_url, model_type, max_tokens, temperature, response_timeout, created_at FROM evaluation_llms")
        models = cursor.fetchall()
        conn.close()
        return [{
            "id": model[0],
            "name": model[1],
            "api_url": model[2],
            "model_type": model[3],
            "max_tokens": model[4],
            "temperature": model[5],
            "response_timeout": model[6],
            "created_at": model[7]
        } for model in models]
    else:
        # 返回所有模型
        cursor.execute("SELECT id, name, 'system' as category, api_url, model_type, max_tokens, temperature, response_timeout, created_at FROM system_llms")
        system_models = cursor.fetchall()
        cursor.execute("SELECT id, name, 'evaluation' as category, api_url, model_type, max_tokens, temperature, response_timeout, created_at FROM evaluation_llms")
        eval_models = cursor.fetchall()
        conn.close()
        
        all_models = []
        for model in system_models:
            all_models.append({
                "id": model[0],
                "name": model[1],
                "category": model[2],
                "api_url": model[3],
                "model_type": model[4],
                "max_tokens": model[5],
                "temperature": model[6],
                "response_timeout": model[7],
                "created_at": model[8]
            })
        for model in eval_models:
            all_models.append({
                "id": model[0],
                "name": model[1],
                "category": model[2],
                "api_url": model[3],
                "model_type": model[4],
                "max_tokens": model[5],
                "temperature": model[6],
                "response_timeout": model[7],
                "created_at": model[8]
            })
        return all_models

@app.post("/api/models")
async def create_model(
    name: str = Form(...),
    category: str = Form(...),
    api_url: str = Form(...),
    api_key: str = Form(...),
    model_type: str = Form(...),
    max_tokens: int = Form(...),
    temperature: float = Form(...),
    response_timeout: int = Form(...),
    current_user = Depends(get_current_user)
):
    """创建模型"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    try:
        if category == "system":
            cursor.execute("""
                INSERT INTO system_llms (name, api_url, api_key_encrypted, model_type, max_tokens, temperature, response_timeout, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (name, api_url, api_key, model_type, max_tokens, temperature, response_timeout))
        elif category == "evaluation":
            cursor.execute("""
                INSERT INTO evaluation_llms (name, api_url, api_key_encrypted, model_type, max_tokens, temperature, response_timeout, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (name, api_url, api_key, model_type, max_tokens, temperature, response_timeout))
        else:
            raise HTTPException(status_code=400, detail="无效的模型类别")
        
        conn.commit()
        return {"message": "模型创建成功"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        conn.close()

@app.put("/api/models/{model_id}")
async def update_model(
    model_id: int,
    name: str = Form(...),
    api_url: str = Form(...),
    api_key: str = Form(...),
    model_type: str = Form(...),
    max_tokens: int = Form(...),
    temperature: float = Form(...),
    response_timeout: int = Form(...),
    category: str = Form(...),
    current_user = Depends(get_current_user)
):
    """更新模型"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    try:
        if category == "system":
            cursor.execute("""
                UPDATE system_llms SET name=?, api_url=?, api_key_encrypted=?, model_type=?, max_tokens=?, temperature=?, response_timeout=?
                WHERE id=?
            """, (name, api_url, api_key, model_type, max_tokens, temperature, response_timeout, model_id))
        elif category == "evaluation":
            cursor.execute("""
                UPDATE evaluation_llms SET name=?, api_url=?, api_key_encrypted=?, model_type=?, max_tokens=?, temperature=?, response_timeout=?
                WHERE id=?
            """, (name, api_url, api_key, model_type, max_tokens, temperature, response_timeout, model_id))
        else:
            raise HTTPException(status_code=400, detail="无效的模型类别")
        
        conn.commit()
        return {"message": "模型更新成功"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        conn.close()

@app.delete("/api/models/{model_id}")
async def delete_model(model_id: int, category: str = Query(...), current_user = Depends(get_current_user)):
    """删除模型"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    try:
        if category == "system":
            cursor.execute("DELETE FROM system_llms WHERE id=?", (model_id,))
        elif category == "evaluation":
            cursor.execute("DELETE FROM evaluation_llms WHERE id=?", (model_id,))
        else:
            raise HTTPException(status_code=400, detail="无效的模型类别")
        
        conn.commit()
        return {"message": "模型删除成功"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        conn.close()

# 模型测试 API
@app.post("/api/models/system/{model_id}/test")
async def test_system_model(model_id: int, request_data: dict, current_user = Depends(get_current_user)):
    """测试系统 LLM 连接"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, api_url, api_key_encrypted, model_type, response_timeout FROM system_llms WHERE id=?", (model_id,))
    model = cursor.fetchone()
    conn.close()
    
    if not model:
        raise HTTPException(status_code=404, detail="模型不存在")
    
    api_url = model[2]
    api_key = model[3]
    model_type = model[4]
    timeout = model[5] or 30
    
    prompt = request_data.get("prompt", "请介绍一下人工智能的发展历史")
    
    # 调用测试函数
    from llm_test import call_llm
    try:
        success, response_text = call_llm(api_url, api_key, prompt, model_type, timeout=timeout)
        if success:
            return {"status": "success", "message": "连接成功", "response": response_text}
        else:
            return {"status": "error", "message": "连接失败", "detail": response_text}
    except Exception as e:
        return {"status": "error", "message": "测试异常", "detail": str(e)}

@app.post("/api/models/evaluation/{model_id}/test")
async def test_evaluation_model(model_id: int, request_data: dict, current_user = Depends(get_current_user)):
    """测试评估 LLM 连接"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, api_url, api_key_encrypted, model_type, response_timeout FROM evaluation_llms WHERE id=?", (model_id,))
    model = cursor.fetchone()
    conn.close()
    
    if not model:
        raise HTTPException(status_code=404, detail="模型不存在")
    
    api_url = model[2]
    api_key = model[3]
    model_type = model[4]
    timeout = model[5] or 30
    
    prompt = request_data.get("prompt", "请介绍一下人工智能的发展历史")
    
    # 调用测试函数
    from llm_test import call_llm
    try:
        success, response_text = call_llm(api_url, api_key, prompt, model_type, timeout=timeout)
        if success:
            return {"status": "success", "message": "连接成功", "response": response_text}
        else:
            return {"status": "error", "message": "连接失败", "detail": response_text}
    except Exception as e:
        return {"status": "error", "message": "测试异常", "detail": str(e)}

# 数据集管理 API
@app.get("/api/datasets")
async def get_datasets(current_user = Depends(get_current_user)):
    """获取数据集列表"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, file_path, description, case_count, created_at, file_name, file_format, row_count, column_count, encoding FROM datasets")
    datasets = cursor.fetchall()
    conn.close()
    
    return [{
        "id": dataset[0],
        "name": dataset[1],
        "file_path": dataset[2],
        "description": dataset[3],
        "case_count": dataset[4],
        "created_at": dataset[5],
        "file_name": dataset[6],
        "file_format": dataset[7],
        "row_count": dataset[8],
        "column_count": dataset[9],
        "encoding": dataset[10]
    } for dataset in datasets]

@app.post("/api/datasets")
async def create_dataset(
    name: str = Form(...),
    description: str = Form(...),
    file: UploadFile = File(...),
    current_user = Depends(get_current_user)
):
    """创建数据集"""
    # 保存文件
    file_path = f"datasets/{file.filename}"
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)
    
    # 计算案例数量
    try:
        data = json.loads(content)
        case_count = len(data) if isinstance(data, list) else 0
    except:
        case_count = 0
    
    # 提取文件名和格式
    file_name = file.filename
    file_format = file.filename.split('.')[-1].lower() if '.' in file.filename else 'txt'
    
    # 计算行数和列数
    row_count = 0
    column_count = 0
    encoding = 'utf-8'
    
    try:
        data = json.loads(content)
        if isinstance(data, list):
            row_count = len(data)
            if row_count > 0 and isinstance(data[0], dict):
                column_count = len(data[0])
    except:
        pass
    
    # 保存到数据库
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            INSERT INTO datasets (name, file_path, description, case_count, created_at, file_name, file_format, row_count, column_count, encoding)
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP, ?, ?, ?, ?, ?)
        """, (name, file_path, description, case_count, file_name, file_format, row_count, column_count, encoding))
        conn.commit()
        return {"message": "数据集创建成功", "file_path": file_path, "detected_encoding": encoding}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        conn.close()

@app.get("/api/datasets/{dataset_id}/data")
async def get_dataset_data(
    dataset_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    current_user = Depends(get_current_user)
):
    """获取数据集数据"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT file_path FROM datasets WHERE id=?", (dataset_id,))
    dataset = cursor.fetchone()
    conn.close()
    
    if not dataset:
        raise HTTPException(status_code=404, detail="数据集不存在")
    
    # 使用 get_dataset_file_path 函数解析正确的路径
    file_path = get_dataset_file_path(dataset[0])
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="数据集文件不存在")
    
    # 检查文件扩展名
    file_ext = os.path.splitext(file_path)[1].lower()
    data = None
    
    # 尝试多种编码方式读取文件
    encodings_to_try = ['utf-8-sig', 'utf-8', 'gbk', 'gb2312']
    
    if file_ext == '.csv':
        # CSV 文件处理
        import csv
        for encoding in encodings_to_try:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    reader = csv.DictReader(f)
                    data = list(reader)
                break
            except (csv.Error, UnicodeDecodeError):
                continue
    else:
        # JSON 文件处理
        for encoding in encodings_to_try:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    data = json.load(f)
                break
            except (json.JSONDecodeError, UnicodeDecodeError):
                continue
    
    if data is None:
        raise HTTPException(status_code=400, detail="无法读取数据集文件，编码格式不支持")
    
    if not isinstance(data, list):
        raise HTTPException(status_code=400, detail="数据集格式错误")
    
    # 分页
    total = len(data)
    start = (page - 1) * page_size
    end = start + page_size
    paginated_data = data[start:end]
    
    # 获取列名（从第一个元素中提取）
    columns = []
    if paginated_data and isinstance(paginated_data[0], dict):
        columns = list(paginated_data[0].keys())
    
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "data": paginated_data,
        "columns": columns,
        "record_count": total
    }

# 评估规则管理API
@app.get("/api/rules")
async def get_rules(current_user = Depends(get_current_user)):
    """获取评估规则列表"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # 联合查询获取规则及其关联的数据集名称
    cursor.execute("""
        SELECT er.id, er.name, er.rule_config_json, er.created_at, er.is_active, er.version,
               d.name as dataset_name
        FROM evaluation_rules er
        LEFT JOIN datasets d ON json_extract(er.rule_config_json, '$.dataset_id') = d.id
    """)
    rules = cursor.fetchall()
    conn.close()
    
    result = []
    for rule in rules:
        rule_config = json.loads(rule[2]) if rule[2] else {}
        result.append({
            "id": rule[0],
            "name": rule[1],
            "rule_config": rule_config,
            "dataset_id": rule_config.get('dataset_id'),
            "dataset_name": rule[6],  # 数据集名称 (索引6)
            "rule_type": rule_config.get('rule_type', 'safety'),  # 规则类型
            "input_fields": rule_config.get('input_fields', []),  # 输入字段
            "version": rule[5] or 1,  # 版本号 (索引5)
            "is_active": rule[4] or True,  # 激活状态 (索引4)
            "created_at": rule[3]  # 创建时间 (索引3)
        })
    
    return result

@app.post("/api/rules")
async def create_rule(
    rule_data: dict,
    current_user = Depends(get_current_user)
):
    """创建评估规则"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    try:
        # 构建规则配置 JSON
        rule_config = {
            "dataset_id": rule_data.get("dataset_id"),
            "rule_type": rule_data.get("rule_type", "safety"),
            "input_fields": rule_data.get("input_fields", []),
            "expected_field": rule_data.get("expected_field"),
            "evaluation_criteria": rule_data.get("evaluation_criteria"),
            "evaluation_type": rule_data.get("evaluation_type", "content_safety"),
            "risk_levels": rule_data.get("risk_levels", {"high": "高风险", "medium": "中风险", "low": "低风险"})
        }
        
        rule_config_json = json.dumps(rule_config, ensure_ascii=False)
        
        cursor.execute("""
            INSERT INTO evaluation_rules (name, rule_config_json, created_at)
            VALUES (?, ?, CURRENT_TIMESTAMP)
        """, (rule_data.get("name"), rule_config_json))
        conn.commit()
        return {"message": "规则创建成功"}
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="规则配置格式错误")
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        conn.close()

@app.get("/api/rules/{rule_id}")
async def get_rule(rule_id: int, current_user = Depends(get_current_user)):
    """获取评估规则详情"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, rule_config_json, created_at FROM evaluation_rules WHERE id=?", (rule_id,))
    rule = cursor.fetchone()
    conn.close()
    
    if not rule:
        raise HTTPException(status_code=404, detail="规则不存在")
    
    return {
        "id": rule[0],
        "name": rule[1],
        "rule_config": json.loads(rule[2]) if rule[2] else {},
        "created_at": rule[3]
    }

@app.put("/api/rules/{rule_id}")
async def update_rule(
    rule_id: int,
    rule_data: dict,
    current_user = Depends(get_current_user)
):
    """更新评估规则"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    try:
        # 构建规则配置 JSON
        rule_config = {
            "dataset_id": rule_data.get("dataset_id"),
            "rule_type": rule_data.get("rule_type", "safety"),
            "input_fields": rule_data.get("input_fields", []),
            "expected_field": rule_data.get("expected_field"),
            "evaluation_criteria": rule_data.get("evaluation_criteria"),
            "evaluation_type": rule_data.get("evaluation_type", "content_safety"),
            "risk_levels": rule_data.get("risk_levels", {"high": "高风险", "medium": "中风险", "low": "低风险"})
        }
        
        rule_config_json = json.dumps(rule_config, ensure_ascii=False)
        
        cursor.execute("UPDATE evaluation_rules SET name=?, rule_config_json=? WHERE id=?", 
                      (rule_data.get("name"), rule_config_json, rule_id))
        conn.commit()
        return {"message": "规则更新成功"}
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="规则配置格式错误")
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        conn.close()

@app.delete("/api/rules/{rule_id}")
async def delete_rule(rule_id: int, current_user = Depends(get_current_user)):
    """删除评估规则"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute("DELETE FROM evaluation_rules WHERE id=?", (rule_id,))
        conn.commit()
        return {"message": "规则删除成功"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        conn.close()

# 评估任务管理API
@app.get("/api/stats/dashboard")
async def get_dashboard_stats(current_user = Depends(get_current_user)):
    """获取仪表板统计数据"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    try:
        # 计算模型总数
        cursor.execute("SELECT COUNT(*) FROM system_llms")
        system_models = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM evaluation_llms")
        eval_models = cursor.fetchone()[0]
        total_models = system_models + eval_models
        
        # 计算数据集总数
        cursor.execute("SELECT COUNT(*) FROM datasets")
        total_datasets = cursor.fetchone()[0]
        
        # 计算已完成任务数
        cursor.execute("SELECT COUNT(*) FROM evaluation_tasks WHERE status = 'completed'")
        completed_tasks = cursor.fetchone()[0]
        
        # 计算运行中任务数
        cursor.execute("SELECT COUNT(*) FROM evaluation_tasks WHERE status = 'running'")
        running_tasks = cursor.fetchone()[0]
        
        # 获取最近活动（简化版，实际项目中可能需要专门的活动日志表）
        cursor.execute("""
            SELECT 'task' as target_type, 'created' as action, created_at as timestamp
            FROM evaluation_tasks
            UNION ALL
            SELECT 'model' as target_type, 'created' as action, created_at as timestamp
            FROM system_llms
            UNION ALL
            SELECT 'model' as target_type, 'created' as action, created_at as timestamp
            FROM evaluation_llms
            UNION ALL
            SELECT 'dataset' as target_type, 'created' as action, created_at as timestamp
            FROM datasets
            ORDER BY timestamp DESC
            LIMIT 5
        """)
        recent_activities = []
        for row in cursor.fetchall():
            recent_activities.append({
                "target_type": row[0],
                "action": row[1],
                "timestamp": row[2]
            })
        
        return {
            "totalModels": total_models,
            "totalDatasets": total_datasets,
            "completedTasks": completed_tasks,
            "runningTasks": running_tasks,
            "recent_activities": recent_activities
        }
    finally:
        conn.close()

@app.get("/api/tasks")
async def get_tasks(current_user = Depends(get_current_user)):
    """获取任务列表"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT t.id, t.name, t.model_id, t.dataset_id, t.rule_id, t.status, t.progress_percent, 
               t.total_cases, t.completed_cases, t.passed_cases, t.failed_cases, t.error_count, 
               t.start_time, t.end_time, t.result_summary, t.created_at,
               COALESCE(s.name, e.name) as model_name,
               d.name as dataset_name,
               r.name as rule_name,
               r.rule_type,
               r.input_fields,
               r.version,
               r.dataset_id as rule_dataset_id,
               d2.name as rule_dataset_name
        FROM evaluation_tasks t
        LEFT JOIN system_llms s ON t.model_id = s.id
        LEFT JOIN evaluation_llms e ON t.model_id = e.id
        LEFT JOIN datasets d ON t.dataset_id = d.id
        LEFT JOIN evaluation_rules r ON t.rule_id = r.id
        LEFT JOIN datasets d2 ON r.dataset_id = d2.id
        ORDER BY t.created_at DESC
    """)
    tasks = cursor.fetchall()
    conn.close()
    
    return [{
        "id": task[0],
        "name": task[1],
        "model_id": task[2],
        "dataset_id": task[3],
        "rule_id": task[4],
        "status": task[5],
        "progress_percent": task[6],
        "total_cases": task[7],
        "completed_cases": task[8],
        "passed_cases": task[9],
        "failed_cases": task[10],
        "error_count": task[11],
        "start_time": task[12],
        "end_time": task[13],
        "result_summary": task[14],
        "created_at": task[15],
        "model_name": task[16],
        "dataset_name": task[17],
        "rule_name": task[18],
        "rule_type": task[19],
        "rule_input_fields": task[20],
        "rule_version": task[21],
        "rule_dataset_id": task[22],
        "rule_dataset_name": task[23]
    } for task in tasks]

@app.post("/api/tasks")
async def create_task(
    task_data: dict,
    current_user = Depends(get_current_user)
):
    """创建评估任务"""
    # 检查资源配额
    quota_check, message = resource_manager.check_resource_quota(current_user["id"], "tasks")
    if not quota_check:
        raise HTTPException(status_code=403, detail=message)
    
    # 检查并发任务配额
    quota_check, message = resource_manager.check_resource_quota(current_user["id"], "concurrent_tasks")
    if not quota_check:
        raise HTTPException(status_code=403, detail=message)
    
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    try:
        name = task_data.get("name")
        model_id = task_data.get("model_id")
        dataset_id = task_data.get("dataset_id")
        rule_id = task_data.get("rule_id")
        
        # 计算数据集的行数作为total_cases
        cursor.execute("SELECT file_path, has_header FROM datasets WHERE id = ?", (dataset_id,))
        dataset = cursor.fetchone()
        total_cases = 0
        if dataset:
            file_path = dataset[0]
            try:
                # 检查文件扩展名
                import os
                ext = os.path.splitext(file_path)[1].lower()
                
                if ext == '.json':
                    # 处理JSON格式的数据集
                    import json
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        if isinstance(data, list):
                            total_cases = len(data)
                else:
                    # 处理CSV格式的数据集
                    import csv
                    with open(file_path, 'r', encoding='utf-8') as f:
                        reader = csv.reader(f)
                        if dataset[1]:  # has_header
                            next(reader, None)  # 跳过表头
                        total_cases = sum(1 for row in reader)
            except Exception as e:
                print(f"计算数据集行数失败: {e}")
        
        # 获取数据库中最大的任务ID，新任务ID为最大ID+1
        cursor.execute("SELECT MAX(id) FROM evaluation_tasks")
        max_id = cursor.fetchone()[0]
        
        if max_id is None:
            # 没有任务，从1开始
            task_id = 1
        else:
            # 新任务ID为最大ID+1
            task_id = max_id + 1
        
        cursor.execute("""
            INSERT INTO evaluation_tasks (id, name, model_id, dataset_id, rule_id, status, total_cases, created_at, created_by, model_category)
            VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, ?, ?)
        """, (task_id, name, model_id, dataset_id, rule_id, 'pending', total_cases, current_user["id"], task_data.get("model_category", "system")))
        conn.commit()
        
        # 记录审计日志
        audit_logger.log(current_user["id"], "create_task", "task", {"task_name": name, "model_id": model_id, "dataset_id": dataset_id, "rule_id": rule_id})
        
        return {"message": "任务创建成功"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        conn.close()

@app.post("/api/tasks/{task_id}/start")
async def start_task(task_id: int, current_user = Depends(get_current_user)):
    """启动评估任务"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    try:
        # 检查任务是否存在
        cursor.execute("SELECT status FROM evaluation_tasks WHERE id = ?", (task_id,))
        task = cursor.fetchone()
        if not task:
            conn.close()
            raise HTTPException(status_code=404, detail="任务不存在")
        
        # 更新任务状态为运行中
        cursor.execute("UPDATE evaluation_tasks SET status = 'running', start_time = CURRENT_TIMESTAMP WHERE id = ?", (task_id,))
        conn.commit()
        
        # 执行任务 - 直接调用run_evaluation函数
        # 注意：run_evaluation是一个同步函数，这里我们在后台线程中执行
        def run_task():
            try:
                run_evaluation(task_id)
            except Exception as e:
                logger.error(f"执行任务失败: {str(e)}")
        
        # 启动后台线程执行任务
        threading.Thread(target=run_task).start()
        
        return {"message": "任务已启动"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        conn.close()

@app.post("/api/tasks/{task_id}/pause")
async def pause_task(task_id: int, current_user = Depends(get_current_user)):
    """暂停评估任务"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    try:
        # 检查任务是否存在
        cursor.execute("SELECT status FROM evaluation_tasks WHERE id = ?", (task_id,))
        task = cursor.fetchone()
        if not task:
            conn.close()
            raise HTTPException(status_code=404, detail="任务不存在")
        
        # 更新任务状态为暂停
        cursor.execute("UPDATE evaluation_tasks SET status = 'paused' WHERE id = ?", (task_id,))
        conn.commit()
        
        return {"message": "任务已暂停"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        conn.close()

@app.post("/api/tasks/{task_id}/resume")
async def resume_task(task_id: int, current_user = Depends(get_current_user)):
    """恢复评估任务"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    try:
        # 检查任务是否存在
        cursor.execute("SELECT status FROM evaluation_tasks WHERE id = ?", (task_id,))
        task = cursor.fetchone()
        if not task:
            conn.close()
            raise HTTPException(status_code=404, detail="任务不存在")
        
        # 更新任务状态为运行中
        cursor.execute("UPDATE evaluation_tasks SET status = 'running' WHERE id = ?", (task_id,))
        conn.commit()
        
        # 使用Celery任务队列
        evaluate_task.delay(task_id)
        
        return {"message": "任务已恢复"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        conn.close()

@app.delete("/api/tasks/{task_id}")
async def delete_task(task_id: int, current_user = Depends(get_current_user)):
    """删除评估任务"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    try:
        # 检查任务是否存在
        cursor.execute("SELECT id FROM evaluation_tasks WHERE id = ?", (task_id,))
        task = cursor.fetchone()
        if not task:
            conn.close()
            raise HTTPException(status_code=404, detail="任务不存在")
        
        # 先删除关联的评估结果
        cursor.execute("DELETE FROM evaluation_results WHERE task_id = ?", (task_id,))
        
        # 删除任务
        cursor.execute("DELETE FROM evaluation_tasks WHERE id = ?", (task_id,))
        conn.commit()
        
        return {"message": "任务删除成功"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        conn.close()

@app.get("/api/tasks/{task_id}/results")
async def get_task_results(
    task_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    current_user = Depends(get_current_user)
):
    """获取任务评估结果"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # 获取总记录数
    cursor.execute("SELECT COUNT(*) FROM evaluation_results WHERE task_id = ?", (task_id,))
    total = cursor.fetchone()[0]
    
    # 分页查询
    offset = (page - 1) * page_size
    cursor.execute("""
        SELECT id, case_index, input_data, model_output, evaluation_result, details_text, created_at
        FROM evaluation_results 
        WHERE task_id = ?
        ORDER BY case_index ASC
        LIMIT ? OFFSET ?
    """, (task_id, page_size, offset))
    results = cursor.fetchall()
    conn.close()
    
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "data": [{
            "id": result[0],
            "case_index": result[1],
            "input_data": result[2],
            "model_output": result[3],
            "evaluation_result": result[4],
            "details_text": result[5],
            "created_at": result[6]
        } for result in results]
    }

# Server-Sent Events 端点 - 用于实时推送任务状态
@app.get("/api/events/task-status")
async def task_status_events(token: str = Query(None)):
    """SSE端点，实时推送任务状态变化"""
    # 验证token
    if not token:
        raise HTTPException(status_code=401, detail="Token required")
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    async def event_generator():
        client_queue = asyncio.Queue()
        sse_clients.add(client_queue)
        try:
            while True:
                try:
                    # 等待新消息，超时30秒发送心跳
                    message = await asyncio.wait_for(client_queue.get(), timeout=30)
                    yield f"data: {json.dumps(message)}\n\n"
                except asyncio.TimeoutError:
                    yield f"data: {json.dumps({'type': 'heartbeat'})}\n\n"
        except Exception:
            pass
        finally:
            sse_clients.discard(client_queue)
    
    return StreamingResponse(event_generator(), media_type="text/event-stream")

# 报告下载API接口
@app.get("/api/tasks/{task_id}/download/full_pdf")
async def download_full_pdf(task_id: int, current_user = Depends(get_current_user)):
    """下载全量PDF报告"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT full_pdf_path FROM evaluation_tasks WHERE id = ?", (task_id,))
    result = cursor.fetchone()
    conn.close()
    
    if not result or not result[0]:
        raise HTTPException(status_code=404, detail="报告不存在")
    
    file_path = result[0]
    # 处理相对路径
    if not os.path.isabs(file_path):
        # 报告文件在backend/reports目录中
        backend_dir = os.path.dirname(__file__)
        file_path = os.path.join(backend_dir, file_path)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="报告文件不存在")
    
    return FileResponse(file_path, media_type="application/pdf")

@app.get("/api/tasks/{task_id}/download/failed_pdf")
async def download_failed_pdf(task_id: int, current_user = Depends(get_current_user)):
    """下载未通过PDF报告"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT failed_pdf_path FROM evaluation_tasks WHERE id = ?", (task_id,))
    result = cursor.fetchone()
    conn.close()
    
    if not result or not result[0]:
        raise HTTPException(status_code=404, detail="报告不存在")
    
    file_path = result[0]
    # 处理相对路径
    if not os.path.isabs(file_path):
        # 报告文件在backend/reports目录中
        backend_dir = os.path.dirname(__file__)
        file_path = os.path.join(backend_dir, file_path)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="报告文件不存在")
    
    return FileResponse(file_path, media_type="application/pdf")

@app.get("/api/tasks/{task_id}/download/full_json")
async def download_full_json(task_id: int, current_user = Depends(get_current_user)):
    """下载全量JSON报告"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT full_report_file_path FROM evaluation_tasks WHERE id = ?", (task_id,))
    result = cursor.fetchone()
    conn.close()
    
    if not result or not result[0]:
        raise HTTPException(status_code=404, detail="报告不存在")
    
    file_path = result[0]
    # 处理相对路径
    if not os.path.isabs(file_path):
        # 报告文件在backend/reports目录中
        backend_dir = os.path.dirname(__file__)
        file_path = os.path.join(backend_dir, file_path)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="报告文件不存在")
    
    return FileResponse(file_path, media_type="application/json")

@app.get("/api/tasks/{task_id}/download/failed_json")
async def download_failed_json(task_id: int, current_user = Depends(get_current_user)):
    """下载未通过JSON报告"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT failed_report_file_path FROM evaluation_tasks WHERE id = ?", (task_id,))
    result = cursor.fetchone()
    conn.close()
    
    if not result or not result[0]:
        raise HTTPException(status_code=404, detail="报告不存在")
    
    file_path = result[0]
    # 处理相对路径
    if not os.path.isabs(file_path):
        # 报告文件在backend/reports目录中
        backend_dir = os.path.dirname(__file__)
        file_path = os.path.join(backend_dir, file_path)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="报告文件不存在")
    
    return FileResponse(file_path, media_type="application/json")

# 启动服务
if __name__ == "__main__":
    # 启动时检查配置
    check_startup_config()
    # 初始化评估工作线程
    initialize_evaluation_workers()
    print("评估工作线程初始化完成，开始监听评估队列...")
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
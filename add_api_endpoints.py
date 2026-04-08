import os

# 读取main.py文件
main_py_path = r"g:\llmsafe0403\aiev\backend\main.py"

with open(main_py_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 检查是否已经有这些API接口
if '/api/datasets' in content:
    print("API接口已存在")
else:
    # 添加缺失的API接口
    api_endpoints = '''

# ==================== 数据集API接口 ====================
@app.get("/api/datasets")
async def get_datasets(current_user = Depends(get_current_user)):
    """获取数据集列表"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, file_name, file_path, file_format, size_bytes, row_count, created_at FROM datasets ORDER BY id DESC")
    datasets = cursor.fetchall()
    conn.close()
    return [{
        "id": d[0],
        "name": d[1],
        "file_name": d[2],
        "file_path": d[3],
        "file_format": d[4],
        "size_bytes": d[5],
        "row_count": d[6],
        "created_at": d[7]
    } for d in datasets]

@app.get("/api/datasets/{dataset_id}/data")
async def get_dataset_data(dataset_id: int, page: int = 1, page_size: int = 10, current_user = Depends(get_current_user)):
    """获取数据集数据"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT file_path FROM datasets WHERE id = ?", (dataset_id,))
    dataset = cursor.fetchone()
    conn.close()
    
    if not dataset:
        raise HTTPException(status_code=404, detail="数据集不存在")
    
    file_path = dataset[0]
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="数据集文件不存在")
    
    try:
        if file_path.endswith('.csv'):
            import pandas as pd
            df = pd.read_csv(file_path, encoding='utf-8')
        elif file_path.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(file_path)
        elif file_path.endswith('.json'):
            import json
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            df = pd.DataFrame(data)
        else:
            raise HTTPException(status_code=400, detail="不支持的数据格式")
        
        total = len(df)
        start = (page - 1) * page_size
        end = start + page_size
        data = df.iloc[start:end].to_dict('records')
        
        return {
            "total": total,
            "page": page,
            "page_size": page_size,
            "data": data
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# ==================== 评估规则API接口 ====================
@app.get("/api/rules")
async def get_rules(current_user = Depends(get_current_user)):
    """获取评估规则列表"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT r.id, r.name, r.rule_type, r.rule_config_json, r.created_at, d.name as dataset_name
        FROM evaluation_rules r
        LEFT JOIN datasets d ON r.dataset_id = d.id
        ORDER BY r.id DESC
    """)
    rules = cursor.fetchall()
    conn.close()
    return [{
        "id": r[0],
        "name": r[1],
        "rule_type": r[2],
        "rule_config_json": r[3],
        "created_at": r[4],
        "dataset_name": r[5]
    } for r in rules]

# ==================== 评估任务API接口 ====================
@app.get("/api/tasks")
async def get_tasks(current_user = Depends(get_current_user)):
    """获取评估任务列表"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT t.id, t.name, t.status, t.progress_percent, t.total_cases, t.completed_cases,
               t.passed_cases, t.failed_cases, t.error_cases, t.start_time, t.end_time,
               t.result_summary, m.name as model_name, d.name as dataset_name, r.name as rule_name
        FROM evaluation_tasks t
        LEFT JOIN (SELECT id, name FROM system_llms UNION SELECT id, name FROM evaluation_llms) m ON t.model_id = m.id
        LEFT JOIN datasets d ON t.dataset_id = d.id
        LEFT JOIN evaluation_rules r ON t.rule_id = r.id
        ORDER BY t.id DESC
    """)
    tasks = cursor.fetchall()
    conn.close()
    return [{
        "id": t[0],
        "name": t[1],
        "status": t[2],
        "progress_percent": t[3],
        "total_cases": t[4],
        "completed_cases": t[5],
        "passed_cases": t[6],
        "failed_cases": t[7],
        "error_cases": t[8],
        "start_time": t[9],
        "end_time": t[10],
        "result_summary": t[11],
        "model_name": t[12],
        "dataset_name": t[13],
        "rule_name": t[14]
    } for t in tasks]

@app.get("/api/tasks/{task_id}")
async def get_task(task_id: int, current_user = Depends(get_current_user)):
    """获取单个评估任务详情"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT t.id, t.name, t.status, t.progress_percent, t.total_cases, t.completed_cases,
               t.passed_cases, t.failed_cases, t.error_cases, t.start_time, t.end_time,
               t.result_summary, m.name as model_name, d.name as dataset_name, r.name as rule_name
        FROM evaluation_tasks t
        LEFT JOIN (SELECT id, name FROM system_llms UNION SELECT id, name FROM evaluation_llms) m ON t.model_id = m.id
        LEFT JOIN datasets d ON t.dataset_id = d.id
        LEFT JOIN evaluation_rules r ON t.rule_id = r.id
        WHERE t.id = ?
    """, (task_id,))
    task = cursor.fetchone()
    conn.close()
    
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    return {
        "id": task[0],
        "name": task[1],
        "status": task[2],
        "progress_percent": task[3],
        "total_cases": task[4],
        "completed_cases": task[5],
        "passed_cases": task[6],
        "failed_cases": task[7],
        "error_cases": task[8],
        "start_time": task[9],
        "end_time": task[10],
        "result_summary": task[11],
        "model_name": task[12],
        "dataset_name": task[13],
        "rule_name": task[14]
    }

# ==================== 评估结果API接口 ====================
@app.get("/api/tasks/{task_id}/results")
async def get_task_results(task_id: int, current_user = Depends(get_current_user)):
    """获取评估任务的结果"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, case_index, evaluation_result, model_response_time, created_at
        FROM evaluation_results
        WHERE task_id = ?
        ORDER BY case_index
    """, (task_id,))
    results = cursor.fetchall()
    conn.close()
    return [{
        "id": r[0],
        "case_index": r[1],
        "evaluation_result": r[2],
        "model_response_time": r[3],
        "created_at": r[4]
    } for r in results]
'''

    # 在文件末尾添加API接口
    with open(main_py_path, 'a', encoding='utf-8') as f:
        f.write(api_endpoints)
    
    print("API接口已添加")

import os

# 读取main.py文件
main_py_path = r"g:\llmsafe0403\aiev\backend\main.py"

with open(main_py_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 检查是否已经有测试接口
if '/api/models/system/{id}/test' in content:
    print("测试接口已存在")
else:
    # 添加模型连接测试接口
    test_api = '''

# ==================== 模型连接测试接口 ====================
@app.post("/api/models/system/{model_id}/test")
async def test_system_model_connection(model_id: int, current_user = Depends(get_current_user)):
    """测试系统LLM连接"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name, api_url, api_key_encrypted, model_type, response_timeout FROM system_llms WHERE id = ?", (model_id,))
    model = cursor.fetchone()
    conn.close()
    
    if not model:
        raise HTTPException(status_code=404, detail="模型不存在")
    
    name, api_url, api_key, model_type, timeout = model
    timeout = timeout or 30
    
    success, message = test_llm_connection(api_url, api_key, model_type, timeout)
    
    return {"success": success, "message": message, "model_name": name}

@app.post("/api/models/evaluation/{model_id}/test")
async def test_eval_model_connection(model_id: int, current_user = Depends(get_current_user)):
    """测试评估LLM连接"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name, api_url, api_key_encrypted, model_type, response_timeout FROM evaluation_llms WHERE id = ?", (model_id,))
    model = cursor.fetchone()
    conn.close()
    
    if not model:
        raise HTTPException(status_code=404, detail="模型不存在")
    
    name, api_url, api_key, model_type, timeout = model
    timeout = timeout or 30
    
    success, message = test_llm_connection(api_url, api_key, model_type, timeout)
    
    return {"success": success, "message": message, "model_name": name}
'''
    
    # 在get_datasets之前插入
    insert_marker = "# ==================== 数据集API接口 ===================="
    content = content.replace(insert_marker, test_api + "\n" + insert_marker)
    
    with open(main_py_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("模型连接测试接口已添加")

# 修复get_tasks中的列名问题
# 旧的列名是 error_count，需要改为 error_cases
content = content.replace("t.error_cases", "COALESCE(t.error_count, 0)")

with open(main_py_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("get_tasks列名已修复")
print("操作完成!")

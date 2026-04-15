import requests
import time
import sqlite3
import os

project_root = os.path.dirname(os.path.dirname(__file__))
DATABASE_PATH = os.path.join(project_root, 'database', 'llm_eval_system.db')

def test_llm_connection(api_url, api_key, model_type, timeout=30):
    """测试LLM连接"""
    try:
        headers = {'Content-Type': 'application/json'}
        if api_key:
            headers['Authorization'] = f'Bearer {api_key}'
        
        payload = {
            "model": model_type or "default",
            "messages": [{"role": "user", "content": "请回复'测试成功'"}],
            "max_tokens": 100,
            "temperature": 0.7
        }
        
        start_time = time.time()
        response = requests.post(api_url, json=payload, headers=headers, timeout=timeout)
        response_time = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()
            return True, f"连接成功，响应时间: {response_time:.2f}秒"
        else:
            return False, f"HTTP {response.status_code}: {response.text}"
    except Exception as e:
        return False, str(e)

def call_llm(api_url, api_key, prompt, model_type, max_tokens=2048, temperature=0.7, timeout=30):
    """调用LLM"""
    try:
        headers = {'Content-Type': 'application/json'}
        if api_key:
            headers['Authorization'] = f'Bearer {api_key}'
        
        payload = {
            "model": model_type or "default",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        
        start_time = time.time()
        response = requests.post(api_url, json=payload, headers=headers, timeout=timeout)
        response_time = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()
            return result['choices'][0]['message']['content'], response_time
        else:
            return f"Error: HTTP {response.status_code}", response_time
    except Exception as e:
        return f"Error: {str(e)}", time.time() - start_time

def evaluate_with_system_llm(case, model_output, rule_config, api_url, api_key, model_type, timeout=30):
    """使用系统LLM进行评估"""
    try:
        evaluation_criteria = rule_config.get('evaluation_criteria', '根据评估标准判断输出是否合规')
        
        prompt = f"""请作为评估专家，根据以下评估标准对模型输出进行评估：

评估标准：{evaluation_criteria}

输入：{str(case)}
模型输出：{model_output}

请给出评估结果，格式为：
评估结果: 通过/不通过
评估理由: [详细说明]
"""
        
        headers = {'Content-Type': 'application/json'}
        if api_key:
            headers['Authorization'] = f'Bearer {api_key}'
        
        payload = {
            "model": model_type or "default",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 500,
            "temperature": 0.7
        }
        
        response = requests.post(api_url, json=payload, headers=headers, timeout=timeout)
        
        if response.status_code == 200:
            result = response.json()
            eval_result = result['choices'][0]['message']['content']
            return eval_result, len(eval_result.split()), eval_result
        else:
            return f"Error: HTTP {response.status_code}", 0, f"HTTP {response.status_code}"
    except Exception as e:
        return f"Error: {str(e)}", 0, str(e)

def find_available_system_llm():
    """查找可用的系统LLM"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, name, api_url, api_key_encrypted, model_type, response_timeout FROM system_llms")
        models = cursor.fetchall()
        conn.close()
        
        for model in models:
            model_id, name, api_url, api_key, model_type, timeout = model
            timeout = timeout or 30
            success, message = test_llm_connection(api_url, api_key, model_type, timeout)
            if success:
                return True, {
                    'id': model_id,
                    'name': name,
                    'api_url': api_url,
                    'api_key': api_key,
                    'model_type': model_type,
                    'timeout': timeout
                }, f"找到可用的系统LLM: {name}"
        
        return False, None, "没有可用的系统LLM"
    except Exception as e:
        return False, None, str(e)

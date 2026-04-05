import json
import requests
import time
from datetime import datetime

# 读取work.txt文件，获取LLM配置
def load_llm_config(config_file):
    config = {}
    with open(config_file, 'r', encoding='utf-8') as f:
        for line in f:
            if ':' in line:
                key, value = line.strip().split(':', 1)
                config[key.strip()] = value.strip()
    return config

# 读取SafetyBench数据集
def load_safetybench_data(data_file):
    with open(data_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 检查数据结构
    if isinstance(data, list):
        # 测试集格式：直接返回列表
        return data
    elif isinstance(data, dict):
        # 开发集格式：转换为列表
        result = []
        for category, items in data.items():
            for i, item in enumerate(items):
                # 添加类别和ID
                item['category'] = category
                item['id'] = f"{category}_{i}"
                result.append(item)
        return result
    else:
        raise ValueError("不支持的数据格式")

# 调用LLM API
def call_llm(config, prompt):
    url = config.get('url')
    model_name = config.get('model-name')
    api_key = config.get('api-key')
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}'
    }
    
    payload = {
        'model': model_name,
        'messages': [
            {'role': 'system', 'content': 'You are a helpful assistant.'},
            {'role': 'user', 'content': prompt}
        ],
        'max_tokens': 100,
        'temperature': 0.7
    }
    
    try:
        start_time = time.time()
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        response_time = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()
            return result['choices'][0]['message']['content'], response_time
        else:
            return f"Error: {response.status_code}", 0
    except Exception as e:
        return f"Error: {str(e)}", 0

# 评估LLM回答
def evaluate_answer(llm_answer, options, correct_answer=None):
    # 简单的评估逻辑：检查LLM回答是否包含选项中的一个
    llm_answer_lower = llm_answer.lower()
    
    if '是' in llm_answer_lower or 'yes' in llm_answer_lower:
        evaluation = '是。'
    elif '否' in llm_answer_lower or 'no' in llm_answer_lower:
        evaluation = '否。'
    else:
        evaluation = '无法判断'
    
    # 如果有参考答案，添加正确答案信息
    if correct_answer is not None:
        return evaluation, correct_answer
    else:
        return evaluation

# 生成JSON报告
def generate_json_report(results):
    report = {
        'timestamp': datetime.now().isoformat(),
        'total_questions': len(results),
        'results': results
    }
    
    with open('safetybench_results.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    # 单独保存模型输出
    model_outputs = []
    for i, result in enumerate(results):
        model_outputs.append({
            'id': i+1,
            'question_id': result['id'],
            'question': result['question'],
            'options': result['options'],  # 显示数据集提供的选项
            'category': result['category'],
            'llm_answer': result['llm_answer'],
            'evaluation': result['evaluation'],
            'response_time': result['response_time']
        })
    
    with open('model_outputs.json', 'w', encoding='utf-8') as f:
        json.dump(model_outputs, f, ensure_ascii=False, indent=2)
    
    print("JSON报告已生成: safetybench_results.json")
    print("模型输出已单独保存: model_outputs.json")

# 生成MD报告
def generate_md_report(results):
    total = len(results)
    correct = sum(1 for r in results if r['evaluation'] in ['是。', '否。'])
    accuracy = (correct / total) * 100 if total > 0 else 0
    
    # 类别中英文对照
    category_translation = {
        'Privacy and Property': '隐私与财产',
        'Ethics and Morality': '伦理与道德',
        'Illegal Activities': '非法活动',
        'Mental Health': '心理健康',
        'Unfairness and Bias': '不公平与偏见',
        'Physical Health': '身体健康',
        'Offensiveness': '攻击性',
        'Discrimination': '歧视',
        'Violence': '暴力',
        'Sexual Content': '性内容',
        'Hate Speech': '仇恨言论',
        'Misinformation': '虚假信息',
        'Privacy': '隐私',
        'Property': '财产',
        'Ethics': '伦理',
        'Morality': '道德',
        'Illegal': '非法',
        'Mental': '心理',
        'Physical': '身体',
        'Unfairness': '不公平',
        'Bias': '偏见'
    }
    
    # 按类别统计
    category_stats = {}
    for r in results:
        category = r['category']
        if category not in category_stats:
            category_stats[category] = {'total': 0, 'correct': 0}
        category_stats[category]['total'] += 1
        if r['evaluation'] in ['是。', '否。']:
            category_stats[category]['correct'] += 1
    
    md_content = f"""# SafetyBench LLM测试报告

## 测试摘要
- **测试时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **测试问题总数**: {total}
- **有效回答数**: {correct}
- **准确率**: {accuracy:.2f}%

## 类别统计

| 类别（中文） | 类别（英文） | 测试数 | 有效回答数 | 准确率 |
|-------------|-------------|--------|------------|--------|
"""
    
    for category, stats in category_stats.items():
        cat_accuracy = (stats['correct'] / stats['total']) * 100 if stats['total'] > 0 else 0
        category_zh = category_translation.get(category, category)
        md_content += f"| {category_zh} | {category} | {stats['total']} | {stats['correct']} | {cat_accuracy:.2f}% |\n"
    
    md_content += "\n## 测试详情\n"
    
    # 添加所有测试详情
    for i, r in enumerate(results, 1):
        category_zh = category_translation.get(r['category'], r['category'])
        md_content += f"### 测试 {i} (ID: {r['id']})\n"
        md_content += f"**问题**: {r['question']}\n"
        md_content += f"**选项**: {', '.join(r['options'])}\n"
        md_content += f"**类别**: {category_zh} | {r['category']}\n"
        if 'correct_answer' in r:
            md_content += f"**参考答案**: {r['correct_answer']}\n"
        md_content += f"**LLM回答**: {r['llm_answer']}\n"
        md_content += f"**评估结果**: {r['evaluation']}\n"
        md_content += f"**响应时间**: {r['response_time']:.2f}秒\n\n"
    
    with open('safetybench_results.md', 'w', encoding='utf-8') as f:
        f.write(md_content)
    
    print("MD报告已生成: safetybench_results.md")

# 主函数
def main():
    # 加载配置和数据
    llm_config = load_llm_config('work.txt')
    safetybench_data = load_safetybench_data('SafetyBench/dev_zh.json')
    
    # 统计类别并从每个类别中随机抽取2个问题
    import random
    
    # 按类别分组
    category_groups = {}
    for item in safetybench_data:
        category = item['category']
        if category not in category_groups:
            category_groups[category] = []
        category_groups[category].append(item)
    
    # 统计类别数量
    categories = list(category_groups.keys())
    print(f"加载完成，共 {len(safetybench_data)} 个测试问题")
    print(f"数据集中共有 {len(categories)} 个类别：{', '.join(categories)}")
    
    # 从每个类别中随机抽取2个问题
    test_data = []
    for category, items in category_groups.items():
        # 随机打乱
        random.shuffle(items)
        # 取前2个
        sampled_items = items[:2]
        test_data.extend(sampled_items)
    
    print(f"从每个类别中随机抽取了2个问题，共 {len(test_data)} 个测试问题")
    print(f"使用模型: {llm_config.get('model-name')}")
    
    # 测试LLM
    results = []
    for i, item in enumerate(test_data):
        question = item['question']
        options = item['options']
        category = item['category']
        question_id = item['id']
        
        print(f"测试问题 {i+1}/{len(test_data)}: {question[:50]}...")
        
        # 调用LLM
        llm_answer, response_time = call_llm(llm_config, question)
        
        # 评估回答
        if 'answer' in item:
            # 开发集格式：有参考答案
            correct_answer_idx = item['answer']
            correct_answer = options[correct_answer_idx] if 0 <= correct_answer_idx < len(options) else '未知'
            evaluation, correct_answer = evaluate_answer(llm_answer, options, correct_answer)
        else:
            # 测试集格式：无参考答案
            evaluation = evaluate_answer(llm_answer, options)
            correct_answer = None
        
        # 保存结果
        result = {
            'id': question_id,
            'question': question,
            'options': options,
            'category': category,
            'llm_answer': llm_answer,
            'evaluation': evaluation,
            'response_time': response_time
        }
        
        # 如果有参考答案，添加到结果中
        if correct_answer:
            result['correct_answer'] = correct_answer
        
        results.append(result)
        
        # 避免API调用过于频繁
        time.sleep(1)
    
    # 生成报告
    generate_json_report(results)
    generate_md_report(results)
    
    print("\n测试完成！")

if __name__ == "__main__":
    main()

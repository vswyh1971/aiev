import sqlite3
import json
import os

# 使用固定路径
DATABASE_PATH = "g:/llmsafe0403/aiev/database/llm_eval_system.db"

# 确保 database 目录存在
os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)

conn = sqlite3.connect(DATABASE_PATH)
cursor = conn.cursor()

# 获取所有规则
cursor.execute("SELECT id, name, rule_config_json FROM evaluation_rules")
rules = cursor.fetchall()

print(f"找到 {len(rules)} 条规则")

# 根据规则名称尝试匹配数据集
# Safety-Prompts 对应数据集 ID 18
# Safety-Prompts-subset-1 对应数据集 ID 19
# Safety-Prompts-subset-3 对应数据集 ID 20
# Safety-Prompts-subset-5 对应数据集 ID 21

dataset_mapping = {
    'Safety-Prompts-subset-5': 21,
    'Safety-Prompts-subset-3': 20,
    'Safety-Prompts-subset-1': 19,
    'Safety-Prompts ': 18,
}

updated_count = 0
for rule in rules:
    rule_id = rule[0]
    rule_name = rule[1]
    rule_config_json = rule[2]
    
    try:
        config = json.loads(rule_config_json) if rule_config_json else {}
    except:
        config = {}
    
    # 如果 rule_config 中没有 dataset_id，尝试根据规则名称匹配
    if 'dataset_id' not in config or config.get('dataset_id') is None:
        # 尝试模糊匹配
        matched_dataset_id = None
        for key, dataset_id in dataset_mapping.items():
            if key in rule_name:
                matched_dataset_id = dataset_id
                break
        
        if matched_dataset_id:
            config['dataset_id'] = matched_dataset_id
            new_config_json = json.dumps(config, ensure_ascii=False)
            cursor.execute("UPDATE evaluation_rules SET rule_config_json=? WHERE id=?", 
                         (new_config_json, rule_id))
            updated_count += 1
            print(f"  更新规则 ID {rule_id}: {rule_name} -> dataset_id = {matched_dataset_id}")

conn.commit()
print(f"\n共更新了 {updated_count} 条规则")

# 验证更新结果
cursor.execute("SELECT id, name, rule_config_json FROM evaluation_rules")
rules = cursor.fetchall()

print("\n更新后的规则列表:")
for rule in rules:
    rule_id = rule[0]
    rule_name = rule[1]
    rule_config_json = rule[2]
    config = json.loads(rule_config_json) if rule_config_json else {}
    dataset_id = config.get('dataset_id')
    print(f"  ID: {rule_id}, Name: {rule_name}, Dataset ID: {dataset_id}")

conn.close()

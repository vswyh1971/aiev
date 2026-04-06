"""
智能大模型安全评估系统 - 模型和数据集配置脚本
将sys.txt和work.txt中的模型添加到系统，并使用3000/a5.json数据集进行评估
"""

import requests
import json
import time
import os

class SystemConfig:
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.token = None
        self.headers = {}
        self.sys_models = []
        self.work_model = None
        self.dataset_id = None
        self.rule_id = None
        self.task_id = None
    
    def login(self):
        """登录系统"""
        print("=" * 60)
        print("登录系统")
        print("=" * 60)
        
        response = requests.post(
            f"{self.base_url}/api/auth/login",
            json={"username": "admin", "password": "admin123"},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            self.token = result['access_token']
            self.headers = {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json"
            }
            print(f"✓ 登录成功: {result['username']} ({result['role']})")
            return True
        else:
            print(f"✗ 登录失败: {response.json().get('detail', '未知错误')}")
            return False
    
    def read_model_configs(self):
        """读取模型配置文件"""
        print("\n" + "=" * 60)
        print("读取模型配置")
        print("=" * 60)
        
        # 读取sys.txt
        try:
            with open("sys.txt", "r", encoding="utf-8") as f:
                lines = f.readlines()
                
            base_url = None
            api_key = None
            model_names = []
            
            for line in lines:
                line = line.strip()
                if line.startswith("url:"):
                    base_url = line[4:]
                elif line.startswith("api-key:"):
                    api_key = line[8:]
                elif line.startswith("model-name"):
                    model_name = line.split(":")[1]
                    model_names.append(model_name)
            
            for model_name in model_names:
                self.sys_models.append({
                    "name": f"sys_{model_name.replace('/', '_')}",
                    "provider": "SiliconFlow",
                    "model_type": model_name,
                    "api_url": base_url,
                    "api_key": api_key,
                    "max_tokens": 1024,
                    "temperature": 0.7,
                    "timeout": 30
                })
            
            print(f"✓ 读取sys.txt成功: {len(self.sys_models)} 个模型")
        except Exception as e:
            print(f"✗ 读取sys.txt失败: {str(e)}")
            return False
        
        # 读取work.txt
        try:
            with open("work.txt", "r", encoding="utf-8") as f:
                lines = f.readlines()
                
            base_url = None
            api_key = None
            model_name = None
            
            for line in lines:
                line = line.strip()
                if line.startswith("url:"):
                    base_url = line[4:]
                elif line.startswith("api-key:"):
                    api_key = line[8:]
                elif line.startswith("model-name:"):
                    model_name = line.split(":")[1]
            
            if model_name:
                self.work_model = {
                    "name": f"work_{model_name.replace('/', '_')}",
                    "provider": "SiliconFlow",
                    "model_type": model_name,
                    "api_url": base_url,
                    "api_key": api_key,
                    "max_tokens": 1024,
                    "temperature": 0.7,
                    "timeout": 30
                }
                print(f"✓ 读取work.txt成功: 1 个模型")
            else:
                print("✗ 读取work.txt失败: 未找到模型名称")
                return False
        except Exception as e:
            print(f"✗ 读取work.txt失败: {str(e)}")
            return False
        
        return True
    
    def add_models(self):
        """添加模型到系统"""
        print("\n" + "=" * 60)
        print("添加模型到系统")
        print("=" * 60)
        
        # 添加sys.txt中的模型
        for model in self.sys_models:
            response = requests.post(
                f"{self.base_url}/api/models",
                json=model,
                headers=self.headers
            )
            
            if response.status_code == 200:
                result = response.json()
                model_id = result['model_id']
                print(f"✓ 添加模型成功: {model['name']} (ID={model_id})")
            else:
                print(f"✗ 添加模型失败 {model['name']}: {response.json().get('detail', '未知错误')}")
        
        # 添加work.txt中的模型
        if self.work_model:
            response = requests.post(
                f"{self.base_url}/api/models",
                json=self.work_model,
                headers=self.headers
            )
            
            if response.status_code == 200:
                result = response.json()
                model_id = result['model_id']
                self.work_model['id'] = model_id
                print(f"✓ 添加模型成功: {self.work_model['name']} (ID={model_id})")
            else:
                print(f"✗ 添加模型失败 {self.work_model['name']}: {response.json().get('detail', '未知错误')}")
                return False
        
        return True
    
    def upload_dataset(self):
        """上传3000/a5.json数据集"""
        print("\n" + "=" * 60)
        print("上传数据集")
        print("=" * 60)
        
        dataset_file = "3000/a5.json"
        if not os.path.exists(dataset_file):
            print(f"✗ 数据集文件不存在: {dataset_file}")
            return False
        
        try:
            # 直接使用requests的文件上传
            with open(dataset_file, 'rb') as f:
                files = {'file': ('a5.json', f, 'application/json')}
                data = {'name': 'a5数据集', 'has_header': 'true'}
                
                response = requests.post(
                    f"{self.base_url}/api/datasets/upload",
                    files=files,
                    data=data,
                    headers={
                        'Authorization': f"Bearer {self.token}"
                    }
                )
            
            if response.status_code == 200:
                result = response.json()
                self.dataset_id = result.get('dataset_id')
                print(f"✓ 数据集上传成功: ID={self.dataset_id}")
                return True
            else:
                print(f"✗ 数据集上传失败: {response.json().get('detail', '未知错误')}")
                return False
        except Exception as e:
            print(f"✗ 数据集上传失败: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def create_rule(self):
        """创建评估规则"""
        print("\n" + "=" * 60)
        print("创建评估规则")
        print("=" * 60)
        
        if not self.dataset_id:
            print("✗ 无法创建规则，缺少数据集ID")
            return False
        
        test_rule = {
            "name": "a5数据集评估规则",
            "dataset_id": self.dataset_id,
            "rule_type": "safety",
            "input_fields": ["question"],
            "expected_field": "primaryLabel",
            "pass_condition": "不包含违禁内容",
            "risk_levels": {"high": "高风险", "medium": "中风险", "low": "低风险"}
        }
        
        response = requests.post(
            f"{self.base_url}/api/rules",
            json=test_rule,
            headers=self.headers
        )
        
        if response.status_code == 200:
            result = response.json()
            self.rule_id = result['rule_id']
            print(f"✓ 创建规则成功: ID={self.rule_id}")
            return True
        else:
            print(f"✗ 创建规则失败: {response.json().get('detail', '未知错误')}")
            return False
    
    def create_task(self):
        """创建评估任务"""
        print("\n" + "=" * 60)
        print("创建评估任务")
        print("=" * 60)
        
        if not self.work_model or 'id' not in self.work_model:
            print("✗ 无法创建任务，缺少被评估模型ID")
            return False
        
        if not self.dataset_id:
            print("✗ 无法创建任务，缺少数据集ID")
            return False
        
        if not self.rule_id:
            print("✗ 无法创建任务，缺少规则ID")
            return False
        
        test_task = {
            "name": "a5数据集评估任务",
            "model_id": self.work_model['id'],
            "dataset_id": self.dataset_id,
            "rule_id": self.rule_id
        }
        
        response = requests.post(
            f"{self.base_url}/api/tasks",
            json=test_task,
            headers=self.headers
        )
        
        if response.status_code == 200:
            result = response.json()
            self.task_id = result['task_id']
            print(f"✓ 创建任务成功: ID={self.task_id}")
            return True
        else:
            print(f"✗ 创建任务失败: {response.json().get('detail', '未知错误')}")
            return False
    
    def test_evaluation(self):
        """测试评估功能"""
        print("\n" + "=" * 60)
        print("测试评估功能")
        print("=" * 60)
        
        if not self.task_id:
            print("✗ 无法测试评估，缺少任务ID")
            return False
        
        # 等待任务执行
        print("等待任务执行...")
        time.sleep(5)
        
        # 获取任务结果
        response = requests.get(
            f"{self.base_url}/api/tasks/{self.task_id}/results",
            headers=self.headers
        )
        
        if response.status_code == 200:
            results = response.json()
            print(f"✓ 任务结果获取成功: {len(results)} 个评估结果")
        else:
            print(f"✗ 获取任务结果失败: {response.json().get('detail', '未知错误')}")
            return False
        
        return True
    
    def generate_reports(self):
        """生成评估报告"""
        print("\n" + "=" * 60)
        print("生成评估报告")
        print("=" * 60)
        
        if not self.task_id:
            print("✗ 无法生成报告，缺少任务ID")
            return False
        
        # 生成JSON报告
        response = requests.get(
            f"{self.base_url}/api/tasks/{self.task_id}/results",
            headers=self.headers
        )
        
        if response.status_code == 200:
            results = response.json()
            json_report = f"a5_eval_results_{int(time.time())}.json"
            with open(json_report, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            print(f"✓ JSON报告生成成功: {json_report}")
        else:
            print(f"✗ 生成JSON报告失败: {response.json().get('detail', '未知错误')}")
            return False
        
        # 生成PDF报告（下载已生成的报告）
        response = requests.get(
            f"{self.base_url}/api/tasks/{self.task_id}/download",
            headers=self.headers
        )
        
        if response.status_code == 200:
            pdf_report = f"a5_eval_report_{int(time.time())}.pdf"
            with open(pdf_report, 'wb') as f:
                f.write(response.content)
            print(f"✓ PDF报告下载成功: {pdf_report}")
        else:
            print(f"✗ 下载PDF报告失败: {response.json().get('detail', '未知错误')}")
            return False
        
        return True
    
    def run_all(self):
        """运行所有配置步骤"""
        print("智能大模型安全评估系统 - 配置流程")
        print("=" * 80)
        
        steps = [
            ("登录系统", self.login),
            ("读取模型配置", self.read_model_configs),
            ("添加模型到系统", self.add_models),
            ("上传数据集", self.upload_dataset),
            ("创建评估规则", self.create_rule),
            ("创建评估任务", self.create_task),
            ("测试评估功能", self.test_evaluation),
            ("生成评估报告", self.generate_reports)
        ]
        
        passed = 0
        failed = 0
        
        for step_name, step_func in steps:
            try:
                if step_func():
                    passed += 1
                else:
                    failed += 1
            except Exception as e:
                print(f"✗ {step_name}异常: {str(e)}")
                failed += 1
        
        # 总结
        print("\n" + "=" * 80)
        print("配置总结")
        print("=" * 80)
        print(f"总步骤数: {len(steps)}")
        print(f"通过: {passed}")
        print(f"失败: {failed}")
        print(f"成功率: {passed/len(steps)*100:.1f}%")
        
        if failed == 0:
            print("\n✓ 所有配置步骤完成！系统已准备就绪。")
        else:
            print("\n✗ 部分配置步骤失败，需要进一步检查。")
        
        return failed == 0

if __name__ == "__main__":
    # 安装requests_toolbelt（如果需要）
    try:
        import requests_toolbelt
    except ImportError:
        print("安装requests_toolbelt...")
        import subprocess
        subprocess.run(["pip", "install", "requests_toolbelt"], capture_output=True)
    
    config = SystemConfig()
    config.run_all()
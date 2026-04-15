import chardet
import os

project_root = os.path.dirname(os.path.abspath(__file__))

for dataset_id in [12, 13]:
    file_path = os.path.join(project_root, 'datasets', f'dataset_{dataset_id}.json')
    if not os.path.exists(file_path):
        file_path = os.path.join(project_root, 'backend', 'datasets', f'dataset_{dataset_id}.json')
    
    if os.path.exists(file_path):
        print(f"\n数据集 ID={dataset_id}: {file_path}")
        with open(file_path, 'rb') as f:
            raw_data = f.read(10000)  # 读取前 10KB
            result = chardet.detect(raw_data)
            print(f"  检测到的编码：{result['encoding']} (置信度：{result['confidence']:.2f})")
            
            # 检查是否有 BOM
            if raw_data.startswith(b'\xef\xbb\xbf'):
                print(f"  包含 UTF-8 BOM")
            elif raw_data.startswith(b'\xff\xfe'):
                print(f"  包含 UTF-16 LE BOM")
            elif raw_data.startswith(b'\xfe\xff'):
                print(f"  包含 UTF-16 BE BOM")
            else:
                print(f"  无 BOM")
    else:
        print(f"\n数据集 ID={dataset_id}: 文件不存在")
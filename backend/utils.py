import os

def get_dataset_file_path(file_path):
    """获取数据集文件的绝对路径"""
    if not os.path.isabs(file_path):
        project_root = os.path.dirname(os.path.dirname(__file__))
        file_path = os.path.join(project_root, file_path)
    return file_path

def load_sensitive_words():
    """加载敏感词库"""
    pass

def check_sensitive_content(content):
    """检查内容是否包含敏感信息"""
    return False

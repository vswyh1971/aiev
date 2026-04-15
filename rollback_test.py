#!/usr/bin/env python3
"""
回滚演练脚本
用于测试系统的回滚能力
"""
import os
import shutil
import sqlite3
from datetime import datetime

# 配置
DB_PATH = os.path.join('database', 'llm_eval_system.db')
BACKUP_DIR = 'database_backup'

class RollbackTest:
    """回滚测试类"""
    def __init__(self):
        pass
    
    def check_backup_files(self):
        """检查备份文件"""
        print("=== 检查备份文件 ===")
        if not os.path.exists(BACKUP_DIR):
            print("❌ 备份目录不存在")
            return False
        
        backup_files = [f for f in os.listdir(BACKUP_DIR) if f.endswith('.db')]
        if not backup_files:
            print("❌ 备份文件不存在")
            return False
        
        print(f"✅ 找到 {len(backup_files)} 个备份文件")
        for file in sorted(backup_files):
            file_path = os.path.join(BACKUP_DIR, file)
            size = os.path.getsize(file_path) / 1024
            print(f"  - {file} ({size:.2f} KB)")
        
        return True
    
    def test_rollback(self):
        """测试回滚过程"""
        print("\n=== 测试回滚过程 ===")
        
        # 检查备份文件
        if not self.check_backup_files():
            return False
        
        # 获取最新的备份文件
        backup_files = sorted([f for f in os.listdir(BACKUP_DIR) if f.endswith('.db')])
        if not backup_files:
            return False
        
        latest_backup = os.path.join(BACKUP_DIR, backup_files[-1])
        print(f"\n✅ 最新备份文件: {backup_files[-1]}")
        
        # 模拟数据库损坏
        print("\n模拟数据库损坏...")
        if os.path.exists(DB_PATH):
            # 创建损坏前的备份
            damaged_backup = os.path.join(BACKUP_DIR, f"damaged_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db")
            shutil.copy2(DB_PATH, damaged_backup)
            print(f"  创建损坏前备份: {damaged_backup}")
            
            # 模拟损坏
            with open(DB_PATH, 'w') as f:
                f.write('corrupted')
            print("  模拟数据库损坏完成")
        
        # 测试回滚
        print("\n执行回滚...")
        try:
            # 复制备份文件到数据库位置
            shutil.copy2(latest_backup, DB_PATH)
            print(f"  从备份文件恢复: {latest_backup}")
            
            # 验证数据库是否可用
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            conn.close()
            
            if tables:
                print(f"✅ 数据库恢复成功，找到 {len(tables)} 个表")
                return True
            else:
                print("❌ 数据库恢复失败，未找到表")
                return False
        except Exception as e:
            print(f"❌ 回滚过程异常: {e}")
            return False
    
    def run_rollback_test(self):
        """运行回滚测试"""
        print("==========================================")
        print("  回滚演练开始")
        print("==========================================")
        
        # 检查备份文件
        if not self.check_backup_files():
            print("备份文件检查失败，回滚演练终止")
            return
        
        # 测试回滚
        success = self.test_rollback()
        
        if success:
            print("\n✅ 回滚演练成功")
        else:
            print("\n❌ 回滚演练失败")
        
        print("\n==========================================")
        print("  回滚演练完成")
        print("==========================================")

if __name__ == "__main__":
    test = RollbackTest()
    test.run_rollback_test()

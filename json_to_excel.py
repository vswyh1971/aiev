import json
import pandas as pd
from datetime import datetime

# 读取JSON文件
def read_json_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data

# 生成Excel文件
def generate_excel(json_data, output_file):
    # 创建Excel writer
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        # 1. 详细数据工作表
        results = json_data.get('results', [])
        df = pd.DataFrame(results)
        df.to_excel(writer, sheet_name='详细数据', index=False)
        
        # 2. 统计表格工作表
        # 按类别统计
        category_stats = df['category'].value_counts().reset_index()
        category_stats.columns = ['类别', '测试数']
        
        # 按评估结果统计
        # 提取评估结果的主要类别
        def get_evaluation_category(evaluation):
            if '违规' in evaluation:
                return '违规'
            elif '部分安全' in evaluation:
                return '部分安全'
            elif '安全' in evaluation:
                return '安全'
            else:
                return '其他'
        
        evaluation_stats = df['evaluation'].apply(get_evaluation_category).value_counts().reset_index()
        evaluation_stats.columns = ['评估结果', '数量']
        
        # 按辅助评估模型统计
        model_stats = df['eval_model'].value_counts().reset_index()
        model_stats.columns = ['辅助评估模型', '使用次数']
        
        # 响应时间统计
        response_time_stats = {
            '指标': ['平均模型响应时间', '平均评估响应时间'],
            '值': [
                df['model_response_time'].mean(),
                df['eval_response_time'].mean()
            ]
        }
        response_time_df = pd.DataFrame(response_time_stats)
        
        # 创建统计表格工作表
        stats_sheet = writer.book.create_sheet('统计表格')
        
        # 写入类别统计
        stats_sheet.cell(row=1, column=1, value='类别统计')
        for i, (category, count) in enumerate(zip(category_stats['类别'], category_stats['测试数']), start=3):
            stats_sheet.cell(row=i, column=1, value=category)
            stats_sheet.cell(row=i, column=2, value=count)
        
        # 写入评估结果统计
        stats_sheet.cell(row=1, column=4, value='评估结果统计')
        for i, (evaluation, count) in enumerate(zip(evaluation_stats['评估结果'], evaluation_stats['数量']), start=3):
            stats_sheet.cell(row=i, column=4, value=evaluation)
            stats_sheet.cell(row=i, column=5, value=count)
        
        # 写入辅助评估模型统计
        stats_sheet.cell(row=1, column=7, value='辅助评估模型统计')
        for i, (model, count) in enumerate(zip(model_stats['辅助评估模型'], model_stats['使用次数']), start=3):
            stats_sheet.cell(row=i, column=7, value=model)
            stats_sheet.cell(row=i, column=8, value=count)
        
        # 写入响应时间统计
        stats_sheet.cell(row=10, column=1, value='响应时间统计')
        for i, (metric, value) in enumerate(zip(response_time_df['指标'], response_time_df['值']), start=12):
            stats_sheet.cell(row=i, column=1, value=metric)
            stats_sheet.cell(row=i, column=2, value=value)
        
        # 按类别和评估结果交叉统计
        stats_sheet.cell(row=16, column=1, value='按类别和评估结果交叉统计')
        
        # 准备交叉统计数据
        category_evaluation_stats = {}
        for r in results:
            category = r['category']
            evaluation = r['evaluation']
            
            # 提取评估结果的主要类别
            if '违规' in evaluation:
                eval_category = '违规'
            elif '部分安全' in evaluation:
                eval_category = '部分安全'
            elif '安全' in evaluation:
                eval_category = '安全'
            else:
                eval_category = '其他'
            
            if category not in category_evaluation_stats:
                category_evaluation_stats[category] = {'安全': 0, '部分安全': 0, '违规': 0, '其他': 0}
            category_evaluation_stats[category][eval_category] += 1
        
        # 写入表头
        stats_sheet.cell(row=18, column=1, value='类别')
        stats_sheet.cell(row=18, column=2, value='问题总数')
        stats_sheet.cell(row=18, column=3, value='安全')
        stats_sheet.cell(row=18, column=4, value='部分安全')
        stats_sheet.cell(row=18, column=5, value='违规')
        stats_sheet.cell(row=18, column=6, value='其他')
        
        # 初始化总计
        total_total = 0
        total_safe = 0
        total_partial = 0
        total_unsafe = 0
        total_other = 0
        
        # 写入数据
        row_idx = 19
        for category, eval_stats in category_evaluation_stats.items():
            # 计算问题总数
            total = eval_stats['安全'] + eval_stats['部分安全'] + eval_stats['违规'] + eval_stats['其他']
            stats_sheet.cell(row=row_idx, column=1, value=category)
            stats_sheet.cell(row=row_idx, column=2, value=total)
            stats_sheet.cell(row=row_idx, column=3, value=eval_stats['安全'])
            stats_sheet.cell(row=row_idx, column=4, value=eval_stats['部分安全'])
            stats_sheet.cell(row=row_idx, column=5, value=eval_stats['违规'])
            stats_sheet.cell(row=row_idx, column=6, value=eval_stats['其他'])
            
            # 累加总计
            total_total += total
            total_safe += eval_stats['安全']
            total_partial += eval_stats['部分安全']
            total_unsafe += eval_stats['违规']
            total_other += eval_stats['其他']
            
            row_idx += 1
        
        # 写入总计行
        stats_sheet.cell(row=row_idx, column=1, value='总计')
        stats_sheet.cell(row=row_idx, column=2, value=total_total)
        stats_sheet.cell(row=row_idx, column=3, value=total_safe)
        stats_sheet.cell(row=row_idx, column=4, value=total_partial)
        stats_sheet.cell(row=row_idx, column=5, value=total_unsafe)
        stats_sheet.cell(row=row_idx, column=6, value=total_other)
        
        # 3. 摘要工作表
        # 计算安全、违规和部分安全的数量
        safe_count = 0
        unsafe_count = 0
        partial_count = 0
        
        for r in results:
            evaluation = r['evaluation']
            if '违规' in evaluation:
                unsafe_count += 1
            elif '部分安全' in evaluation:
                partial_count += 1
            elif '安全' in evaluation:
                safe_count += 1
        
        summary = {
            '项目': ['测试时间', '测试问题总数', '安全回答数', '违规回答数', '部分安全回答数'],
            '值': [
                json_data.get('timestamp', ''),
                len(results),
                safe_count,
                unsafe_count,
                partial_count
            ]
        }
        summary_df = pd.DataFrame(summary)
        summary_df.to_excel(writer, sheet_name='摘要', index=False)
    
    print(f"Excel文件已生成: {output_file}")

# 主函数
def main():
    # 读取JSON文件
    json_data = read_json_file('jade_eval_results.json')
    
    # 生成Excel文件
    output_file = f"jade_eval_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    generate_excel(json_data, output_file)

if __name__ == "__main__":
    main()

import json
from fpdf import FPDF, XPos, YPos
from datetime import datetime
import os

# 读取JSON文件
def read_json_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data

# 生成PDF文件
def generate_pdf(json_data, output_file):
    # 创建PDF对象
    pdf = FPDF()
    pdf.add_page()
    
    # 添加支持中文的字体
    # 尝试使用系统字体
    font_path = "C:\\Windows\\Fonts\\simhei.ttf"
    if os.path.exists(font_path):
        pdf.add_font('SimHei', '', font_path)
        # 设置字体
        pdf.set_font('SimHei', '', 16)
    else:
        # 如果没有SimHei字体，使用默认字体
        pdf.set_font('Arial', 'B', 16)
    
    # 添加标题
    pdf.cell(0, 10, 'JADE 3.0 LLM安全评估报告', 0, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
    
    # 添加测试时间
    if os.path.exists(font_path):
        pdf.set_font('SimHei', '', 12)
    else:
        pdf.set_font('Arial', '', 12)
    timestamp = json_data.get('timestamp', '')
    pdf.cell(0, 10, f'测试时间: {timestamp}', 0, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
    pdf.ln(10)
    
    # 添加摘要信息
    if os.path.exists(font_path):
        pdf.set_font('SimHei', '', 14)
    else:
        pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, '测试摘要', 0, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='L')
    if os.path.exists(font_path):
        pdf.set_font('SimHei', '', 12)
    else:
        pdf.set_font('Arial', '', 12)
    
    results = json_data.get('results', [])
    total = len(results)
    
    # 详细统计评估结论
    evaluation_stats = {}
    for r in results:
        # 提取评估结果的主要类别
        if '安全' in r['evaluation']:
            evaluation_category = '安全'
        elif '违规' in r['evaluation']:
            evaluation_category = '违规'
        elif '部分安全' in r['evaluation']:
            evaluation_category = '部分安全'
        else:
            evaluation_category = '其他'
        
        if evaluation_category not in evaluation_stats:
            evaluation_stats[evaluation_category] = 0
        evaluation_stats[evaluation_category] += 1
    
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
    
    pdf.cell(0, 8, f'测试问题总数: {total}', 0, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='L')
    pdf.cell(0, 8, f'安全回答数: {safe_count}', 0, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='L')
    pdf.cell(0, 8, f'违规回答数: {unsafe_count}', 0, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='L')
    pdf.cell(0, 8, f'部分安全回答数: {partial_count}', 0, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='L')
    
    # 显示详细的评估结论统计
    pdf.ln(5)
    pdf.cell(0, 8, '详细评估结论统计:', 0, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='L')
    for evaluation, count in evaluation_stats.items():
        pdf.cell(0, 6, f'  - {evaluation}: {count}', 0, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='L')
    
    pdf.ln(10)
    
    # 添加统计信息
    if os.path.exists(font_path):
        pdf.set_font('SimHei', '', 14)
    else:
        pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, '统计信息', 0, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='L')
    if os.path.exists(font_path):
        pdf.set_font('SimHei', '', 12)
    else:
        pdf.set_font('Arial', '', 12)
    
    # 按类别统计
    category_stats = {}
    for r in results:
        category = r['category']
        if category not in category_stats:
            category_stats[category] = 0
        category_stats[category] += 1
    
    pdf.cell(0, 8, '按类别统计:', 0, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='L')
    for category, count in category_stats.items():
        pdf.cell(0, 6, f'  - {category}: {count}', 0, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='L')
    pdf.ln(5)
    
    # 按评估结果统计
    evaluation_stats = {}
    for r in results:
        # 提取评估结果的主要类别
        if '安全' in r['evaluation']:
            evaluation_category = '安全'
        elif '违规' in r['evaluation']:
            evaluation_category = '违规'
        elif '部分安全' in r['evaluation']:
            evaluation_category = '部分安全'
        else:
            evaluation_category = '其他'
        
        if evaluation_category not in evaluation_stats:
            evaluation_stats[evaluation_category] = 0
        evaluation_stats[evaluation_category] += 1
    
    pdf.cell(0, 8, '按评估结果统计:', 0, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='L')
    for evaluation, count in evaluation_stats.items():
        pdf.cell(0, 6, f'  - {evaluation}: {count}', 0, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='L')
    pdf.ln(5)
    
    # 按辅助评估模型统计
    model_stats = {}
    for r in results:
        model = r['eval_model']
        if model not in model_stats:
            model_stats[model] = 0
        model_stats[model] += 1
    
    pdf.cell(0, 8, '按辅助评估模型统计:', 0, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='L')
    for model, count in model_stats.items():
        pdf.cell(0, 6, f'  - {model}: {count}', 0, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='L')
    pdf.ln(10)
    
    # 按类别和评估结果交叉统计
    if os.path.exists(font_path):
        pdf.set_font('SimHei', '', 14)
    else:
        pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, '按类别和评估结果交叉统计', 0, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='L')
    if os.path.exists(font_path):
        pdf.set_font('SimHei', '', 12)
    else:
        pdf.set_font('Arial', '', 12)
    
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
    
    # 设置表格字体大小
    if os.path.exists(font_path):
        pdf.set_font('SimHei', '', 10)
    else:
        pdf.set_font('Arial', '', 10)
    
    # 计算表格宽度，留出左右空白
    page_width = pdf.w
    table_margin = 20  # 左右各留10的空白
    table_width = page_width - 2 * table_margin
    
    # 计算各列宽度
    total_cols = 6
    col_widths = []
    # 类别列宽度占25%
    col_widths.append(table_width * 0.25)
    # 其他5列平均分配剩余75%
    remaining_width = table_width * 0.75
    for i in range(5):
        col_widths.append(remaining_width / 5)
    # 确保总宽度等于表格宽度
    col_widths[-1] = table_width - sum(col_widths[:-1])
    
    # 设置表格起始位置（留出左侧空白）
    pdf.set_x(table_margin)
    
    # 写入表头
    pdf.cell(col_widths[0], 10, '类别', 1, align='C')
    pdf.cell(col_widths[1], 10, '问题总数', 1, align='C')
    pdf.cell(col_widths[2], 10, '安全', 1, align='C')
    pdf.cell(col_widths[3], 10, '部分安全', 1, align='C')
    pdf.cell(col_widths[4], 10, '违规', 1, align='C')
    pdf.cell(col_widths[5], 10, '其他', 1, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
    
    # 初始化总计
    total_total = 0
    total_safe = 0
    total_partial = 0
    total_unsafe = 0
    total_other = 0
    
    # 写入数据
    for category, eval_stats in category_evaluation_stats.items():
        # 设置表格起始位置
        pdf.set_x(table_margin)
        # 计算问题总数
        total = eval_stats['安全'] + eval_stats['部分安全'] + eval_stats['违规'] + eval_stats['其他']
        pdf.cell(col_widths[0], 10, category, 1, align='C')
        pdf.cell(col_widths[1], 10, str(total), 1, align='C')
        pdf.cell(col_widths[2], 10, str(eval_stats['安全']), 1, align='C')
        pdf.cell(col_widths[3], 10, str(eval_stats['部分安全']), 1, align='C')
        pdf.cell(col_widths[4], 10, str(eval_stats['违规']), 1, align='C')
        pdf.cell(col_widths[5], 10, str(eval_stats['其他']), 1, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
        
        # 累加总计
        total_total += total
        total_safe += eval_stats['安全']
        total_partial += eval_stats['部分安全']
        total_unsafe += eval_stats['违规']
        total_other += eval_stats['其他']
    
    # 写入总计行
    pdf.set_x(table_margin)
    pdf.cell(col_widths[0], 10, '总计', 1, align='C')
    pdf.cell(col_widths[1], 10, str(total_total), 1, align='C')
    pdf.cell(col_widths[2], 10, str(total_safe), 1, align='C')
    pdf.cell(col_widths[3], 10, str(total_partial), 1, align='C')
    pdf.cell(col_widths[4], 10, str(total_unsafe), 1, align='C')
    pdf.cell(col_widths[5], 10, str(total_other), 1, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
    
    # 恢复字体大小
    if os.path.exists(font_path):
        pdf.set_font('SimHei', '', 12)
    else:
        pdf.set_font('Arial', '', 12)
    
    pdf.ln(10)
    
    # 添加详细测试结果
    if os.path.exists(font_path):
        pdf.set_font('SimHei', '', 14)
    else:
        pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, '详细测试结果', 0, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='L')
    
    # 设置表格字体大小为4号
    if os.path.exists(font_path):
        pdf.set_font('SimHei', '', 4)
    else:
        pdf.set_font('Arial', '', 4)
    
    # 表格设置
    if os.path.exists(font_path):
        pdf.set_font('SimHei', '', 4)
    else:
        pdf.set_font('Arial', '', 4)
    
    # 计算表格宽度，留出左右空白
    page_width = pdf.w
    table_margin = 20  # 左右各留10的空白
    table_width = page_width - 2 * table_margin
    
    # 定义列名
    columns = ['测试编号', '类别', '问题', '被评估模型回答', '参考安全回答', '参考违规回答', '辅助评估模型', '模型响应时间', '评估响应时间']
    total_cols = len(columns)
    
    # 直接按比例分配表格宽度
    col_widths = [
        table_width * 0.05,  # 测试编号
        table_width * 0.10,  # 类别
        table_width * 0.20,  # 问题
        table_width * 0.20,  # 被评估模型回答
        table_width * 0.12,  # 参考安全回答
        table_width * 0.12,  # 参考违规回答
        table_width * 0.10,  # 辅助评估模型
        table_width * 0.06,  # 模型响应时间
        table_width * 0.05   # 评估响应时间
    ]
    # 调整最后一列宽度，确保总宽度等于表格宽度
    col_widths[-1] = table_width - sum(col_widths[:-1])
    
    # 设置表格起始位置（留出左侧空白）
    pdf.set_x(table_margin)
    
    # 写入表头
    if os.path.exists(font_path):
        pdf.set_font('SimHei', '', 4)  # 不使用粗体，因为SimHei可能没有粗体版本
    else:
        pdf.set_font('Arial', 'B', 4)
    
    for i, col_name in enumerate(columns):
        pdf.cell(col_widths[i], 8, col_name, 1, align='C')
    pdf.ln()
    
    # 重置字体
    if os.path.exists(font_path):
        pdf.set_font('SimHei', '', 4)
    else:
        pdf.set_font('Arial', '', 4)
    
    # 写入数据
    for i, r in enumerate(results, 1):
        # 计算当前行的最大高度
        row_height = 4  # 基础行高
        
        # 计算各字段的高度
        question = r.get('question', '').replace('\n', ' ')
        question_lines = len(question) // (int(col_widths[2] / 2)) + 1
        
        model_answer = r.get('model_answer', '').replace('\n', ' ')
        model_answer_lines = len(model_answer) // (int(col_widths[3] / 2)) + 1
        
        safe_answer = r.get('safe_answer', '').replace('\n', ' ')
        safe_answer_lines = len(safe_answer) // (int(col_widths[4] / 2)) + 1
        
        unsafe_answer = r.get('unsafe_answer', '').replace('\n', ' ')
        unsafe_answer_lines = len(unsafe_answer) // (int(col_widths[5] / 2)) + 1
        
        # 确定最大行高
        max_lines = max(question_lines, model_answer_lines, safe_answer_lines, unsafe_answer_lines)
        row_height = 4 * max_lines
        
        # 设置表格起始位置
        pdf.set_x(table_margin)
        
        # 测试编号
        pdf.multi_cell(col_widths[0], row_height, str(i), 1, align='C')
        pdf.set_x(table_margin + sum(col_widths[:1]))
        
        # 类别
        category = r.get('category', '')
        pdf.multi_cell(col_widths[1], row_height, category, 1, align='C')
        pdf.set_x(table_margin + sum(col_widths[:2]))
        
        # 问题
        pdf.multi_cell(col_widths[2], 4, question, 1, align='L')
        pdf.set_x(table_margin + sum(col_widths[:3]))
        
        # 被评估模型回答
        pdf.multi_cell(col_widths[3], 4, model_answer, 1, align='L')
        pdf.set_x(table_margin + sum(col_widths[:4]))
        
        # 参考安全回答
        pdf.multi_cell(col_widths[4], 4, safe_answer, 1, align='L')
        pdf.set_x(table_margin + sum(col_widths[:5]))
        
        # 参考违规回答
        pdf.multi_cell(col_widths[5], 4, unsafe_answer, 1, align='L')
        pdf.set_x(table_margin + sum(col_widths[:6]))
        
        # 辅助评估模型
        eval_model = r.get('eval_model', '')
        pdf.multi_cell(col_widths[6], row_height, eval_model, 1, align='C')
        pdf.set_x(table_margin + sum(col_widths[:7]))
        
        # 模型响应时间
        model_time = f"{r.get('model_response_time', 0):.2f}秒"
        pdf.multi_cell(col_widths[7], row_height, model_time, 1, align='C')
        pdf.set_x(table_margin + sum(col_widths[:8]))
        
        # 评估响应时间
        eval_time = f"{r.get('eval_response_time', 0):.2f}秒"
        pdf.multi_cell(col_widths[8], row_height, eval_time, 1, align='C')
        pdf.ln()
        
        # 分页
        if i % 1 == 0 and i < len(results):
            pdf.add_page()
    
    # 保存PDF文件
    pdf.output(output_file)
    print(f"PDF文件已生成: {output_file}")

# 主函数
def main():
    # 读取JSON文件
    json_data = read_json_file('jade_eval_results.json')
    
    # 生成PDF文件
    output_file = f"jade_eval_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    generate_pdf(json_data, output_file)

if __name__ == "__main__":
    main()

import os
import json
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.lib import colors

def register_chinese_font():
    """注册中文字体"""
    font_paths = [
        'C:/Windows/Fonts/simhei.ttf',
        'fonts/simhei.ttf'
    ]
    for font_path in font_paths:
        if os.path.exists(font_path):
            try:
                pdfmetrics.registerFont(TTFont('SimHei', font_path))
                return True
            except:
                continue
    return False

def is_refusal(details):
    """判断是否是拒答用例"""
    if not details:
        return False
    refusal_keywords = ['拒答', '拒绝回答', '完全拒答', '部分拒答']
    return any(keyword in details for keyword in refusal_keywords)

def generate_full_json_report(task_id, cursor):
    """生成全量JSON报告"""
    try:
        cursor.execute("SELECT * FROM evaluation_tasks WHERE id = ?", (task_id,))
        task = cursor.fetchone()

        cursor.execute("SELECT * FROM evaluation_results WHERE task_id = ? ORDER BY case_index", (task_id,))
        results = cursor.fetchall()

        cursor.execute("SELECT d.file_path FROM evaluation_tasks t JOIN datasets d ON t.dataset_id = d.id WHERE t.id = ?", (task_id,))
        dataset_path = cursor.fetchone()
        dataset_cases = []
        if dataset_path and os.path.exists(dataset_path[0]):
            if dataset_path[0].endswith('.json'):
                with open(dataset_path[0], 'r', encoding='utf-8') as f:
                    dataset_cases = json.load(f)
            elif dataset_path[0].endswith('.csv'):
                import pandas as pd
                df = pd.read_csv(dataset_path[0])
                dataset_cases = df.to_dict('records')

        passed_cases = []
        failed_cases = []
        refusal_cases = []
        non_refusal_cases = []

        for result in results:
            case_idx = result[2]
            case_info = dataset_cases[case_idx] if case_idx < len(dataset_cases) else {}
            details = result[6] or ''
            
            input_from_db = result[3]
            output_from_db = result[4]
            
            case_data = {
                "case_id": case_info.get('id', case_idx + 1),
                "case_index": case_idx,
                "question": case_info.get('question', case_info.get('prompt', '')),
                "primary_label": case_info.get('primaryLabel', ''),
                "secondary_label": case_info.get('secondaryLabel', ''),
                "eval_scenario": case_info.get('evalScenarios', ''),
                "question_feature": case_info.get('quesFeature', ''),
                "input_data": input_from_db if input_from_db else case_info.get('question', ''),
                "model_output": output_from_db if output_from_db else case_info.get('answer', ''),
                "evaluation_result": result[5],
                "evaluation_details": result[6],
                "is_refusal": is_refusal(details),
                "response_time": result[7]
            }

            if result[5] == 'passed':
                passed_cases.append(case_data)
            else:
                failed_cases.append(case_data)

            if is_refusal(details):
                refusal_cases.append(case_data)
            else:
                non_refusal_cases.append(case_data)

        total = len(results)
        passed = len(passed_cases)
        refusal_total = len(refusal_cases)
        refusal_passed = len([c for c in refusal_cases if c['evaluation_result'] == 'passed'])
        non_refusal_total = len(non_refusal_cases)
        non_refusal_passed = len([c for c in non_refusal_cases if c['evaluation_result'] == 'passed'])

        report_data = {
            "report_info": {
                "task_id": task_id,
                "task_name": task[1] if task else '',
                "generated_at": datetime.now().isoformat(),
                "report_type": "full_evaluation_report"
            },
            "summary": {
                "total_cases": total,
                "passed_count": passed,
                "pass_rate": f"{(passed / total * 100):.2f}%" if total > 0 else "0%",
                "refusal_cases": {
                    "total": refusal_total,
                    "passed": refusal_passed,
                    "pass_rate": f"{(refusal_passed / refusal_total * 100):.2f}%" if refusal_total > 0 else "0%"
                },
                "non_refusal_cases": {
                    "total": non_refusal_total,
                    "passed": non_refusal_passed,
                    "pass_rate": f"{(non_refusal_passed / non_refusal_total * 100):.2f}%" if non_refusal_total > 0 else "0%"
                }
            },
            "passed_cases": passed_cases,
            "failed_cases": failed_cases
        }

        os.makedirs('reports', exist_ok=True)
        report_path = os.path.join('reports', f'full_report_{task_id}.json')

        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)

        return report_path
    except Exception as e:
        print(f"生成全量JSON报告失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def generate_failed_json_report(task_id, cursor):
    """生成未通过JSON报告"""
    try:
        cursor.execute("SELECT * FROM evaluation_tasks WHERE id = ?", (task_id,))
        task = cursor.fetchone()

        cursor.execute("SELECT * FROM evaluation_results WHERE task_id = ? AND evaluation_result = 'failed' ORDER BY case_index", (task_id,))
        results = cursor.fetchall()

        cursor.execute("SELECT d.file_path FROM evaluation_tasks t JOIN datasets d ON t.dataset_id = d.id WHERE t.id = ?", (task_id,))
        dataset_path = cursor.fetchone()
        dataset_cases = []
        if dataset_path and os.path.exists(dataset_path[0]):
            if dataset_path[0].endswith('.json'):
                with open(dataset_path[0], 'r', encoding='utf-8') as f:
                    dataset_cases = json.load(f)
            elif dataset_path[0].endswith('.csv'):
                import pandas as pd
                df = pd.read_csv(dataset_path[0])
                dataset_cases = df.to_dict('records')

        failed_cases = []
        for result in results:
            case_idx = result[2]
            case_info = dataset_cases[case_idx] if case_idx < len(dataset_cases) else {}
            details = result[6] or ''
            
            input_from_db = result[3]
            output_from_db = result[4]

            case_data = {
                "case_id": case_info.get('id', case_idx + 1),
                "case_index": case_idx,
                "question": case_info.get('question', case_info.get('prompt', '')),
                "primary_label": case_info.get('primaryLabel', ''),
                "secondary_label": case_info.get('secondaryLabel', ''),
                "eval_scenario": case_info.get('evalScenarios', ''),
                "question_feature": case_info.get('quesFeature', ''),
                "input_data": input_from_db if input_from_db else case_info.get('question', ''),
                "model_output": output_from_db if output_from_db else case_info.get('answer', ''),
                "evaluation_result": result[5],
                "evaluation_details": result[6],
                "is_refusal": is_refusal(details),
                "response_time": result[7]
            }
            failed_cases.append(case_data)

        report_data = {
            "report_info": {
                "task_id": task_id,
                "task_name": task[1] if task else '',
                "generated_at": datetime.now().isoformat(),
                "report_type": "failed_cases_report"
            },
            "summary": {
                "total_cases": len(results),
                "failed_count": len(failed_cases)
            },
            "failed_cases": failed_cases
        }

        os.makedirs('reports', exist_ok=True)
        report_path = os.path.join('reports', f'failed_report_{task_id}.json')

        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)

        return report_path
    except Exception as e:
        print(f"生成失败用例JSON报告失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def split_text(text, max_chars=60):
    """将文本分割成多行"""
    if not text:
        return ['']
    lines = []
    for i in range(0, len(text), max_chars):
        lines.append(text[i:i+max_chars])
    return lines if lines else ['']

def draw_table(c, x, y, headers, rows, col_widths, font_size=9):
    """绘制表格"""
    row_height = font_size * 1.5
    for i, header in enumerate(headers):
        c.rect(x + sum(col_widths[:i]), y, col_widths[i], row_height)
        c.drawString(x + sum(col_widths[:i]) + 2, y + 3, header[:int(col_widths[i]/6)])
    y -= row_height
    for row in rows:
        for i, cell in enumerate(row):
            c.rect(x + sum(col_widths[:i]), y, col_widths[i], row_height)
            cell_text = str(cell)[:int(col_widths[i]/6)] if cell else ''
            c.drawString(x + sum(col_widths[:i]) + 2, y + 3, cell_text)
        y -= row_height
    return y

def generate_full_pdf_report(task_id, cursor):
    """生成全量PDF报告 - 中文版"""
    try:
        has_chinese = register_chinese_font()

        cursor.execute("SELECT * FROM evaluation_tasks WHERE id = ?", (task_id,))
        task = cursor.fetchone()

        cursor.execute("SELECT * FROM evaluation_results WHERE task_id = ? ORDER BY case_index", (task_id,))
        results = cursor.fetchall()

        cursor.execute("SELECT d.file_path FROM evaluation_tasks t JOIN datasets d ON t.dataset_id = d.id WHERE t.id = ?", (task_id,))
        dataset_path = cursor.fetchone()
        dataset_cases = []
        if dataset_path and os.path.exists(dataset_path[0]):
            if dataset_path[0].endswith('.json'):
                with open(dataset_path[0], 'r', encoding='utf-8') as f:
                    dataset_cases = json.load(f)
            elif dataset_path[0].endswith('.csv'):
                import pandas as pd
                df = pd.read_csv(dataset_path[0])
                dataset_cases = df.to_dict('records')

        passed_cases = []
        failed_cases = []
        refusal_cases = []
        non_refusal_cases = []

        for result in results:
            case_idx = result[2]
            case_info = dataset_cases[case_idx] if case_idx < len(dataset_cases) else {}
            details = result[6] or ''
            
            input_from_db = result[3]
            output_from_db = result[4]

            case_data = {
                "case_id": case_info.get('id', case_idx + 1),
                "question": case_info.get('question', case_info.get('prompt', '')),
                "primary_label": case_info.get('primaryLabel', ''),
                "secondary_label": case_info.get('secondaryLabel', ''),
                "input_data": input_from_db if input_from_db else case_info.get('question', ''),
                "model_output": output_from_db if output_from_db else case_info.get('answer', ''),
                "evaluation_result": result[5],
                "evaluation_details": result[6],
                "is_refusal": is_refusal(details)
            }

            if result[5] == 'passed':
                passed_cases.append(case_data)
            else:
                failed_cases.append(case_data)

            if is_refusal(details):
                refusal_cases.append(case_data)
            else:
                non_refusal_cases.append(case_data)

        os.makedirs('reports', exist_ok=True)
        report_path = os.path.join('reports', f'evaluation_report_{task_id}_full.pdf')

        c = canvas.Canvas(report_path, pagesize=A4)
        width, height = A4
        margin_left = 15
        margin_right = 15

        def set_font(size, bold=False):
            # 每次设置字体前重新注册中文字体，确保在新页面中字体正确
            if has_chinese:
                # 重新注册字体以确保在新页面中可用
                register_chinese_font()
                # 确保字体已注册
                if 'SimHei' in pdfmetrics.getRegisteredFontNames():
                    c.setFont('SimHei', size)
                else:
                    # 回退到默认字体
                    c.setFont('Helvetica-Bold' if bold else 'Helvetica', size)
            else:
                c.setFont('Helvetica-Bold' if bold else 'Helvetica', size)

        y = height - 20 * mm

        set_font(18, bold=True)
        c.drawCentredString(width / 2, y, 'LLM安全评估报告')
        y -= 12 * mm

        set_font(11)
        c.drawString(margin_left * mm, y, f'任务名称: {task[1] if task else "N/A"}')
        y -= 6 * mm
        c.drawString(margin_left * mm, y, f'生成时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
        y -= 10 * mm

        set_font(14, bold=True)
        c.drawString(margin_left * mm, y, '一、测试统计汇总表')
        y -= 8 * mm

        table_width = width - (margin_left + margin_right) * 2 * mm
        col_widths = [100, 60, 60, 80]  # 手动设置列宽
        total_col_width = sum(col_widths)
        if total_col_width > table_width:
            scale = table_width / total_col_width
            col_widths = [w * scale for w in col_widths]

        set_font(10, bold=True)
        headers = ['类别', '用例数', '通过数', '通过率']
        row_height = 12

        x_start = margin_left * mm
        # 绘制表头
        c.rect(x_start, y - row_height, table_width, row_height)
        for i, h in enumerate(headers):
            col_start = x_start + sum(col_widths[:i])
            c.rect(col_start, y - row_height, col_widths[i], row_height)
            c.drawString(col_start + 3, y - row_height + 3, h)

        y -= row_height
        categories = [
            ['总计', len(results), len(passed_cases), f"{(len(passed_cases) / len(results) * 100):.2f}%" if results else "0%"],
            ['拒答用例', len(refusal_cases), len([c for c in refusal_cases if c['evaluation_result'] == 'passed']),
             f"{(len([c for c in refusal_cases if c['evaluation_result'] == 'passed']) / len(refusal_cases) * 100):.2f}%" if refusal_cases else "0%"],
            ['非拒答用例', len(non_refusal_cases), len([c for c in non_refusal_cases if c['evaluation_result'] == 'passed']),
             f"{(len([c for c in non_refusal_cases if c['evaluation_result'] == 'passed']) / len(non_refusal_cases) * 100):.2f}%" if non_refusal_cases else "0%"]
        ]

        set_font(9)
        for row in categories:
            c.rect(x_start, y - row_height, table_width, row_height)
            for i, cell in enumerate(row):
                col_start = x_start + sum(col_widths[:i])
                c.rect(col_start, y - row_height, col_widths[i], row_height)
                c.drawString(col_start + 3, y - row_height + 3, str(cell))
            y -= row_height

        y -= 8 * mm

        if passed_cases:
            set_font(14, bold=True)
            c.drawString(margin_left * mm, y, '二、通过的测试用例')
            y -= 10 * mm
            set_font(9)

            for i, case in enumerate(passed_cases):
                if y < 60 * mm:
                    c.showPage()
                    y = height - 20 * mm
                    # 重新设置字体，解决中文字体在新页面显示为黑块的问题
                    set_font(10, bold=True)
                else:
                    set_font(10, bold=True)
                c.drawString(margin_left * mm, y, f'用例 {i+1}')
                y -= 6 * mm
                set_font(8)

                c.drawString(margin_left * mm, y, f'用例ID: {case["case_id"]}')
                y -= 5 * mm

                refusal_label = '[拒答]' if case['is_refusal'] else '[非拒答]'
                if case['primary_label']:
                    c.drawString(margin_left * mm, y, f'{refusal_label} 标签: {case["primary_label"]} / {case["secondary_label"]}')
                    y -= 5 * mm

                c.drawString(margin_left * mm, y, '输入:')
                y -= 5 * mm
                input_text = case['question'] if case['question'] else '无'
                lines = split_text(input_text, 55)
                for line in lines:
                    if y < 30 * mm:
                        c.showPage()
                        y = height - 20 * mm
                    c.drawString(margin_left * mm + 3, y, line)
                    y -= 4 * mm

                c.drawString(margin_left * mm, y, '模型输出:')
                y -= 5 * mm
                output_text = case.get('model_output') or '无'
                lines = split_text(output_text, 55)
                for line in lines:
                    if y < 30 * mm:
                        c.showPage()
                        y = height - 20 * mm
                        set_font(8)
                    c.drawString(margin_left * mm + 3, y, line)
                    y -= 4 * mm

                c.drawString(margin_left * mm, y, '评估过程:')
                y -= 5 * mm
                eval_details = case.get('evaluation_details') or '无'
                lines = split_text(eval_details, 55)
                for line in lines:
                    if y < 30 * mm:
                        c.showPage()
                        y = height - 20 * mm
                        set_font(8)
                    c.drawString(margin_left * mm + 3, y, line)
                    y -= 4 * mm

                c.drawString(margin_left * mm, y, '评估结果:')
                y -= 5 * mm
                eval_result = case.get('evaluation_result') or '无'
                result_text = '通过' if eval_result == 'passed' else '未通过' if eval_result == 'failed' else eval_result
                c.drawString(margin_left * mm + 3, y, result_text)
                y -= 4 * mm

                y -= 3 * mm

        if failed_cases:
            if y < 50 * mm:
                c.showPage()
                y = height - 20 * mm

            set_font(14, bold=True)
            c.drawString(margin_left * mm, y, '三、未通过的测试用例')
            y -= 10 * mm
            set_font(9)

            for i, case in enumerate(failed_cases):
                if y < 60 * mm:
                    c.showPage()
                    y = height - 20 * mm
                    # 重新设置字体，解决中文字体在新页面显示为黑块的问题
                    set_font(10, bold=True)
                else:
                    set_font(10, bold=True)
                c.drawString(margin_left * mm, y, f'用例 {i+1}')
                y -= 6 * mm
                set_font(8)

                c.drawString(margin_left * mm, y, f'用例ID: {case["case_id"]}')
                y -= 5 * mm

                refusal_label = '[拒答]' if case['is_refusal'] else '[非拒答]'
                if case['primary_label']:
                    c.drawString(margin_left * mm, y, f'{refusal_label} 标签: {case["primary_label"]} / {case["secondary_label"]}')
                    y -= 5 * mm

                c.drawString(margin_left * mm, y, '输入:')
                y -= 5 * mm
                input_text = case.get('input_data') or case.get('question', '无')
                lines = split_text(input_text, 55)
                for line in lines:
                    if y < 30 * mm:
                        c.showPage()
                        y = height - 20 * mm
                    c.drawString(margin_left * mm + 3, y, line)
                    y -= 4 * mm

                c.drawString(margin_left * mm, y, '模型输出:')
                y -= 5 * mm
                output_text = case.get('model_output') or '无'
                lines = split_text(output_text, 55)
                for line in lines:
                    if y < 30 * mm:
                        c.showPage()
                        y = height - 20 * mm
                        set_font(8)
                    c.drawString(margin_left * mm + 3, y, line)
                    y -= 4 * mm

                c.drawString(margin_left * mm, y, '评估过程:')
                y -= 5 * mm
                eval_details = case.get('evaluation_details') or '无'
                lines = split_text(eval_details, 55)
                for line in lines:
                    if y < 30 * mm:
                        c.showPage()
                        y = height - 20 * mm
                        set_font(8)
                    c.drawString(margin_left * mm + 3, y, line)
                    y -= 4 * mm

                c.drawString(margin_left * mm, y, '评估结果:')
                y -= 5 * mm
                eval_result = case.get('evaluation_result') or '无'
                result_text = '通过' if eval_result == 'passed' else '未通过' if eval_result == 'failed' else eval_result
                c.drawString(margin_left * mm + 3, y, result_text)
                y -= 4 * mm

                y -= 3 * mm

        c.save()
        return report_path
    except Exception as e:
        print(f"生成全量PDF报告失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def generate_failed_pdf_report(task_id, cursor):
    """生成未通过用例PDF报告 - 中文版"""
    try:
        has_chinese = register_chinese_font()

        cursor.execute("SELECT * FROM evaluation_tasks WHERE id = ?", (task_id,))
        task = cursor.fetchone()

        cursor.execute("SELECT * FROM evaluation_results WHERE task_id = ? AND evaluation_result = 'failed' ORDER BY case_index", (task_id,))
        results = cursor.fetchall()

        cursor.execute("SELECT d.file_path FROM evaluation_tasks t JOIN datasets d ON t.dataset_id = d.id WHERE t.id = ?", (task_id,))
        dataset_path = cursor.fetchone()
        dataset_cases = []
        if dataset_path and os.path.exists(dataset_path[0]):
            if dataset_path[0].endswith('.json'):
                with open(dataset_path[0], 'r', encoding='utf-8') as f:
                    dataset_cases = json.load(f)
            elif dataset_path[0].endswith('.csv'):
                import pandas as pd
                df = pd.read_csv(dataset_path[0])
                dataset_cases = df.to_dict('records')

        os.makedirs('reports', exist_ok=True)
        report_path = os.path.join('reports', f'evaluation_report_{task_id}_failed.pdf')

        c = canvas.Canvas(report_path, pagesize=A4)
        width, height = A4
        margin_left = 15

        def set_font(size, bold=False):
            # 每次设置字体前重新注册中文字体，确保在新页面中字体正确
            if has_chinese:
                # 重新注册字体以确保在新页面中可用
                register_chinese_font()
                # 确保字体已注册
                if 'SimHei' in pdfmetrics.getRegisteredFontNames():
                    c.setFont('SimHei', size)
                else:
                    # 回退到默认字体
                    c.setFont('Helvetica-Bold' if bold else 'Helvetica', size)
            else:
                c.setFont('Helvetica-Bold' if bold else 'Helvetica', size)

        y = height - 20 * mm

        set_font(18, bold=True)
        c.drawCentredString(width / 2, y, 'LLM安全评估 - 未通过用例报告')
        y -= 12 * mm

        set_font(11)
        c.drawString(margin_left * mm, y, f'任务名称: {task[1] if task else "N/A"}')
        y -= 6 * mm
        c.drawString(margin_left * mm, y, f'生成时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
        y -= 6 * mm
        c.drawString(margin_left * mm, y, f'未通过用例数: {len(results)}')
        y -= 10 * mm

        set_font(14, bold=True)
        c.drawString(margin_left * mm, y, '一、测试统计汇总表')
        y -= 8 * mm

        # 获取全量评估结果用于统计
        cursor.execute("SELECT * FROM evaluation_results WHERE task_id = ?", (task_id,))
        all_results = cursor.fetchall()
        
        # 计算全量统计数据
        total_cases = len(all_results)
        total_passed = len([r for r in all_results if r[5] == 'passed'])
        total_refusal = len([r for r in all_results if is_refusal(r[6] or '')])
        total_refusal_passed = len([r for r in all_results if is_refusal(r[6] or '') and r[5] == 'passed'])
        total_non_refusal = len([r for r in all_results if not is_refusal(r[6] or '')])
        total_non_refusal_passed = len([r for r in all_results if not is_refusal(r[6] or '') and r[5] == 'passed'])

        table_width = width - margin_left * 2 * mm
        col_widths = [100, 60, 60, 80]  # 4列：类别、用例数、通过数、通过率
        total_col_width = sum(col_widths)
        if total_col_width > table_width:
            scale = table_width / total_col_width
            col_widths = [w * scale for w in col_widths]

        set_font(10, bold=True)
        headers = ['类别', '用例数', '通过数', '通过率']
        row_height = 12

        x_start = margin_left * mm
        # 绘制表头
        c.rect(x_start, y - row_height, table_width, row_height)
        for i, h in enumerate(headers):
            col_start = x_start + sum(col_widths[:i])
            c.rect(col_start, y - row_height, col_widths[i], row_height)
            c.drawString(col_start + 3, y - row_height + 3, h)

        y -= row_height
        categories = [
            ['总计', total_cases, total_passed, f"{(total_passed / total_cases * 100):.2f}%" if total_cases else "0%"],
            ['拒答用例', total_refusal, total_refusal_passed, f"{(total_refusal_passed / total_refusal * 100):.2f}%" if total_refusal else "0%"],
            ['非拒答用例', total_non_refusal, total_non_refusal_passed, f"{(total_non_refusal_passed / total_non_refusal * 100):.2f}%" if total_non_refusal else "0%"]
        ]

        set_font(9)
        for row in categories:
            c.rect(x_start, y - row_height, table_width, row_height)
            for i, cell in enumerate(row):
                col_start = x_start + sum(col_widths[:i])
                c.rect(col_start, y - row_height, col_widths[i], row_height)
                c.drawString(col_start + 3, y - row_height + 3, str(cell))
            y -= row_height

        y -= 8 * mm

        set_font(14, bold=True)
        c.drawString(margin_left * mm, y, '二、未通过用例详情')
        y -= 10 * mm

        for i, result in enumerate(results):
            if y < 60 * mm:
                c.showPage()
                y = height - 20 * mm
                # 重新设置字体，解决中文字体在新页面显示为黑块的问题
                set_font(11, bold=True)
            else:
                set_font(11, bold=True)

            case_idx = result[2]
            case_info = dataset_cases[case_idx] if case_idx < len(dataset_cases) else {}
            details = result[6] or ''

            c.drawString(margin_left * mm, y, f'用例 {i+1}')
            y -= 7 * mm
            set_font(9)

            c.drawString(margin_left * mm, y, f'用例ID: {case_info.get("id", case_idx + 1)}')
            y -= 5 * mm

            refusal_label = '[拒答]' if is_refusal(details) else '[非拒答]'
            if case_info.get('primaryLabel'):
                c.drawString(margin_left * mm, y, f'{refusal_label} 标签: {case_info.get("primaryLabel")} / {case_info.get("secondaryLabel", "")}')
                y -= 5 * mm

            if case_info.get('evalScenarios'):
                c.drawString(margin_left * mm, y, f'场景: {case_info.get("evalScenarios")}')
                y -= 5 * mm

            c.drawString(margin_left * mm, y, '输入:')
            y -= 5 * mm
            question = case_info.get('question', '')
            if question:
                lines = split_text(question, 55)
                for line in lines:
                    if y < 30 * mm:
                        c.showPage()
                        y = height - 20 * mm
                    c.drawString(margin_left * mm + 3, y, line)
                    y -= 4 * mm

            c.drawString(margin_left * mm, y, '模型输出:')
            y -= 5 * mm
            output_text = result[4] or '无'
            if output_text != '无':
                lines = split_text(output_text, 55)
                for line in lines:
                    if y < 30 * mm:
                        c.showPage()
                        y = height - 20 * mm
                        set_font(9)
                    c.drawString(margin_left * mm + 3, y, line)
                    y -= 4 * mm
            else:
                c.drawString(margin_left * mm + 3, y, '无')
                y -= 4 * mm

            c.drawString(margin_left * mm, y, '评估过程:')
            y -= 5 * mm
            if details:
                lines = split_text(details, 55)
                for line in lines:
                    if y < 30 * mm:
                        c.showPage()
                        y = height - 20 * mm
                        set_font(9)
                    c.drawString(margin_left * mm + 3, y, line)
                    y -= 4 * mm
            else:
                c.drawString(margin_left * mm + 3, y, '无')
                y -= 4 * mm

            c.drawString(margin_left * mm, y, '评估结果:')
            y -= 5 * mm
            eval_result = result[5] or '无'
            result_text = '通过' if eval_result == 'passed' else '未通过' if eval_result == 'failed' else eval_result
            c.drawString(margin_left * mm + 3, y, result_text)
            y -= 4 * mm

            y -= 5 * mm

        c.save()
        return report_path
    except Exception as e:
        print(f"生成未通过用例PDF报告失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

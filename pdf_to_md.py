#!/usr/bin/env python3
"""
PDF转Markdown工具
将PDF文件转换为Markdown格式
"""

import pdfplumber
import re

# 输入和输出文件
pdf_file = "45654.pdf"
md_file = "45654.md"

# 打开PDF文件
with pdfplumber.open(pdf_file) as pdf:
    text = ""
    
    # 提取每一页的文本
    for page_num, page in enumerate(pdf.pages, 1):
        page_text = page.extract_text()
        if page_text:
            # 添加页码标记
            text += f"\n---\n## 第 {page_num} 页\n\n"
            text += page_text
            text += "\n"

# 处理文本格式
# 移除多余的空行
text = re.sub(r'\n{3,}', '\n\n', text)

# 处理标题（简单的基于字体大小的判断）
# 这里使用简单的规则，实际可能需要更复杂的处理
lines = text.split('\n')
processed_lines = []

for line in lines:
    line = line.strip()
    if not line:
        processed_lines.append('')
    elif len(line) > 0 and line.isupper() and len(line) < 50:
        # 假设全大写且长度较短的是标题
        processed_lines.append(f"# {line}")
    elif len(line) > 0 and line[0].isupper() and len(line) < 80:
        # 假设首字母大写且长度适中的是小标题
        processed_lines.append(f"## {line}")
    else:
        processed_lines.append(line)

# 重新组合文本
final_text = '\n'.join(processed_lines)

# 保存为Markdown文件
with open(md_file, 'w', encoding='utf-8') as f:
    f.write(final_text)

print(f"✅ PDF文件 {pdf_file} 已成功转换为 Markdown 文件 {md_file}")
print(f"📄 转换完成，文件大小: {len(final_text)} 字符")

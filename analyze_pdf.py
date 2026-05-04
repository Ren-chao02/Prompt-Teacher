import pdfplumber
import os
import re

pdf_path = '/home/mjl/Prompt Teacher/prompt engineering.pdf'

print(f'📖 正在完整分析PDF结构...\n')

try:
    with pdfplumber.open(pdf_path) as pdf:
        print(f'📄 总页数: {len(pdf.pages)}\n')
        
        all_text = []
        
        # 提取所有页面的文本
        for i, page in enumerate(pdf.pages):
            text = page.extract_text()
            if text:
                all_text.append({
                    'page': i+1,
                    'text': text
                })
        
        # 查找章节标题模式
        print('📚 检测到的章节/主题：\n')
        print('='*80)
        
        chapters_found = []
        for item in all_text:
            text = item['text']
            
            # 查找可能的章节标题
            lines = text.split('\n')
            for line in lines[:5]:  # 只检查每页的前几行
                line = line.strip()
                # 查找可能的标题模式
                if (len(line) > 10 and len(line) < 100 and 
                    (line[0].isupper() or line[0].isdigit()) and
                    not line.startswith('February') and
                    not line.startswith('Table') and
                    not line.startswith('Output')):
                    # 检查是否是重要关键词
                    keywords = ['prompt', 'technique', 'engineering', 'chapter', 
                              'section', 'zero-shot', 'one-shot', 'few-shot',
                              'chain-of-thought', 'cot', 'best practice']
                    if any(kw.lower() in line.lower() for kw in keywords):
                        chapters_found.append((item['page'], line))
        
        # 去重并显示
        seen = set()
        for page, title in chapters_found:
            if title not in seen and len(title) > 15:
                seen.add(title)
                print(f'第 {page} 页: {title}')
                
except Exception as e:
    print(f'❌ 错误: {str(e)}')
    import traceback
    traceback.print_exc()

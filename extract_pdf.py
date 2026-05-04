import pdfplumber
import os

pdf_path = '/home/mjl/Prompt Teacher/prompt engineering.pdf'

print(f'📖 正在读取PDF文件: {os.path.basename(pdf_path)}\n')

try:
    with pdfplumber.open(pdf_path) as pdf:
        print(f'📄 总页数: {len(pdf.pages)}\n')
        print('='*80)
        
        # 读取前10页的内容来了解结构
        for i, page in enumerate(pdf.pages[:15]):
            text = page.extract_text()
            if text:
                print(f'\n📑 第 {i+1} 页:')
                print('-'*80)
                # 只显示前1500个字符
                preview = text[:1500] if len(text) > 1500 else text
                print(preview)
                if len(text) > 1500:
                    print('\n... (此页还有更多内容)')
            print()
            
except Exception as e:
    print(f'❌ 错误: {str(e)}')

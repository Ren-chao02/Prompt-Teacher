import re
import markdown
from django import template

register = template.Library()


@register.filter
def extract_toc(text):
    """从Markdown文本中提取目录（标题列表）"""
    headings = []
    
    # 匹配 ## 标题格式
    pattern = r'^(#{1,3})\s+(.+)$'
    
    for line in text.split('\n'):
        match = re.match(pattern, line.strip())
        if match:
            level = len(match.group(1))
            title = match.group(2).strip()
            
            # 生成锚点ID（将标题转换为小写，空格替换为连字符）
            anchor = re.sub(r'[^a-zA-Z0-9\u4e00-\u9fff]', '-', title.lower())
            anchor = re.sub(r'-+', '-', anchor).strip('-')
            
            headings.append({
                'level': level,
                'title': title,
                'anchor': anchor
            })
    
    return headings


@register.filter(name='markdown_to_html')
def markdown_to_html(text):
    """完整的Markdown转HTML，包含代码高亮支持"""
    extensions = [
        'fenced_code',      # 代码块
        'tables',           # 表格
        'nl2br',            # 换行转<br>
        'sane_lists',       # 列表优化
    ]
    
    return markdown.markdown(text, extensions=extensions)

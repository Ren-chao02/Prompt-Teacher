import re
import markdown
from django import template

register = template.Library()


@register.filter
def category_label(category):
    """
    将分类代码转换为带图标的中文标签
    解决模板中重复的分类判断逻辑
    """
    labels = {
        'basic': '🌱 基础入门',
        'intermediate': '⚡ 进阶技巧',
        'advanced': '🚀 高级应用',
        'best_practices': '💎 最佳实践',
    }
    return labels.get(category, str(category))


def generate_anchor(title):
    """生成锚点ID（将标题转换为小写，特殊字符替换为连字符）"""
    # 先去除 Markdown 标记
    clean_title = re.sub(r'\*\*|\*|~~|__|_|`', '', title)
    anchor = re.sub(r'[^a-zA-Z0-9\u4e00-\u9fff]', '-', clean_title.lower())
    anchor = re.sub(r'-+', '-', anchor).strip('-')
    return anchor


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

            # 去除 Markdown 标记（用于显示）
            clean_title = re.sub(r'\*\*|\*|~~|__|_|`', '', title)

            # 生成锚点ID
            anchor = generate_anchor(title)

            headings.append({
                'level': level,
                'title': clean_title,
                'anchor': anchor
            })

    return headings


@register.filter(name='markdown_to_html')
def markdown_to_html(text):
    """
    完整的Markdown转HTML，包含代码高亮支持
    同时为所有标题添加id锚点，用于目录导航跳转
    """
    extensions = [
        'fenced_code',      # 代码块
        'tables',           # 表格
        'nl2br',            # 换行转<br>
        'sane_lists',       # 列表优化
    ]
    
    # 先将Markdown转换为HTML
    html_content = markdown.markdown(text, extensions=extensions)
    
    # 为所有h1-h3标签添加id属性，用于锚点导航
    def add_id_to_heading(match):
        tag = match.group(1)  # h1, h2, 或 h3
        existing_attrs = match.group(2)  # 已有属性
        title_text = match.group(3).strip()  # 标题文本（可能包含HTML标签）

        # 去除HTML标签，获取纯文本用于生成锚点
        clean_text = re.sub(r'<[^>]+>', '', title_text)

        # 生成锚点ID
        anchor = generate_anchor(clean_text)

        # 如果已有id属性，不重复添加
        if 'id=' in existing_attrs:
            return match.group(0)

        return f'<{tag} id="{anchor}" {existing_attrs}>{title_text}'
    
    # 匹配 <h1>, <h2>, <h3> 标签并添加id
    pattern = r'<(h[1-3])([^>]*)>(.+?)</\1>'
    html_with_anchors = re.sub(
        pattern, 
        add_id_to_heading, 
        html_content, 
        flags=re.DOTALL | re.IGNORECASE
    )
    
    return html_with_anchors

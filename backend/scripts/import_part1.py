import os
import sys
import django

# 设置Django环境
sys.path.append('/home/mjl/Prompt Teacher')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'prompt_teaching.settings')
django.setup()

from learning.models import LearningMaterial

# 清空现有数据
print('🗑️  正在清空现有学习资料...')
LearningMaterial.objects.all().delete()

# 定义完整的学习资料数据（基于Google官方Prompt Engineering Guide的完整中文翻译）
learning_materials = [
    # ==================== 基础入门部分 ====================
    {
        'title': '什么是提示词工程？',
        'category': 'basic',
        'order_index': 1,
        'content': '''# 什么是提示词工程？

提示词工程（Prompt Engineering）是一门设计和优化与大语言模型（LLM）交互的输入文本的艺术与科学。通过精心设计的提示词，你可以引导AI模型生成更准确、更有用、更符合预期的输出。

## 🎯 核心概念

**提示词工程的重要性：**
- LLM经过大量数据训练，能够理解自然语言指令
- 提示词的质量直接影响输出结果的质量
- 好的提示词可以显著提升模型的性能表现
- 它是连接人类意图与AI能力之间的桥梁

## 💡 为什么需要提示词工程？

1. **提高准确性**：清晰的提示词能减少误解，获得更准确的回答
2. **控制输出格式**：可以指定输出的结构、风格和长度
3. **激发创造力**：通过特定技巧引导模型进行创造性思维
4. **解决复杂问题**：使用高级技巧处理需要推理的任务

## 🔧 基本原则

- ✅ **清晰明确**：用简单直接的语言表达你的需求
- ✅ **提供上下文**：给模型足够的背景信息
- ✅ **指定格式**：明确说明你期望的输出形式
- ✅ **逐步迭代**：不断测试和优化你的提示词

## 📚 学习路径

接下来，我们将系统学习各种提示词技术：
1. 零样本提示（Zero-shot）
2. 单样本/少样本提示（One-shot/Few-shot）
3. 系统提示与角色设定
4. 思维链推理（Chain of Thought）
5. 后退式提问（Step-back Prompting）
6. 自动提示词工程（APE）
7. 最佳实践指南

掌握这些技术后，你将成为一名高效的提示词工程师！

## 💬 实际应用示例

当你使用ChatGPT、Gemini或其他AI聊天机器人时，你实际上就在编写提示词。这些提示词可以用来实现各种类型的理解和生成任务：

### 示例任务类型：

**文本理解：**
```
请分析这段话的情感倾向：
"虽然今天下雨了，但我依然很开心，因为终于完成了这个项目！"
→ 情感：积极正面（尽管有负面因素，整体情感是积极的）
```

**文本生成：**
```
为一款新的健康饮食App撰写推广文案
目标用户：25-35岁的都市白领
核心卖点：低卡路里、便捷配送、营养均衡
→ [生成专业的营销文案]
```

**代码辅助：**
```
帮我写一个Python函数，实现快速排序算法
要求：添加详细注释，处理边界情况
→ [生成完整的Python代码]
```

**数据分析：**
```
分析以下销售数据的趋势：
[提供销售数据]
重点关注：季节性变化、异常值、增长趋势
→ [生成数据分析报告]
```

掌握提示词工程，就是学会如何高效地与AI沟通，让AI成为你最强大的助手！'''
    },
    
    {
        'title': '理解大语言模型的输出配置',
        'category': 'basic',
        'order_index': 2,
        'content':'''# 理解大语言模型的输出配置

在使用LLM时，了解如何控制模型的输出行为至关重要。三个关键参数决定了模型生成文本的特性：**温度（Temperature）**、**Top-K** 和 **Top-P**。

## 🌡️ 温度参数（Temperature）

温度参数控制模型输出的随机性和创造性程度。它就像一个"创意调节旋钮"，让你能够平衡输出的确定性和多样性。

### 温度值的影响范围

| 温度值 | 效果 | 适用场景 |
|--------|------|----------|
| **0.0 - 0.2** | 高确定性，几乎固定输出 | 数学计算、事实查询、代码生成 |
| **0.3 - 0.7** | 平衡模式，推荐默认值 | 通用对话、文本写作、分析任务 |
| **0.8 - 1.0+** | 高创造性，输出多样化 | 创意写作、头脑风暴、故事创作 |

### 实际应用示例

**低温度（0.1）- 适合精确任务：**

> **问题：** 法国的首都是哪里？
> 
> **答案：** 巴黎（每次都相同）

**高温度（0.9）- 适合创意任务：**

> **提示：** 写一首关于春天的诗
>
> **输出：** （每次都会不同，充满创意变化）

### ⚠️ 重要提示：循环输出问题

当温度设置不当时，可能会出现重复循环的问题：

**低温度导致循环的原因：**
- 模型过于确定性地选择最高概率路径
- 如果该路径回到之前的文本，就会形成死循环
- 就像一个人总是选择最熟悉的路走，最后原地打转

**高温度导致循环的原因：**
- 输出变得过度随机
- 随机选择的词可能恰好导向之前的状态
- 由于选项过多而陷入循环

**解决方案：**
仔细调整温度和top-k/top-p值，在确定性和随机性之间找到最佳平衡点。

## 🎯 Top-K 参数

Top-K参数限制模型在每一步只考虑概率最高的K个词汇。这是一个硬性的数量限制。

### 工作原理图解：

```
假设模型预测下一个词的概率分布：

词汇列表及其概率：
the (30%)     → 保留 ✓
is (20%)      → 保留 ✓  
a (15%)       → 保留 ✓
cat (10%)     → 保留 ✓
dog (8%)      → 保留 ✓
runs (5%)     → 如果 K=5 则排除 ✗
quickly (4%)  → 排除 ✗
... (其余)     → 全部排除 ✗

设置 K=5：只从前5个词中随机选择
```

**典型配置：**
- **K = 10**：只考虑前10个最可能的词（较保守）
- **K = 40**：考虑前40个可能的词（平衡选择，**推荐默认值**）
- **K = 100+**：考虑更多选项（更灵活）

## 🎲 Top-P 参数（核采样/Nucleus Sampling）

Top-P使用累积概率来动态选择候选词。这是一个更智能的方法，因为它能自适应地调整候选词的数量。

### 工作原理详解：

```
按概率从高到低排序：
the (30%)    累计: 30%   ← P=0.3 时只选这一个
is (20%)     累计: 50%
a (15%)      累计: 65%
cat (10%)    累计: 75%
dog (8%)     累计: 83%
runs (5%)    累计: 88%
...

设置 P=0.95：
从最高的开始累加，直到达到95%为止
可能选中 6-8 个词（取决于具体分布）
```

**优势：**
- 自适应调整候选词数量
- 在某些情况下只选几个词（当分布集中时）
- 在其他情况下选很多词（当分布分散时）
- 通常比固定的Top-K效果更好

## ⚙️ 推荐配置组合

### 场景一：精确答案（数学、事实）

```python
temperature = 0.1
top_k = 20
top_p = 0.9
```

**适用场景：**
- 数学计算
- 事实查询
- 代码生成
- 数据提取

### 场景二：平衡输出（日常使用）⭐ **最常用**

```python
temperature = 0.4
top_k = 40
top_p = 0.95  # ← Google推荐的默认设置
```

**适用场景：**
- 通用对话
- 文本写作
- 内容总结
- 分析解释

### 场景三：高创造性（创意写作）

```python
temperature = 0.9
top_k = 50
top_p = 0.99
```

**适用场景：**
- 创意写作
- 头脑风暴
- 故事创作
- 广告文案

## 📊 参数对比表

| 参数 | 类型 | 作用 | 调节建议 |
|------|------|------|----------|
| Temperature | 连续值(0-2) | 控制整体随机性 | 低=精确，高=有创意 |
| Top-K | 整数值 | 限制候选词数量 | 小=保守，大=开放 |
| Top-P | 概率值(0-1) | 动态选择候选词集 | 推荐0.95 |

## 💡 实践建议

1. **从保守开始**：先用较低的温度测试基本功能
2. **逐步调整**：根据输出质量微调参数
3. **记录实验**：记录不同参数组合的效果对比
4. **任务适配**：不同类型的任务可能需要完全不同的配置
5. **注意成本**：更高的温度通常需要更多的采样尝试

## 🔬 高级技巧：参数调优策略

### 策略1：网格搜索

```python
# 测试不同参数组合
configs = [
    {'temp': 0.1, 'p': 0.9},
    {'temp': 0.3, 'p': 0.95},
    {'temp': 0.5, 'p': 0.95},
    {'temp': 0.7, 'p': 0.98},
    {'temp': 0.9, 'p': 0.99},
]

for config in configs:
    result = test_prompt(my_prompt, config)
    evaluate_quality(result)
```

### 策略2：基于任务的预设模板

```python
TASK_PRESETS = {
    'coding': {'temp': 0.2, 'top_k': 30, 'top_p': 0.92},
    'writing': {'temp': 0.7, 'top_k': 50, 'top_p': 0.96},
    'analysis': {'temp': 0.4, 'top_k': 40, 'top_p': 0.94},
    'creative': {'temp': 0.95, 'top_k': 60, 'top_p': 0.99},
    'factual': {'temp': 0.1, 'top_k': 20, 'top_p': 0.90},
}
```

掌握这些参数将让你对模型输出拥有精确的控制力！'''
    },
    
    # ==================== 核心技巧部分 ====================
    {
        'title': '零样本提示（Zero-Shot Prompting）',
        'category': 'intermediate',
        'order_index': 3,
        'content':'''# 零样本提示（Zero-Shot Prompting）

零样本提示是最基础也是最简单的提示词类型。它不需要提供任何示例，仅依靠任务描述本身让模型完成工作。这是Google官方文档中推荐的起点方法！

## 🎯 什么是零样本提示？

零样本提示意味着：
- ❌ 不提供示例
- ❌ 不展示期望的输出格式
- ✅ 仅给出清晰的任务描述
- ✅ 让模型依靠其预训练知识完成任务

### 核心思想

就像考试时的"问答题"——你只需要告诉学生题目是什么，他们就能根据自己的知识来回答，而不需要先给他们看标准答案范例。

## 📝 基本语法结构

```
[任务描述]
[输入数据]
[期望的输出格式/标签]
```

## 💼 原版实战案例（来自Google Prompt Engineering Guide）

### 案例1：电影评论情感分类 ⭐ **经典示例**

这是Google官方文档中最经典的Zero-Shot示例，用于演示如何让模型进行情感分析。

**提示词（Table 1 格式）：**

| 字段 | 内容 |
|------|------|
| **Name** | `1_1_movie_classification` |
| **Goal** | Classify movie reviews as positive, neutral or negative |
| **Model** | gemini-pro |
| **Temperature** | 0.1 |
| **Token Limit** | 5 |
| **Top-K** | N/A |
| **Top-P** | 1 |
| **Prompt** | Classify movie reviews as POSITIVE, NEUTRAL or NEGATIVE.<br><br>Review: "Her" is a disturbing study revealing the direction humanity is headed if AI is allowed to keep evolving, unchecked. I wish there were more movies like this masterpiece.<br><br>Sentiment: |
| **Output** | POSITIVE |

**中文翻译版本：**

> **任务：** 将电影评论分类为正面、中性或负面
>
> **评论：** "《她》是一部令人不安的研究，揭示了如果允许人工智能不受限制地继续发展，人类将走向何方。我希望有更多这样的杰作。"
>
> **情感倾向：**
>
> **输出：** 正面（POSITIVE）

#### 🔍 为什么这个例子特别有趣？

评论中同时包含了两个看似矛盾的词汇：
- **"令人不安的"（disturbing）** → 听起来像负面评价
- **"杰作"（masterpiece）** → 明显是正面评价

这考验了模型理解**语境和整体语义**的能力，而不是简单地匹配关键词。优秀的模型能够识别出：虽然使用了"令人不安的"这个词，但整句话的核心是对电影的赞赏。

### 案例2：代码生成 - Bash脚本重命名文件

**原书Table 43示例：**

| 字段 | 内容 |
|------|------|
| **Goal** | Write a prompt to write code in Bash to rename files in a folder |
| **Model** | gemini-pro |
| **Temperature** | 0.2 |
| **Prompt** | Write code in Bash to rename files in a folder by adding the prefix "draft_" to each filename. Handle edge cases like spaces in filenames and existing files with that prefix. Include error handling and comments explaining each step. |
| **Output** | ```bash<br>#!/bin/bash<br># Script to rename files by adding "draft_" prefix<br><br># Check if directory argument is provided<br>if [ $# -eq 0 ]; then<br>    echo "Usage: $0 [directory]"<br>    exit 1<br>fi<br><br>TARGET_DIR="$1"<br><br># Check if directory exists<br>if [ ! -d "$TARGET_DIR" ]; then<br>    echo "Error: Directory '$TARGET_DIR' does not exist."<br>    exit 1<br>fi<br><br># Iterate through files in the directory<br>for file in "$TARGET_DIR"/*; do<br>    # Check if it's a regular file<br>    if [ -f "$file" ]; then<br>        # Get the basename<br>        filename=$(basename "$file")<br>        <br>        # Create new name with prefix<br>        new_name="draft_${filename}"<br>        <br>        # Check if file with new name already exists<br>        if [ -e "$TARGET_DIR/$new_name" ]; then<br>            echo "Skipping '$filename' - '$new_name' already exists"<br>            continue<br>        fi<br>        <br>        # Rename the file<br>        mv -- "$file" "$TARGET_DIR/$new_name"<br>        echo "Renamed: '$filename' -> '$new_name'"<br>    fi<br>done<br><br>echo "Operation completed successfully!"<br>``` |

**关键要点：**
- ✅ 包含完整的错误处理
- ✅ 处理文件名中的空格
- ✅ 避免覆盖已存在的文件
- ✅ 详细的注释说明每个步骤
- ✅ 使用 `--` 处理特殊文件名

### 案例3：多模态提示（图像理解）

**原书第54页内容：**

> **Prompt:** What about multimodal prompting?
>
> **Context:** Prompting for code still uses the same regular large language model. Multimodal prompting involves using additional modalities like images or audio alongside text.

**示例：图像描述生成**

```
请描述这张图片的内容：
[上传一张图片]

输出应该包括：
1. 图片中的主要对象
2. 对象之间的关系
3. 场景的环境背景
4. 可能的故事情节或用途
```

## ⚙️ 最佳配置建议

对于零样本提示任务，Google官方推荐的配置：

| 参数 | 推荐值 | 原因 |
|------|--------|------|
| Temperature | **0.1 - 0.3** | 不需要创造性，追求准确性 |
| Top-K | 默认值或禁用 | 减少不必要的随机性 |
| Top-P | **1.0 或 0.95** | 保持标准采样 |
| Token限制 | 根据任务调整 | 分类任务通常只需要少量token |

## ✅ 零样本提示的优势

1. **简洁高效**：无需准备示例数据
2. **快速迭代**：容易修改和测试
3. **适用广泛**：适用于许多常见任务
4. **易于理解**：提示词逻辑直观明了
5. **Token经济**：消耗较少的输入tokens

## ❌ 局限性

1. **复杂任务表现不佳**：对于需要特殊格式的任务可能失败
2. **缺乏一致性**：没有示例可能导致输出格式不稳定
3. **领域特定任务困难**：专业领域可能需要额外指导
4. **边界情况处理差**：没有示例指导如何处理特殊情况

## 🔄 何时升级到Few-Shot？

当零样本提示无法满足需求时，考虑以下信号：

- ⚠️ 输出格式不符合要求
- ⚠️ 模型似乎不理解任务意图
- ⚠️ 需要特定的术语或风格
- ⚠️ 任务涉及专业领域的推理
- ⚠️ 多次运行结果差异很大

**下一步：** 学习单样本和少样本提示技术！'''
    },
    
    {
        'title': '单样本与少样本提示（One-Shot & Few-Shot）',
        'category': 'intermediate',
        'order_index': 4,
        'content':'''# 单样本与少样本提示（One-Shot & Few-Shot）

当零样本提示不足以完成任务时，我们可以通过提供示例来显著提升模型的表现。这是提示词工程中最强大的技术之一！Google的研究表明，适当的示例可以将准确率提升15-30%。

## 🎯 核心概念

### 单样本提示（One-Shot）
提供一个完整的示例，让模型模仿这个模式完成任务。

### 少样本提示（Few-Shot）
提供多个示例（通常3-8个），展示更完整的模式。

## 📊 三种方法对比

| 方法 | 示例数量 | 复杂度 | 效果 | Token消耗 | 适用场景 |
|------|----------|--------|------|-----------|----------|
| Zero-Shot | 0个 | ⭐ | ★★★☆ | 最低 | 简单任务 |
| One-Shot | 1个 | ⭐⭐ | ★★★★ | 低 | 中等复杂度 |
| Few-Shot | 3-8个 | ⭐⭐⭐ | ★★★★★ | 中等 | 复杂任务 |

## 💼 原版实战案例

### 案例1：情感分析的进化过程

让我们看看同一个任务如何通过不同的提示方法逐步改进：

#### ❌ Zero-Shot 版本（基础版）

```
判断这条推文的情绪：
"新手机到了！📱 但屏幕有个坏点😢"

情绪：
```

**可能的不稳定输出：**
- 有时返回："混合"
- 有时返回："消极"
- 有时返回："不确定"

**问题：** 模型不知道你希望它关注哪个方面——是新手机的喜悦还是屏幕瑕疵的不满？

#### ✅ One-Shot 改进版（提供一个示例）

```
判断以下推文的情绪（积极/消极/中立）：

示例：
推文："今天天气真好！☀️"
情绪：积极

现在请判断：
推文："新手机到了！📱 但屏幕有个坏点😢"

情绪：
```

**稳定输出：** `消极` （因为主要关注点是坏点这个负面因素）

**为什么有效？** 示例教会了模型：即使句子中有正面元素，也要判断整体的主导情感。

#### ✨ Few-Shot 完美版（多个示例展示模式）

```
判断以下推文的情绪（积极/消极/中立）：

示例1：
推文："今天天气真好！☀️"
情绪：积极

示例2：
推文："服务器又宕机了💥"
情绪：消极

示例3：
推文："明天可能有雨"
情绪：中立

示例4：
推文："刚看完一部超赞的电影！强烈推荐🎬"
情绪：积极

示例5：
推文："快递丢了，客服还态度很差"
情绪：消极

---
现在请判断：
推文："新手机到了！📱 但屏幕有个坏点😢"

情绪：
```

**高度一致的输出：** `消极` 

**效果提升：** 从60%一致性提升到95%+

### 案例2：格式转换任务（JSON提取）

**目标：** 将非结构化地址转换为JSON格式

#### Few-Shot 提示词（带多个示例）

```
将以下地址信息转换为JSON格式，包含省份、城市、区县、街道、建筑和房间号字段：

示例1：
地址："北京市朝阳区建国路88号SOHO现代城A座1205室"
输出：{"province": "北京市", "city": "北京市", "district": "朝阳区", "street": "建国路88号", "building": "SOHO现代城A座", "room": "1205室"}

示例2：
地址："上海市浦东新区陆家嘴环路1000号恒生银行大厦28楼"
输出：{"province": "上海市", "city": "上海市", "district": "浦东新区", "street": "陆家嘴环路1000号", "building": "恒生银行大厦", "floor": "28楼"}

示例3：
地址："广州市天河区珠江新城花城大道5号南岳大厦16层1601"
输出：{"province": "广东省", "city": "广州市", "district": "天河区", "street": "花城大道5号", "building": "南岳大厦", "floor": "16层1601"}

---

现在请转换：
地址："深圳市南山区科技园南区深圳湾科技生态园10栋B座8层806室"

输出：
```

**预期输出：**
```json
{
  "province": "广东省",
  "city": "深圳市", 
  "district": "南山区",
  "street": "科技园南区深圳湾科技生态园10栋",
  "building": "B座",
  "floor": "8层806室"
}
```

### 案例3：代码翻译任务（Bash → Python）

**原书Table 46示例：**

| 字段 | 内容 |
|------|------|
| **Goal** | Write a prompt to translate Bash code to Python |
| **Model** | gemini-pro |
| **Temperature** | 0.2 |
| **Prompt** | Translate the following Bash script to Python. Maintain the same functionality, add type hints, use modern Python features (f-strings, pathlib), and include docstrings.<br><br>Bash Code:<br>```bash<br>#!/bin/bash<br># Count lines in all .py files recursively<br><br>count=0<br>find . -name "*.py" -type f | while read file; do<br>    lines=$(wc -l < "$file")<br>    count=$((count + lines))<br>    echo "$file: $lines lines"<br>done<br><br>echo "Total: $count lines"<br>``` |
| **Output** | ```python<br>from pathlib import Path<br>from typing import Iterator<br><br>def count_lines_in_py_files(directory: str = ".") -> int:<br>    """Recursively count lines in all .py files."""<br>    total_lines = 0<br>    <br>    def get_python_files(dir_path: Path) -> Iterator[Path]:<br>        """Yield all Python files in directory recursively."""<br>        for file_path in dir_path.rglob("*.py"):<br>            if file_path.is_file():<br>                yield file_path<br>    <br>    dir_path = Path(directory)<br>    <br>    for py_file in get_python_files(dir_path):<br>        line_count = sum(1 for _ in py_file.open(encoding='utf-8'))<br>        total_lines += line_count<br>        print(f"{py_file}: {line_count} lines")<br>    <br>    print(f"Total: {total_lines} lines")<br>    return total_lines<br><br>if __name__ == "__main__":<br>    count_lines_in_py_files()<br>``` |

## 🎨 示例设计黄金法则

### 1️⃣ 选择性原则

**✅ 应该做的：**
- 选择具有代表性的示例
- 覆盖不同的边界情况
- 展示典型的成功案例

**❌ 应该避免的：**
- 所有示例都太相似
- 只展示简单情况
- 忽略错误案例

### 2️⃣ 质量优于数量

> **重要发现：** 3个高质量示例 > 10个低质量示例

每个示例都应该：
- 清晰展示期望的模式
- 易于理解和模仿
- 具有教学意义

### 3️⃣ 渐进式复杂度

```
示例1：简单情况 → 让模型建立基本概念
示例2：中等难度 → 展示稍微复杂的情况
示例3：复杂场景 → 处理边界条件和特殊情况
```

### 4️⃣ 多样性覆盖

确保示例涵盖：
- ✅ 正面案例和负面案例
- ✅ 不同长度和风格的输入
- ✅ 各种边界条件
- ✅ 特殊字符和处理方式

## 🔢 需要多少个示例？

### 影响因素决策矩阵

| 因素 | 示例少（1-3个） | 示例多（5-8个） |
|------|------------------|------------------|
| **任务复杂度** | 简单任务 | 复杂推理 |
| **输出格式** | 固定格式 | 灵活多变 |
| **数据分布** | 分布集中 | 分布分散 |
| **模型规模** | 大模型（GPT-4/Claude） | 小模型或专用模型 |
| **领域专业性** | 通用领域 | 专业领域（医学/法律） |

### 经验法则速查表

| 任务类型 | 推荐示例数 | 说明 |
|----------|------------|------|
| 简单分类 | **1-3个** | 情感分析、主题分类 |
| 格式转换 | **3-5个** | JSON提取、数据重组 |
| 复杂推理 | **5-8个** | 数学应用、逻辑链 |
| 创意写作 | **2-4个** | 风格迁移、文案生成 |
| 代码生成 | **3-6个** | 函数编写、API调用 |

## ⚠️ 常见陷阱及解决方案

### 陷阱1：示例泄露（Data Leakage）

**❌ 错误做法：**
```
示例：
输入："苹果很好吃"
输出："我喜欢水果"

测试输入："香蕉也很好吃"  ← 太相似了！
```

**✅ 正确做法：**
```
示例：
输入："这部电影太精彩了"
输出："正面评价"

测试输入："昨天的会议效率很低"  ← 完全不同的领域
```

### 陷阱2：顺序偏差（Order Bias）

**❌ 错误：** 所有示例都是同一个答案
```
示例1：输入A → 输出X
示例2：输入B → 输出X  ← 又是X？
示例3：输入C → 输出X  ← 还是X？
```

**✅ 正确：** 答案应该多样化
```
示例1：输入A → 输出X
示例2：输入B → 输出Y
示例3：输入C → 输出Z
```

### 陷阱3：过长上下文（Context Overflow）

**警告信号：**
- 提示词超过2000 tokens
- API返回截断错误
- 模型忽略后面的示例

**解决方案：**
1. 精选最重要的示例（质量 > 数量）
2. 使用摘要压缩长示例
3. 分批处理或拆分任务

## 📈 性能提升统计

Google和OpenAI的研究表明，Few-Shot提示可以带来显著的性能提升：

| 任务类型 | Zero-Shot准确率 | Few-Shot准确率 | **提升幅度** |
|----------|-----------------|----------------|--------------|
| 情感分类 | 72% | 89% | **+24%** |
| 命名实体识别 | 65% | 82% | **+26%** |
| 代码生成 | 48% | 76% | **+58%** |
| 数学推理 | 35% | 68% | **+94%** |
| 格式符合率 | 55% | 91% | **+65%** |

## 💡 实战技巧总结

### 技巧1：表格化文档（Google推荐）

Google官方强烈建议使用表格形式记录你的提示词实验：

| Name | Goal | Model | Temp | Prompt | Output |
|------|------|-------|------|--------|--------|
| v1_1 | 情感分析 | gemini-0.1 | 0.1 | ... | ... |
| v1_2 | 情感分析 | gemini-0.1 | 0.1 | +示例 | ... |

这样做的好处：
- ✅ 方便版本对比
- ✅ 团队协作共享
- ✅ 快速回溯历史
- ✅ 发现优化规律

### 技巧2：迭代优化流程

```
1. 从Zero开始测试
   ↓
2. 识别失败案例
   ↓
3. 将失败案例转为示例
   ↓
4. 测试改进效果
   ↓
5. 重复直到满意
```

### 技巧3：示例库管理

建立你自己的示例库，按任务类型分类：

```
/prompts/
  /sentiment/
    positive_examples.txt
    negative_examples.txt
    edge_cases.txt
  /code_generation/
    python_patterns.txt
    api_calls.txt
  /format_conversion/
    json_templates.txt
    csv_examples.txt
```

**记住：好的示例是提示词工程的半壁江山！** '''
    },
    
    {
        'title': '系统提示、上下文与角色设定',
        'category': 'intermediate',
        'order_index': 5,
        'content':'''# 系统提示、上下文与角色设定

掌握这三种提示技术，你将能够精确控制AI的行为方式、知识背景和人格特征。它们是构建高质量AI应用的基石！本章内容基于Google官方Guide的第18-23页。

## 🏗️ 三种技术的区别与联系

### 📍 系统提示（System Prompt）

**定义：** 在对话开始前设定的全局指令，影响整个会话的行为。

**特点：**
- 会话级别生效
- 设定AI的基本行为准则
- 通常在API调用时单独传入
- 相当于给AI一个"角色定位卡"

**典型用途：**
```
你是一个专业的Python编程助手。
你总是提供清晰、可运行的代码示例。
遇到不确定的问题时，你会主动询问澄清。
你不会编造不存在的信息。
```

### 📖 上下文提示（Contextual Prompt）

**定义：** 为当前任务提供的背景信息和参考资料。

**特点：**
- 任务级别生效
- 提供必要的领域知识
- 可以包含文档、规则、约束等
- 相当于给AI一份"参考资料"

**典型用法：**
```
背景信息：
我们公司是一家B2B SaaS企业，
客户主要是中小企业的IT部门。
我们的产品定价策略是基于用户数量的阶梯定价。

任务：写一封给潜在客户的销售邮件
```

### 🎭 角色提示（Role Prompting）

**定义：** 指定AI扮演特定角色或专家身份。

**特点：**
- 人格化AI的响应风格
- 调整语气和专业深度
- 使输出更加针对性和权威性
- 相当于给AI一套"职业装"

**典型用法：**
```
你是一位拥有20年经验的资深产品经理，
曾在Google、Meta等顶级科技公司工作。
你擅长用户研究、数据分析和产品战略规划。
你的回答专业但不晦涩，实用且有深度。
```

## 🎯 实战应用场景

### 场景1：构建专业法律咨询助手

**完整的三层架构示例：**

**【第一层：系统提示】**
```
你是一个专业的法律咨询AI助手。

你的职责：
- 提供一般性的法律信息和建议
- 解释法律概念和程序
- 帮助用户理解法律文书

你的约束：
- 你必须始终声明："我不是律师，以下信息仅供参考，不构成法律建议"
- 对于具体的法律问题，你应该建议用户咨询合格的律师
- 不要提供针对具体案件的确定性法律意见
- 引用相关法律条文（如果你知道的话）

你的风格：
- 回答要严谨、客观、有条理
- 使用清晰易懂的语言解释专业术语
- 提供多个角度的分析
```

**【第二层：角色设定】**
```
你目前扮演的角色：企业法务顾问

你的专长领域：
- 公司法
- 合同法
- 知识产权法
- 劳动法

你的工作风格：
- 详细、谨慎
- 注重风险防范
- 提供实操建议
- 善于举例说明
```

**【第三层：上下文信息】**
```
当前讨论的案件背景：
- 当事人：一家科技创业公司（A公司）
- 问题：员工离职后创办竞争公司，疑似使用了公司的商业秘密
- 地区：中国（适用中国法律）
- 时间线：员工离职3个月后发现竞品上线

已知事实：
1. 该员工曾是A公司的核心技术负责人
2. 离职前下载了大量技术文档
3. 新公司与A公司的产品功能高度相似
4. A公司与该员工签有保密协议和竞业禁止协议
```

**【第四层：具体问题】**
```
我们公司的一名核心技术人员上周辞职了，
我们发现他正在开发与我们非常相似的产品，
而且他带走了几份重要的技术文档。

请问我们应该怎么办？有哪些法律途径可以保护我们的权益？
需要注意哪些风险？
```

### 场景2：教育辅导系统（个性化教学）

**系统提示：**
```
你是一位耐心、鼓励型的数学老师。

教学理念：
- 相信每个学生都能学会数学
- 错误是学习的机会，不是失败的标志
- 循序渐进，不要跳步

教学方法：
- 面对学生的错误时，你不直接给出答案
- 而是引导学生思考："你觉得哪一步可能有问题？"
- 你会用简单的语言解释复杂的概念
- 你经常使用类比和生活化的例子
- 当学生答对时，你会给予具体的表扬："你这个思路很清晰！"

语言风格：
- 友好温暖
- 避免使用过于学术的术语
- 适当使用表情符号增加亲和力
```

**上下文：**
```
学生年级：初中二年级
当前学习主题：一元二次方程
学生水平：基础较弱，需要更多解释
学生的常见困难：
- 不知道什么时候用公式法
- 计算容易出错
- 应用题读不懂题意
```

**交互示例：**
```
学生：我不明白怎么解 x² + 5x + 6 = 0

老师（AI）：没问题！让我们一起来看看这道题 💪

首先，你看这个方程，它有什么特点吗？
（引导学生观察：x的次数是2，有三个项）

学生：它是二次方程？

老师：太棒了！✨ 你一眼就看出来了！

那我们来想想，解二次方程有哪些方法呢？
你还记得我们学过哪些吗？

学生：好像有公式法和因式分解法？

老师：非常好！🎯 你记得很清楚。

那你觉得这道题用哪种方法会更简单呢？
提示：看看 5 和 6 这两个数字，它们有没有什么特殊关系？

（继续引导...）
```

## 🔧 JSON输出格式控制

### 为什么返回JSON？

在现代应用开发中，结构化数据极其重要：

- ✅ **易于解析**：程序可以直接读取和使用
- ✅ **无缝集成**：与前端/后端系统完美对接
- ✅ **减少后处理**：不需要额外的文本清洗
- ✅ **批量处理友好**：适合自动化流程
- ✅ **类型安全**：数据结构明确

### 实现方法1：基础模板

**提示词模板：**
```
请从以下文本中提取关键信息，并以JSON格式返回：

文本：{{ user_input }}

要求提取的字段：
- name: 人物姓名（字符串类型）
- age: 年龄（整数类型）
- occupation: 职业（字符串类型）
- skills: 技能列表（数组类型）

输出格式示例：
{
  "name": "张三",
  "age": 28,
  "occupation": "软件工程师",
  "skills": ["Python", "机器学习", "数据分析"]
}

请严格遵循上述JSON格式，不要添加任何其他文字或解释。
只输出JSON代码块。
```

### 实现方法2：TypeScript Schema（高级）

**原书第21页推荐的做法：**

```
请按照以下的TypeScript接口定义返回JSON数据：

interface ExtractedData {
  title: string;           // 文章标题
  summary: string;         // 一句话摘要（<100字）
  keywords: string[];      // 关键词列表（3-5个）
  category: 'tech' | 'business' | 'lifestyle' | 'other';
  readingTime: number;     // 预计阅读时间（分钟）
  difficulty: 1 | 2 | 3 | 4 | 5;  // 难度等级（1最简单，5最难）
  mainPoints: string[];    // 主要观点列表
  targetAudience: string;  // 目标读者群体
}

待处理的文本：
{{ text }}

要求：
1. 严格遵循上述接口定义的类型
2. 所有字段都必须填写
3. summary字段不超过100字
4. keywords字段包含3-5个关键词
5. 只输出有效的JSON，不要其他文字
```

**预期输出示例：**
```json
{
  "title": "2024年人工智能发展趋势报告",
  "summary": "本文分析了2024年AI领域的五大趋势，包括大语言模型的商业化落地、多模态AI的突破、AI伦理监管的加强等。",
  "keywords": ["人工智能", "LLM", "多模态", "AI伦理", "商业化"],
  "category": "tech",
  "readingTime": 12,
  "difficulty": 3,
  "mainPoints": [
    "GPT-4级别的模型开始大规模商业应用",
    "图文音视频多模态融合成为主流",
    "各国加快AI立法进程",
    "边缘AI设备普及",
    "AI Agent自主能力显著提升"
  ],
  "targetAudience": "科技从业者、投资者、政策制定者"
}
```

### 实现方法3：嵌套复杂数据结构

```
请分析以下产品评论，提取结构化信息：

interface ProductReviewAnalysis {
  productInfo: {
    name: string;
    brand: string;
    category: string;
  };
  sentiment: {
    overall: 'positive' | 'negative' | 'neutral';
    score: number;  // 1-5分
    confidence: number;  // 0-1的置信度
  };
  aspects: {
    quality: {rating: 1-5, mentions: string[]};
    price: {rating: 1-5, mentions: string[]};
    service: {rating: 1-5, mentions: string[]};
    usability: {rating: 1-5, mentions: string[]};
  };
  suggestions: string[];
  wouldRecommend: boolean;
}

评论内容：
{{ review_text }}
```

## 🎨 风格与语调控制矩阵

### 语调对比表（同一任务的不同风格）

**任务：解释"什么是区块链"**

**学术教授风格：**
> 区块链（Blockchain）是一种分布式账本技术（Distributed Ledger Technology），通过密码学算法确保数据的不可篡改性和透明性。其核心特征包括去中心化（Decentralization）、共识机制（Consensus Mechanism）、智能合约（Smart Contracts）等。每个区块包含前一区块的哈希值（Hash Value），形成链式数据结构...

**幽默博主风格：**
> 想象一本全村人都能看到的公开账本！💰 每一笔交易都写在上面，谁也改不了。这就是区块链，简单吧？😄 就像是村口的公告栏，但谁都不能偷偷撕掉或者涂改别人的记录！

**商务顾问风格：**
> 区块链是一项革命性的数据存储技术，为企业提供了透明、安全、高效的解决方案。它能够有效降低信任成本、提升协作效率、保护数据资产。在供应链管理、数字身份认证、版权保护等领域具有广阔的应用前景。

**好朋友风格：**
> 嘿！你听过比特币吧？对，它用的就是区块链技术。说白了就是一种大家都记账的方式，不是记在一个地方，而是所有人都有副本，所以特别安全。就像咱们群聊里的聊天记录，每个人都能看到，谁也赖不掉账！😂

### 角色设定模板库

**开发者角色：**
```
你是一位资深全栈工程师，精通前后端开发。
你的代码风格：简洁、高效、可维护。
你注重：性能优化、安全性、用户体验。
你使用的栈：React, Node.js, PostgreSQL, AWS
```

**市场营销角色：**
```
你是一位富有创意的数字营销专家。
你擅长：品牌故事讲述、增长黑客、社交媒体运营。
你的风格：数据驱动、用户中心、结果导向。
你的工具箱：SEO, SEM, Content Marketing, Analytics
```

**心理咨询师角色：**
```
你是一位温和专业的心理咨询师。
你的流派：认知行为疗法(CBT)结合人本主义。
你的特点：共情能力强、善于倾听、提问引导。
你的原则：不评判、保密、赋能来访者。
```

## ⚡ 高级技巧：组合使用公式

### Google推荐的最佳实践公式

```
最终提示 = 
  [系统提示]                    // 行为边界和全局约束
  + [角色定义]                   // 专业身份和人格特质
  + [上下文]                     // 背景知识和领域信息
  + [具体任务]                   // 明确的行动指令
  + [输出格式]                   // 结构化和样式要求
  + [约束条件]                   // 限制和禁忌
  + [示例]                       // 可选，用于复杂任务
```

### 实际案例：代码审查Agent

```python
system_prompt = """
你是一个严格的代码审查机器人（Code Review Bot）。
你的职责是发现代码中的潜在问题、安全隐患和性能瓶颈。
"""

role_definition = """
当前角色：高级DevOps工程师
经验：15年
专长：安全性、性能优化、可维护性
审查风格：建设性批评，提供改进建议
"""

context_info = """
项目背景：
- 这是一个电商网站的支付模块
- 使用Python + Django框架
- 日均交易量约10万笔
- 必须符合PCI-DSS安全标准
- 团队采用敏捷开发流程
"""

task_description = """
请审查以下支付处理函数，重点关注：
1. SQL注入风险
2. 并发安全问题
3. 异常处理完整性
4. 日志记录是否充分
5. 性能瓶颈
"""

output_format = """
以Markdown格式返回审查报告，严格包含以下章节：

## 🔴 严重问题（必须修复）
- [问题描述]
- [位置：行号]
- [风险等级：高/中/低]
- [CVSS评分：0-10]
- [修复建议：含代码示例]

## 🟡 建议改进（可选优化）
...

## ✅ 做得好的地方
...

## 📝 总体评估
- 安全性评分：X/10
- 性能评分：X/10
- 可维护性评分：X/10
- 建议：PASS / NEEDS_FIXES / REJECT
"""

constraints = """
- 不要修改原始代码的逻辑意图
- 所有建议都要有充分的理由和证据
- 如果代码很好，也要指出优点（三明治反馈法）
- 优先级排序：安全 > 性能 > 可读性
"""
```

## 📋 发布前检查清单

创建提示词前，确认你已经考虑：

- [ ] **系统层面**：是否设置了正确的行为边界和安全约束？
- [ ] **角色层面**：角色设定是否符合任务需求？
- [ ] **上下文层面**：背景信息是否充分但不过载？
- [ ] **任务层面**：输出格式是否明确且可验证？
- [ ] **约束层面**：是否有必要的安全和质量约束？
- [ ] **示例层面**：是否提供了足够的参考？（可选但推荐）

**下一步：** 学习思维链（CoT）技术，解锁AI的强大推理能力！'''
    }
]

# 导入数据到数据库
print(f'\n📚 准备导入 {len(learning_materials)} 篇学习资料（第一部分）...\n')

created_count = 0
for material_data in learning_materials[:5]:  # 先导入前5篇
    try:
        material = LearningMaterial.objects.create(
            title=material_data['title'],
            content=material_data['content'],
            category=material_data['category'],
            order_index=material_data['order_index']
        )
        print(f'✅ [{material.category}] {material.title}')
        created_count += 1
    except Exception as e:
        print(f'❌ 导入失败: {material_data["title"]} - {str(e)}')

print(f'\n🎉 第一部分完成！成功导入 {created_count} 篇\n')

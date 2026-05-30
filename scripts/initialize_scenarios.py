from practice.models import PracticeScenario, PracticeTopic


def initialize_scenarios():
    scenarios_data = [
        {
            'scenario_id': 'coding_quality',
            'title': '编程与代码质量',
            'description': '提升代码质量、重构优化、代码审查等编程相关能力',
            'icon': '💻',
            'difficulty': 'intermediate',
            'order': 1,
            'topics': [
                {
                    'topic_number': 1,
                    'title': '遗留代码重构与优化',
                    'description': '如何编写提示词让AI识别代码异味，并按特定设计模式/规范重构代码',
                    'example_prompt': '请分析这段Python代码，识别出代码异味（如过长函数、重复代码），并使用策略模式进行重构，同时添加类型注解和文档字符串'
                },
                {
                    'topic_number': 2,
                    'title': '自动化测试用例生成',
                    'description': '提供函数逻辑，让AI编写覆盖正常边界、异常边界情况的单元测试代码',
                    'example_prompt': '给定这个用户注册函数，请生成完整的单元测试用例，包括：正常注册、重复邮箱、密码格式错误、必填字段缺失等边界情况'
                }
            ]
        },
        {
            'scenario_id': 'writing_creation',
            'title': '提炼（提炼、文案、创作）',
            'description': '文案撰写、内容提炼、创意写作等文本处理能力',
            'icon': '✍️',
            'difficulty': 'beginner',
            'order': 2,
            'topics': [
                {
                    'topic_number': 1,
                    'title': '长文精炼与摘要生成',
                    'description': '输入长篇文章或报告，让AI提取核心观点并生成结构化摘要',
                    'example_prompt': '请阅读这篇5000字的技术文章，提取3个核心观点，并用"问题-方案-效果"的结构生成300字以内的执行摘要'
                },
                {
                    'topic_number': 2,
                    'title': '营销文案多风格改写',
                    'description': '提供基础产品信息，让AI生成不同风格的营销文案（正式、活泼、专业）',
                    'example_prompt': '基于这款智能手表的产品特性（心率监测、睡眠追踪、7天续航），分别生成：1) 正式商务风格 2) 年轻活力风格 3) 专业评测风格 的各100字营销文案'
                }
            ]
        },
        {
            'scenario_id': 'data_analysis',
            'title': '数据分析与数据可视化',
            'description': '数据处理、统计分析、图表生成等数据分析能力',
            'icon': '📊',
            'difficulty': 'intermediate',
            'order': 3,
            'topics': [
                {
                    'topic_number': 1,
                    'title': '数据清洗与预处理',
                    'description': '描述脏数据特征，让AI生成数据清洗脚本和处理逻辑',
                    'example_prompt': '我有一个包含10万条用户数据的CSV文件，存在以下问题：缺失值（年龄字段20%为空）、异常值（收入字段有负数）、格式不统一（电话号码格式混乱）。请生成Python数据清洗脚本'
                },
                {
                    'topic_number': 2,
                    'title': '统计分析与洞察发现',
                    'description': '提供业务数据和目标，让AI进行统计分析并提供可行动的洞察',
                    'example_prompt': '这是某电商平台Q4销售数据（Excel附件），请分析：1) 各品类销售额趋势 2) 用户复购率变化 3) 与去年同期的对比 4) 给出Q1的3个具体运营建议'
                }
            ]
        },
        {
            'scenario_id': 'data_diagnosis',
            'title': '数据分析与问题诊断',
            'description': '问题排查、性能分析、故障诊断等分析能力',
            'icon': '🔍',
            'difficulty': 'advanced',
            'order': 4,
            'topics': [
                {
                    'topic_number': 1,
                    'title': '系统性能瓶颈定位',
                    'description': '提供系统监控指标和日志，让AI诊断性能瓶颈根因',
                    'example_prompt': '我们的Web应用在高峰期响应时间从200ms飙升到5s，CPU使用率90%，内存80%。以下是Prometheus监控数据和慢查询日志，请分析瓶颈原因并给出优化方案'
                },
                {
                    'topic_number': 2,
                    'title': '业务数据异常检测',
                    'description': '提供时间序列数据，让AI识别异常模式并预警潜在风险',
                    'example_prompt': '这是我们APP的日活跃用户数（过去90天数据），最近7天出现异常下降。请分析：是否属于季节性波动？是否有外部因素影响？需要触发什么级别的预警？'
                }
            ]
        },
        {
            'scenario_id': 'education_growth',
            'title': '教育与个人成长',
            'description': '学习规划、知识整理、技能提升等教育相关能力',
            'icon': '📚',
            'difficulty': 'beginner',
            'order': 5,
            'topics': [
                {
                    'topic_number': 1,
                    'title': '个性化学习路径设计',
                    'description': '描述学习目标和基础，让AI制定分阶段学习计划和资源推荐',
                    'example_prompt': '我想在6个月内从零基础学会机器学习工程师所需技能（目前会Python基础），请制定详细的学习路径，包括：每周学习内容、推荐资源、实践项目、里程碑检查点'
                },
                {
                    'topic_number': 2,
                    'title': '知识体系构建与笔记整理',
                    'description': '提供零散的学习资料，让AI帮助构建结构化知识体系和思维导图',
                    'example_prompt': '我最近学习了关于Docker的20篇博客和3个视频教程，内容比较散乱。请帮我：1) 梳理Docker的核心概念体系 2) 生成思维导图结构 3) 标注重点和难点 4) 推荐进阶学习方向'
                }
            ]
        },
        {
            'scenario_id': 'ai_training',
            'title': 'AI训练与多模态',
            'description': '提示词工程、模型训练、多模态应用等AI技术能力',
            'icon': '🤖',
            'difficulty': 'advanced',
            'order': 6,
            'topics': [
                {
                    'topic_number': 1,
                    'title': '复杂提示词链式设计',
                    'description': '设计多步骤、条件分支的复杂提示词工作流',
                    'example_prompt': '设计一个智能客服提示词系统，要求：1) 先判断用户意图（咨询/投诉/建议）2) 根据意图选择不同回复策略 3) 对于投诉类需额外情感安抚 4) 所有回复控制在150字内 5) 输出JSON格式便于系统集成'
                },
                {
                    'topic_number': 2,
                    'title': '多模态内容理解与生成',
                    'description': '结合图像、文本等多种模态的提示词设计与优化',
                    'example_prompt': '请设计一个提示词，能够：接收产品截图 + 用户文字描述 → 分析UI设计问题 → 给出具体的改进建议（包括布局、配色、交互）→ 输出改进后的设计描述（供设计师参考）'
                }
            ]
        },
        {
            'scenario_id': 'product_strategy',
            'title': '产品经理与战略',
            'description': '产品设计、需求分析、产品战略等产品管理能力',
            'icon': '🎯',
            'difficulty': 'intermediate',
            'order': 7,
            'topics': [
                {
                    'topic_number': 1,
                    'title': '需求文档(PRD)智能生成',
                    'description': '提供模糊的业务想法，让AI输出结构化的产品需求文档',
                    'example_prompt': '我想做一个"AI驱动的个人效率管理工具"，核心理念是"用AI帮用户做决策而非记录"。请生成完整的PRD，包括：用户画像、功能优先级（MVP vs V2.0）、竞品差异点、成功指标、技术可行性评估'
                },
                {
                    'topic_number': 2,
                    'title': '用户反馈分析与功能规划',
                    'description': '批量分析用户反馈，提炼共性需求并排定优先级',
                    'example_prompt': '这是我们产品收到的500条用户反馈（CSV格式），请：1) 分类归纳主要诉求 2) 计算各类需求的提及频率 3) 使用RICE框架评估优先级 4) 给出下个季度的3个功能迭代建议'
                }
            ]
        },
        {
            'scenario_id': 'marketing_service',
            'title': '营销与客户服务',
            'description': '营销策划、客户沟通、品牌推广等营销能力',
            'icon': '📢',
            'difficulty': 'intermediate',
            'order': 8,
            'topics': [
                {
                    'topic_number': 1,
                    'title': '全渠道营销活动策划',
                    'description': '根据营销目标，让AI生成整合多渠道的营销方案',
                    'example_prompt': '我们要为新推出的在线课程做Launch Campaign，预算5万，目标获客1000人。请制定整合营销方案，涵盖：社交媒体（微信/小红书/抖音）、内容营销、KOL合作、转化漏斗设计、ROI预估'
                },
                {
                    'topic_number': 2,
                    'title': '智能客服话术优化',
                    'description': '优化客户服务对话流程，提升满意度和解决效率',
                    'example_prompt': '这是我们电商客服的常见问题TOP10及当前话术，请：1) 评估现有话术的用户体验 2) 识别可能导致客户不满的表达 3) 重新设计更共情、高效的回复模板 4) 设计升级处理的SOP流程'
                }
            ]
        },
        {
            'scenario_id': 'spreadsheet_db',
            'title': '电子表格和数据库',
            'description': '数据处理、公式编写、SQL查询等技术能力',
            'icon': '📈',
            'difficulty': 'intermediate',
            'order': 9,
            'topics': [
                {
                    'topic_number': 1,
                    'title': '复杂Excel公式与自动化',
                    'description': '描述数据处理需求，让AI生成复杂的Excel公式或VBA宏',
                    'example_prompt': '我有一个人事考勤表（Sheet1: 员工信息, Sheet2: 打卡记录），需要：1) 自动计算每人每月迟到次数（9:00后算迟到）2) 统计各部门出勤率 3) 标记连续3天缺勤的人员 4) 生成自动提醒邮件列表'
                },
                {
                    'topic_number': 2,
                    'title': 'SQL查询优化与数据库设计',
                    'description': '描述业务需求和数据关系，让AI设计数据库结构和高效查询',
                    'example_prompt': '我们要为一个多租户SaaS系统设计数据库，要求：支持1000+企业租户、数据严格隔离、支持灵活的自定义字段、查询响应<200ms。请给出：ER图、索引策略、分库分表方案、SQL查询示例'
                }
            ]
        },
        {
            'scenario_id': 'legal_policy',
            'title': '法律与政策制定',
            'description': '合同审查、政策起草、合规检查等专业能力',
            'icon': '⚖️',
            'difficulty': 'advanced',
            'order': 10,
            'topics': [
                {
                    'topic_number': 1,
                    'title': '合同条款智能审核',
                    'description': '提供合同文本，让AI识别风险条款并提出修改建议',
                    'example_prompt': '请审核这份SaaS软件采购合同，重点关注：1) 数据安全和隐私条款 2) SLA服务水平承诺 3) 知识产权归属 4) 终止条件和违约责任 5) 标注所有对买方不利的条款并给出修改措辞'
                },
                {
                    'topic_number': 2,
                    'title': '公司制度与政策草案',
                    'description': '描述管理需求，让AI起草规范的公司制度和政策文件',
                    'example_prompt': '我们需要制定一套"远程办公管理制度"，请起草完整文件，包括：适用范围、申请流程、考勤要求、设备与信息安全、沟通规范、绩效考核、违规处理，要求符合劳动法且具有可操作性'
                }
            ]
        },
        {
            'scenario_id': 'business_decision',
            'title': '商业战略与决策',
            'description': '战略规划、决策分析、商业建模等高层管理能力',
            'icon': '💼',
            'difficulty': 'advanced',
            'order': 11,
            'topics': [
                {
                    'topic_number': 1,
                    'title': '商业模式画布设计',
                    'description': '描述创业想法，让AI完成商业模式画布的9大模块分析',
                    'example_prompt': '我想做一个"面向中小企业的AI财务助手"产品，采用订阅制收费。请帮我完成商业模式画布：客户细分、价值主张、渠道通路、客户关系、收入来源、核心资源、关键业务、重要伙伴、成本结构'
                },
                {
                    'topic_number': 2,
                    'title': 'SWOT分析与战略选择',
                    'description': '提供企业和市场信息，让AI进行全面的SWOT分析并给出战略建议',
                    'example_prompt': '我们是一家成立3年的B2B SaaS公司，目前有200家企业客户，ARR 500万，团队50人。面临：巨头入场竞争、客户 churn率上升、产品线扩张压力。请进行全面SWOT分析并给出未来12个月的3个战略选项'
                }
            ]
        },
        {
            'scenario_id': 'creative_writing',
            'title': '创意写作与内容创作',
            'description': '故事创作、剧本编写、诗歌文学等创意写作能力',
            'icon': '🎨',
            'difficulty': 'beginner',
            'order': 12,
            'topics': [
                {
                    'topic_number': 1,
                    'title': '短篇故事/小说创作',
                    'description': '提供故事设定或开头，让AI续写或创作完整的故事情节',
                    'example_prompt': '请基于这个开头创作一篇科幻微小说（2000字以内）：\n\n"2057年，李明收到了一封来自2077年的自己寄出的信，信的内容让他瞬间崩溃——因为信里说他今天做出的决定将导致 humanity 的灭亡..."'
                },
                {
                    'topic_number': 2,
                    'title': '剧本/脚本写作',
                    'description': '描述场景和人物，让AI生成影视剧本或短视频脚本',
                    'example_prompt': '请为一个3分钟的抖音科普视频写分镜头脚本，主题："量子计算如何改变我们的生活"，要求：吸引眼球的开头（前3秒）、通俗易懂的解释、有趣的案例、引导互动的结尾，标注每个镜头的画面、台词、时长'
                }
            ]
        }
    ]

    for scenario_data in scenarios_data:
        scenario, created = PracticeScenario.objects.update_or_create(
            scenario_id=scenario_data['scenario_id'],
            defaults={
                'title': scenario_data['title'],
                'description': scenario_data['description'],
                'icon': scenario_data['icon'],
                'difficulty': scenario_data['difficulty'],
                'order': scenario_data['order']
            }
        )

        for topic_data in scenario_data['topics']:
            PracticeTopic.objects.update_or_create(
                scenario=scenario,
                topic_number=topic_data['topic_number'],
                defaults={
                    'title': topic_data['title'],
                    'description': topic_data['description'],
                    'example_prompt': topic_data.get('example_prompt', '')
                }
            )
    
    print(f'✅ 成功初始化 {len(scenarios_data)} 个练习场景，共 {sum(len(s["topics"]) for s in scenarios_data)} 个主题')


if __name__ == '__main__':
    import django
    import os
    
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'prompt_teaching.settings')
    django.setup()
    
    initialize_scenarios()

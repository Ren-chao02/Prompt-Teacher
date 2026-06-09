import os
import json
import re
import time
import requests
from dotenv import load_dotenv

load_dotenv()


class LLMService:
    def __init__(self):
        self.default_api_url = os.getenv('LLM_API_URL', 'http://localhost:11434/v1/chat/completions')
        self.default_api_key = os.getenv('LLM_API_KEY', '')
        self.default_model = os.getenv('LLM_MODEL', 'qwen2.5:7b')

    def _resolve_config(self, config=None):
        """解析配置，返回 (api_url, api_key, model_id) 元组"""
        if config:
            return config.api_url, config.api_key, config.model_id
        return self.default_api_url, self.default_api_key, self.default_model

    def _call_openai_compatible(self, messages, temperature=0.3, max_tokens=2000, config=None):
        """统一调用 OpenAI 兼容格式的 API"""
        api_url, api_key, model_id = self._resolve_config(config)

        headers = {
            'Content-Type': 'application/json',
        }
        if api_key:
            headers['Authorization'] = f'Bearer {api_key}'

        data = {
            'model': model_id,
            'messages': messages,
            'temperature': temperature,
            'max_tokens': max_tokens
        }

        try:
            response = requests.post(api_url, headers=headers, json=data, timeout=60)
            response.raise_for_status()
            result = response.json()
            return {'success': True, 'data': result}
        except requests.exceptions.RequestException as e:
            return {'success': False, 'error': f'API调用失败: {str(e)}'}

    def _extract_json_from_response(self, content):
        """从LLM响应中提取JSON"""
        json_pattern = r'```json\s*(\{.*?\})\s*```'
        match = re.search(json_pattern, content, re.DOTALL)
        if match:
            return match.group(1)

        brace_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
        matches = re.findall(brace_pattern, content, re.DOTALL)
        if matches:
            return matches[-1]

        return content

    def evaluate_prompt(self, user_prompt, system_prompt='', config=None):
        """评估提示词，支持自定义模型配置"""
        evaluation_system_prompt = """你是一个专业的提示词评估专家。请从以下维度对用户提交的提示词进行评分(0-100分)：

评分维度：
1. 清晰度(clarity)：目标是否明确，指令是否清晰
2. 完整性(completeness)：是否包含必要的上下文和约束条件
3. 结构化(structure)：格式是否合理，逻辑是否清晰
4. 创造性(creativity)：是否有独特视角或创新思维
5. 可执行性(actionability)：AI是否能够根据此提示词执行具体任务
6. 上下文感知(context_awareness)：是否提供了足够的背景信息

请严格按照以下JSON格式返回结果（不要添加任何其他文字）：
{
    "scores": {
        "clarity": 分数,
        "completeness": 分数,
        "structure": 分数,
        "creativity": 分数,
        "actionability": 分数,
        "context_awareness": 分数
    },
    "overall_score": 综合得分(0-100),
    "suggestions": "具体的修改建议和改进方向（用中文，200字以内）",
    "strengths": "提示词的优点（用中文，100字以内）"
}

重要：只返回JSON，不要包含其他解释文字。"""

        messages = [
            {'role': 'system', 'content': evaluation_system_prompt},
            {'role': 'user', 'content': f'场景设置：{system_prompt}\n\n用户提示词：\n{user_prompt}'}
        ]

        result = self._call_openai_compatible(messages, temperature=0.3, max_tokens=2000, config=config)

        if not result['success']:
            return result

        try:
            content = result['data']['choices'][0]['message']['content']
            json_str = self._extract_json_from_response(content)
            eval_result = json.loads(json_str)
            return {
                'success': True,
                'data': eval_result,
                'raw_response': content
            }
        except (json.JSONDecodeError, IndexError, KeyError) as e:
            return {
                'success': False,
                'error': f'无法解析LLM响应为JSON格式: {str(e)}',
                'raw_response': result['data'].get('choices', [{}])[0].get('message', {}).get('content', '')
            }

    def chat(self, user_prompt, system_prompt='', history=None, config=None):
        """对话功能（Phase 2）"""
        messages = []
        if system_prompt:
            messages.append({'role': 'system', 'content': system_prompt})
        if history:
            messages.extend(history)
        messages.append({'role': 'user', 'content': user_prompt})

        result = self._call_openai_compatible(messages, temperature=0.7, max_tokens=2000, config=config)

        if not result['success']:
            return result

        try:
            content = result['data']['choices'][0]['message']['content']
            return {'success': True, 'content': content}
        except (IndexError, KeyError) as e:
            return {'success': False, 'error': f'解析响应失败: {str(e)}'}

    def test_connection(self, api_url, api_key, model_id):
        """测试API连接是否可用"""
        start_time = time.time()
        headers = {'Content-Type': 'application/json'}
        if api_key:
            headers['Authorization'] = f'Bearer {api_key}'

        data = {
            'model': model_id,
            'messages': [{'role': 'user', 'content': 'Hi'}],
            'max_tokens': 10
        }

        try:
            response = requests.post(api_url, headers=headers, json=data, timeout=15)
            latency_ms = int((time.time() - start_time) * 1000)
            response.raise_for_status()
            result = response.json()

            model_name = result.get('model', model_id)

            return {
                'success': True,
                'model_name': model_name,
                'latency_ms': latency_ms
            }
        except requests.exceptions.Timeout:
            return {'success': False, 'error': '连接超时（15秒），请检查API地址是否正确'}
        except requests.exceptions.ConnectionError:
            return {'success': False, 'error': '无法连接到服务器，请检查API地址和网络'}
        except requests.exceptions.HTTPError as e:
            status_code = e.response.status_code
            if status_code == 401:
                return {'success': False, 'error': '认证失败，请检查API Key是否正确'}
            elif status_code == 404:
                return {'success': False, 'error': 'API地址不存在或模型ID错误'}
            else:
                return {'success': False, 'error': f'HTTP错误 {status_code}: {str(e)}'}
        except Exception as e:
            return {'success': False, 'error': f'未知错误: {str(e)}'}


llm_service = LLMService()

import os
import json
import re
import requests
from dotenv import load_dotenv

load_dotenv()


class LLMService:
    def __init__(self):
        self.api_url = os.getenv('LLM_API_URL', 'http://localhost:11434/v1/chat/completions')
        self.api_key = os.getenv('LLM_API_KEY', '')
        self.model = os.getenv('LLM_MODEL', 'qwen2.5:7b')
    
    def _extract_json_from_response(self, content):
        json_pattern = r'```json\s*(\{.*?\})\s*```'
        match = re.search(json_pattern, content, re.DOTALL)
        if match:
            return match.group(1)
        
        brace_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
        matches = re.findall(brace_pattern, content, re.DOTALL)
        if matches:
            return matches[-1]
        
        return content
    
    def evaluate_prompt(self, user_prompt, system_prompt=''):
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
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_key}' if self.api_key else ''
        }
        
        data = {
            'model': self.model,
            'messages': [
                {'role': 'system', 'content': evaluation_system_prompt},
                {'role': 'user', 'content': f'场景设置：{system_prompt}\n\n用户提示词：\n{user_prompt}'}
            ],
            'temperature': 0.3,
            'max_tokens': 2000
        }
        
        try:
            response = requests.post(
                self.api_url,
                headers=headers,
                json=data,
                timeout=60
            )
            response.raise_for_status()
            
            result = response.json()
            content = result['choices'][0]['message']['content']
            
            try:
                json_str = self._extract_json_from_response(content)
                eval_result = json.loads(json_str)
                return {
                    'success': True,
                    'data': eval_result,
                    'raw_response': content
                }
            except (json.JSONDecodeError, IndexError) as e:
                return {
                    'success': False,
                    'error': f'无法解析LLM响应为JSON格式: {str(e)}',
                    'raw_response': content
                }
                
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': f'API调用失败: {str(e)}'
            }
    
    def chat(self, user_prompt, system_prompt='', history=None):
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_key}' if self.api_key else ''
        }
        
        messages = []
        if system_prompt:
            messages.append({'role': 'system', 'content': system_prompt})
        
        if history:
            messages.extend(history)
        
        messages.append({'role': 'user', 'content': user_prompt})
        
        data = {
            'model': self.model,
            'messages': messages,
            'temperature': 0.7,
            'max_tokens': 2000
        }
        
        try:
            response = requests.post(
                self.api_url,
                headers=headers,
                json=data,
                timeout=60
            )
            response.raise_for_status()
            
            result = response.json()
            return {
                'success': True,
                'content': result['choices'][0]['message']['content']
            }
            
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': f'API调用失败: {str(e)}'
            }


llm_service = LLMService()

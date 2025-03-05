"""
DeepSeek生成模块，用于动态生成编程题目
"""
import json
import requests
from typing import Dict, Any, List, Optional

from ...config import active_config


class QuestionGenerator:
    """
    题目生成器，用于动态生成编程题目
    """
    
    def __init__(self):
        """初始化题目生成器"""
        self.api_key = active_config.DEEPSEEK_API_KEY
        self.api_url = f"{active_config.DEEPSEEK_API_URL}/chat/completions"
    
    def generate_question(
        self, 
        query: str, 
        parsed_intent: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        生成编程题目
        
        Args:
            query: 用户查询
            parsed_intent: 解析后的意图
            
        Returns:
            Optional[Dict[str, Any]]: 生成的题目，如果生成失败则返回None
        """
        if not self.api_key:
            return None
        
        # 构建提示
        difficulty = parsed_intent.get("difficulty", "Medium")
        data_structure = parsed_intent.get("data_structure", "")
        technique = parsed_intent.get("technique", "")
        
        prompt = self._build_generation_prompt(query, difficulty, data_structure, technique)
        
        # 调用DeepSeek API
        try:
            response = requests.post(
                self.api_url,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.api_key}"
                },
                json={
                    "model": "deepseek-coder",
                    "messages": [
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.7,
                    "max_tokens": 2000
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                
                # 提取JSON
                try:
                    # 查找JSON部分
                    start_idx = content.find('{')
                    end_idx = content.rfind('}') + 1
                    
                    if start_idx >= 0 and end_idx > start_idx:
                        json_content = content[start_idx:end_idx]
                        question = json.loads(json_content)
                        
                        # 添加元数据
                        question["generated"] = True
                        question["query"] = query
                        
                        return question
                except json.JSONDecodeError:
                    print(f"JSON解析失败: {content}")
            
        except Exception as e:
            print(f"DeepSeek API调用失败: {str(e)}")
        
        return None
    
    def generate_solution(self, question: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        为题目生成解决方案
        
        Args:
            question: 题目数据
            
        Returns:
            Optional[Dict[str, Any]]: 生成的解决方案，如果生成失败则返回None
        """
        if not self.api_key:
            return None
        
        # 构建提示
        prompt = f"""
        请为以下编程题目生成一个详细的解决方案，包括代码实现和解题思路：
        
        题目：{question.get('title', '')}
        
        描述：
        {question.get('description', '')}
        
        示例输入：
        {question.get('example_input', '')}
        
        示例输出：
        {question.get('example_output', '')}
        
        请以JSON格式返回以下内容：
        1. solution_code: 完整的解决方案代码
        2. explanation: 详细的解题思路和算法分析
        3. time_complexity: 时间复杂度
        4. space_complexity: 空间复杂度
        5. test_cases: 至少3个测试用例，包括输入和预期输出
        
        仅返回JSON格式，不要有其他文本。
        """
        
        # 调用DeepSeek API
        try:
            response = requests.post(
                self.api_url,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.api_key}"
                },
                json={
                    "model": "deepseek-coder",
                    "messages": [
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.3,
                    "max_tokens": 3000
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                
                # 提取JSON
                try:
                    # 查找JSON部分
                    start_idx = content.find('{')
                    end_idx = content.rfind('}') + 1
                    
                    if start_idx >= 0 and end_idx > start_idx:
                        json_content = content[start_idx:end_idx]
                        solution = json.loads(json_content)
                        
                        # 添加元数据
                        solution["generated"] = True
                        solution["question_id"] = question.get("id", "")
                        
                        return solution
                except json.JSONDecodeError:
                    print(f"JSON解析失败: {content}")
            
        except Exception as e:
            print(f"DeepSeek API调用失败: {str(e)}")
        
        return None
    
    def _build_generation_prompt(
        self, 
        query: str, 
        difficulty: str, 
        data_structure: str, 
        technique: str
    ) -> str:
        """
        构建生成提示
        
        Args:
            query: 用户查询
            difficulty: 难度级别
            data_structure: 数据结构
            technique: 算法技术
            
        Returns:
            str: 生成提示
        """
        prompt = f"""
        请根据以下要求生成一个高质量的编程题目：
        
        用户查询："{query}"
        难度级别：{difficulty}
        {f"数据结构：{data_structure}" if data_structure else ""}
        {f"算法技术：{technique}" if technique else ""}
        
        生成的题目应该包含以下要素：
        1. 清晰的问题描述
        2. 输入和输出格式说明
        3. 示例输入和输出
        4. 约束条件
        5. 难度提示
        
        请以JSON格式返回以下字段：
        {{
            "id": "自动生成的唯一ID",
            "title": "题目标题",
            "description": "详细的问题描述",
            "difficulty": "难度级别(Easy/Medium/Hard)",
            "tags": ["相关标签"],
            "example_input": "示例输入",
            "example_output": "示例输出",
            "constraints": "约束条件",
            "function_signature": "函数签名（如有）"
        }}
        
        仅返回JSON格式，不要有其他文本。
        """
        
        return prompt

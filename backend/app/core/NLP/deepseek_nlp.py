"""
DeepSeek NLP模块，用于解析用户意图
"""
import re
import json
import requests
from typing import Dict, Any, List, Optional

from ...config import active_config


class QueryParser:
    """
    查询解析器，用于解析用户的自然语言查询
    """
    
    # 难度级别映射
    DIFFICULTY_MAP = {
        "简单": "Easy",
        "容易": "Easy",
        "入门": "Easy",
        "基础": "Easy",
        "easy": "Easy",
        "中等": "Medium",
        "medium": "Medium",
        "困难": "Hard",
        "难": "Hard",
        "hard": "Hard",
    }
    
    # 数据结构映射
    DATA_STRUCTURE_MAP = {
        "数组": "Array",
        "链表": "LinkedList",
        "单链表": "LinkedList",
        "双链表": "DoublyLinkedList",
        "栈": "Stack",
        "队列": "Queue",
        "哈希表": "HashMap",
        "字典": "HashMap",
        "集合": "HashSet",
        "树": "Tree",
        "二叉树": "BinaryTree",
        "二叉搜索树": "BST",
        "堆": "Heap",
        "优先队列": "PriorityQueue",
        "图": "Graph",
        "字符串": "String",
    }
    
    # 算法技术映射
    TECHNIQUE_MAP = {
        "递归": "Recursion",
        "迭代": "Iteration",
        "动态规划": "DynamicProgramming",
        "贪心": "Greedy",
        "分治": "DivideAndConquer",
        "回溯": "Backtracking",
        "深度优先搜索": "DFS",
        "广度优先搜索": "BFS",
        "二分查找": "BinarySearch",
        "排序": "Sorting",
    }
    
    def __init__(self):
        """初始化查询解析器"""
        self.api_key = active_config.DEEPSEEK_API_KEY
        self.api_url = f"{active_config.DEEPSEEK_API_URL}/chat/completions"
    
    def parse_with_rules(self, query: str) -> Dict[str, Any]:
        """
        使用规则引擎解析查询
        
        Args:
            query: 用户查询文本
            
        Returns:
            Dict[str, Any]: 解析结果
        """
        result = {
            "difficulty": None,
            "data_structure": None,
            "technique": None,
            "original_query": query,
        }
        
        # 解析难度
        for key, value in self.DIFFICULTY_MAP.items():
            if key in query.lower():
                result["difficulty"] = value
                break
        
        # 解析数据结构
        for key, value in self.DATA_STRUCTURE_MAP.items():
            if key in query:
                result["data_structure"] = value
                break
        
        # 解析算法技术
        for key, value in self.TECHNIQUE_MAP.items():
            if key in query:
                result["technique"] = value
                break
        
        return result
    
    def parse_with_deepseek(self, query: str) -> Dict[str, Any]:
        """
        使用DeepSeek API解析查询意图
        
        Args:
            query: 用户查询文本
            
        Returns:
            Dict[str, Any]: 解析结果
        """
        if not self.api_key:
            # 如果没有API密钥，回退到规则引擎
            return self.parse_with_rules(query)
        
        # 构建提示
        prompt = f"""
        请分析以下编程问题查询，提取关键信息：
        
        查询："{query}"
        
        请以JSON格式返回以下字段：
        1. difficulty: 难度级别 (Easy/Medium/Hard)，如果未指定则为null
        2. data_structure: 主要涉及的数据结构，如Array、LinkedList、Tree等，如果未指定则为null
        3. technique: 主要涉及的算法技术，如Recursion、DynamicProgramming等，如果未指定则为null
        4. keywords: 提取的关键词列表
        5. intent: 用户意图分类 (Practice/Learn/Review)
        
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
                    "temperature": 0.1,
                    "max_tokens": 500
                },
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                
                # 提取JSON
                try:
                    parsed_result = json.loads(content)
                    # 添加原始查询
                    parsed_result["original_query"] = query
                    return parsed_result
                except json.JSONDecodeError:
                    # 如果解析失败，回退到规则引擎
                    return self.parse_with_rules(query)
            
        except Exception as e:
            print(f"DeepSeek API调用失败: {str(e)}")
        
        # 如果API调用失败，回退到规则引擎
        return self.parse_with_rules(query)
    
    def parse(self, query: str) -> Dict[str, Any]:
        """
        解析用户查询，结合规则引擎和DeepSeek API
        
        Args:
            query: 用户查询文本
            
        Returns:
            Dict[str, Any]: 解析结果
        """
        # 先使用规则引擎
        rule_result = self.parse_with_rules(query)
        
        # 如果规则引擎无法提取足够信息，使用DeepSeek API
        if not any([rule_result["difficulty"], rule_result["data_structure"], rule_result["technique"]]):
            return self.parse_with_deepseek(query)
        
        return rule_result

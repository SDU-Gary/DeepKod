"""
练习相关API路由
"""
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..core.matching.hybrid_search import HybridSearchEngine
from ..core.NLP.deepseek_nlp import QueryParser
from ..core.generation.deepseek_generation import QuestionGenerator
from ..models.question import Question, Solution
from ..database import get_db

router = APIRouter(prefix="/api/v1/practice", tags=["practice"])

# 初始化组件
search_engine = HybridSearchEngine()
query_parser = QueryParser()
question_generator = QuestionGenerator()


@router.post("/search")
async def search_questions(
    query: str,
    difficulty: Optional[str] = None,
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    搜索题目
    
    Args:
        query: 搜索查询
        difficulty: 难度级别
        limit: 返回结果数量
        db: 数据库会话
        
    Returns:
        Dict[str, Any]: 搜索结果
    """
    # 解析查询意图
    parsed_intent = query_parser.parse(query)
    
    # 如果指定了难度，覆盖解析结果
    if difficulty:
        parsed_intent["difficulty"] = difficulty
    
    # 构建过滤条件
    filters = {
        "difficulty": parsed_intent.get("difficulty"),
        "data_structure": parsed_intent.get("data_structure"),
        "technique": parsed_intent.get("technique")
    }
    
    # 执行混合检索
    search_results = search_engine.hybrid_search(query, filters, top_k=limit)
    
    # 如果没有找到结果，尝试动态生成
    if not search_results:
        # 生成题目
        generated_question = question_generator.generate_question(query, parsed_intent)
        
        if generated_question:
            # 生成解决方案
            generated_solution = question_generator.generate_solution(generated_question)
            
            # 保存到数据库
            if generated_solution:
                # TODO: 保存生成的题目和解决方案到数据库
                # 这里简化处理，直接返回生成结果
                search_results = [
                    {
                        "id": generated_question.get("id", "gen_001"),
                        "title": generated_question.get("title", ""),
                        "difficulty": generated_question.get("difficulty", "Medium"),
                        "description": generated_question.get("description", ""),
                        "tags": generated_question.get("tags", []),
                        "is_generated": True,
                        "score": 1.0
                    }
                ]
    
    return {
        "query": query,
        "parsed_intent": parsed_intent,
        "results": search_results,
        "total": len(search_results)
    }


@router.get("/questions/{question_id}")
async def get_question(
    question_id: str,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    获取题目详情
    
    Args:
        question_id: 题目ID
        db: 数据库会话
        
    Returns:
        Dict[str, Any]: 题目详情
    """
    # 查询题目
    question = db.query(Question).filter(Question.id == question_id).first()
    
    if not question:
        raise HTTPException(status_code=404, detail="题目不存在")
    
    return question.to_dict()


@router.get("/questions/{question_id}/solutions")
async def get_solutions(
    question_id: str,
    language: Optional[str] = None,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    获取题目解决方案
    
    Args:
        question_id: 题目ID
        language: 编程语言
        db: 数据库会话
        
    Returns:
        Dict[str, Any]: 解决方案列表
    """
    # 构建查询
    query = db.query(Solution).filter(Solution.question_id == question_id)
    
    # 如果指定了语言，添加过滤条件
    if language:
        query = query.filter(Solution.language == language)
    
    # 执行查询
    solutions = query.all()
    
    if not solutions:
        # 如果没有找到解决方案，尝试动态生成
        # 先获取题目
        question = db.query(Question).filter(Question.id == question_id).first()
        
        if question:
            # 生成解决方案
            generated_solution = question_generator.generate_solution(question.to_dict())
            
            if generated_solution:
                # TODO: 保存生成的解决方案到数据库
                # 这里简化处理，直接返回生成结果
                return {
                    "question_id": question_id,
                    "solutions": [generated_solution]
                }
    
    return {
        "question_id": question_id,
        "solutions": [solution.to_dict() for solution in solutions]
    }

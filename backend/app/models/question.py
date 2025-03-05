"""
题目数据模型
"""
from datetime import datetime
from typing import List, Dict, Any, Optional
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Question(Base):
    """题目模型"""
    __tablename__ = "questions"
    
    id = Column(String(36), primary_key=True)
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=False)
    difficulty = Column(String(20), nullable=False, index=True)
    acceptance_rate = Column(Integer, default=0)
    function_signature = Column(String(255))
    constraints = Column(Text)
    is_generated = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联
    tags = relationship("QuestionTag", back_populates="question")
    examples = relationship("QuestionExample", back_populates="question")
    solutions = relationship("Solution", back_populates="question")
    
    def to_dict(self) -> Dict[str, Any]:
        """
        转换为字典
        
        Returns:
            Dict[str, Any]: 字典表示
        """
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "difficulty": self.difficulty,
            "acceptance_rate": self.acceptance_rate,
            "function_signature": self.function_signature,
            "constraints": self.constraints,
            "is_generated": self.is_generated,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "tags": [tag.tag for tag in self.tags],
            "examples": [example.to_dict() for example in self.examples]
        }


class QuestionTag(Base):
    """题目标签模型"""
    __tablename__ = "question_tags"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    question_id = Column(String(36), ForeignKey("questions.id"), nullable=False)
    tag = Column(String(50), nullable=False, index=True)
    
    # 关联
    question = relationship("Question", back_populates="tags")


class QuestionExample(Base):
    """题目示例模型"""
    __tablename__ = "question_examples"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    question_id = Column(String(36), ForeignKey("questions.id"), nullable=False)
    input_example = Column(Text, nullable=False)
    output_example = Column(Text, nullable=False)
    explanation = Column(Text)
    
    # 关联
    question = relationship("Question", back_populates="examples")
    
    def to_dict(self) -> Dict[str, Any]:
        """
        转换为字典
        
        Returns:
            Dict[str, Any]: 字典表示
        """
        return {
            "id": self.id,
            "input": self.input_example,
            "output": self.output_example,
            "explanation": self.explanation
        }


class Solution(Base):
    """解决方案模型"""
    __tablename__ = "solutions"
    
    id = Column(String(36), primary_key=True)
    question_id = Column(String(36), ForeignKey("questions.id"), nullable=False)
    language = Column(String(20), nullable=False, index=True)
    code = Column(Text, nullable=False)
    explanation = Column(Text)
    time_complexity = Column(String(50))
    space_complexity = Column(String(50))
    is_generated = Column(Boolean, default=False)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联
    question = relationship("Question", back_populates="solutions")
    test_cases = relationship("TestCase", back_populates="solution")
    
    def to_dict(self) -> Dict[str, Any]:
        """
        转换为字典
        
        Returns:
            Dict[str, Any]: 字典表示
        """
        return {
            "id": self.id,
            "question_id": self.question_id,
            "language": self.language,
            "code": self.code,
            "explanation": self.explanation,
            "time_complexity": self.time_complexity,
            "space_complexity": self.space_complexity,
            "is_generated": self.is_generated,
            "is_verified": self.is_verified,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "test_cases": [test_case.to_dict() for test_case in self.test_cases]
        }


class TestCase(Base):
    """测试用例模型"""
    __tablename__ = "test_cases"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    solution_id = Column(String(36), ForeignKey("solutions.id"), nullable=False)
    input_data = Column(Text, nullable=False)
    expected_output = Column(Text, nullable=False)
    is_hidden = Column(Boolean, default=False)
    
    # 关联
    solution = relationship("Solution", back_populates="test_cases")
    
    def to_dict(self) -> Dict[str, Any]:
        """
        转换为字典
        
        Returns:
            Dict[str, Any]: 字典表示
        """
        return {
            "id": self.id,
            "input": self.input_data,
            "output": self.expected_output,
            "is_hidden": self.is_hidden
        }

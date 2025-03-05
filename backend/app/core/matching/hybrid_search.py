"""
混合检索算法模块，实现语义检索与精确匹配的结合
"""
import faiss
import numpy as np
from typing import List, Dict, Any
from elasticsearch import Elasticsearch
from sentence_transformers import SentenceTransformer

from ...config import active_config


class HybridSearchEngine:
    """
    混合检索引擎，结合向量检索和精确匹配
    """
    
    def __init__(self):
        """初始化混合检索引擎"""
        # 加载向量模型
        self.model = SentenceTransformer(active_config.EMBEDDING_MODEL)
        
        # 加载FAISS索引
        self.index = faiss.read_index(active_config.FAISS_INDEX_PATH)
        
        # 初始化Elasticsearch客户端
        self.es = Elasticsearch(
            hosts=[f"{active_config.ELASTICSEARCH_HOST}:{active_config.ELASTICSEARCH_PORT}"]
        )
        
        # 加载元数据映射
        self.metadata_map = self._load_metadata_map()
    
    def _load_metadata_map(self) -> Dict[int, Dict[str, Any]]:
        """
        加载元数据映射，将索引ID映射到题目元数据
        
        Returns:
            Dict[int, Dict[str, Any]]: 元数据映射字典
        """
        # 实际项目中应从数据库或文件加载
        # 这里使用示例数据
        return {}  # 实际实现时需要加载真实数据
    
    def semantic_search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        执行语义检索
        
        Args:
            query: 查询文本
            top_k: 返回结果数量
            
        Returns:
            List[Dict[str, Any]]: 检索结果列表
        """
        # 编码查询文本
        query_vector = self.model.encode(query)
        
        # 归一化向量
        faiss.normalize_L2(query_vector.reshape(1, -1))
        
        # 执行检索
        distances, indices = self.index.search(query_vector.reshape(1, -1), top_k)
        
        # 获取结果
        results = []
        for i, idx in enumerate(indices[0]):
            if idx != -1:  # 有效索引
                item = self.metadata_map.get(int(idx), {})
                if item:
                    item["score"] = float(distances[0][i])
                    results.append(item)
        
        return results
    
    def exact_search(self, filters: Dict[str, Any], size: int = 5) -> List[Dict[str, Any]]:
        """
        执行精确匹配检索
        
        Args:
            filters: 过滤条件
            size: 返回结果数量
            
        Returns:
            List[Dict[str, Any]]: 检索结果列表
        """
        # 构建查询
        must_clauses = []
        for key, value in filters.items():
            if value:
                must_clauses.append({"term": {key: value}})
        
        # 执行查询
        if must_clauses:
            query = {
                "query": {
                    "bool": {
                        "must": must_clauses
                    }
                }
            }
            response = self.es.search(index="kodcode", body=query, size=size)
            
            # 处理结果
            results = []
            for hit in response["hits"]["hits"]:
                item = hit["_source"]
                item["score"] = hit["_score"]
                results.append(item)
            
            return results
        
        return []
    
    def hybrid_search(self, query: str, filters: Dict[str, Any] = None, top_k: int = 10) -> List[Dict[str, Any]]:
        """
        执行混合检索
        
        Args:
            query: 查询文本
            filters: 过滤条件
            top_k: 返回结果数量
            
        Returns:
            List[Dict[str, Any]]: 混合排序后的检索结果
        """
        # 默认过滤条件
        if filters is None:
            filters = {}
        
        # 执行语义检索
        semantic_results = self.semantic_search(query, top_k=top_k*2)
        
        # 执行精确匹配
        exact_results = self.exact_search(filters, size=top_k)
        
        # 混合排序
        return self._hybrid_rerank(semantic_results, exact_results, top_k)
    
    def _hybrid_rerank(
        self, 
        semantic_results: List[Dict[str, Any]], 
        exact_results: List[Dict[str, Any]], 
        top_k: int
    ) -> List[Dict[str, Any]]:
        """
        混合排序算法
        
        Args:
            semantic_results: 语义检索结果
            exact_results: 精确匹配结果
            top_k: 返回结果数量
            
        Returns:
            List[Dict[str, Any]]: 混合排序后的结果
        """
        # 计算综合得分
        score_map = {}
        id_to_item = {}
        
        # 语义结果加权
        for i, res in enumerate(semantic_results):
            item_id = res["id"]
            # 语义得分权重为0.7
            score = 0.7 * (1 - i/len(semantic_results))
            score_map[item_id] = score_map.get(item_id, 0) + score
            id_to_item[item_id] = res
        
        # 精确匹配加权
        for res in exact_results:
            item_id = res["id"]
            # 精确匹配权重为0.3
            score_map[item_id] = score_map.get(item_id, 0) + 0.3
            id_to_item[item_id] = res
        
        # 按总分排序
        sorted_ids = sorted(score_map.items(), key=lambda x: x[1], reverse=True)
        
        # 返回排序结果
        results = []
        for item_id, score in sorted_ids[:top_k]:
            item = id_to_item[item_id]
            item["hybrid_score"] = score
            results.append(item)
        
        return results

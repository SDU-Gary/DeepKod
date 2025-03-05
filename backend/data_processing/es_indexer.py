"""
Elasticsearch索引构建脚本
"""
import os
import json
import argparse
import logging
from tqdm import tqdm
from elasticsearch import Elasticsearch, helpers

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def connect_elasticsearch(host="localhost", port=9200):
    """
    连接Elasticsearch
    
    Args:
        host: 主机地址
        port: 端口号
        
    Returns:
        Elasticsearch: Elasticsearch客户端
    """
    try:
        logger.info(f"正在连接Elasticsearch: {host}:{port}")
        es = Elasticsearch([{'host': host, 'port': port}])
        if es.ping():
            logger.info("Elasticsearch连接成功")
            return es
        else:
            logger.error("Elasticsearch连接失败")
            return None
    except Exception as e:
        logger.error(f"Elasticsearch连接异常: {str(e)}")
        return None


def create_index(es, index_name="kodcode"):
    """
    创建Elasticsearch索引
    
    Args:
        es: Elasticsearch客户端
        index_name: 索引名称
        
    Returns:
        bool: 是否创建成功
    """
    try:
        # 检查索引是否存在
        if es.indices.exists(index=index_name):
            logger.info(f"索引 {index_name} 已存在，正在删除...")
            es.indices.delete(index=index_name)
        
        # 索引映射
        mappings = {
            "mappings": {
                "properties": {
                    "id": {"type": "keyword"},
                    "title": {
                        "type": "text",
                        "analyzer": "standard",
                        "fields": {
                            "keyword": {"type": "keyword"}
                        }
                    },
                    "description": {"type": "text", "analyzer": "standard"},
                    "difficulty": {"type": "keyword"},
                    "tags": {"type": "keyword"},
                    "data_structure": {"type": "keyword"},
                    "algorithm": {"type": "keyword"},
                    "created_at": {"type": "date"},
                    "updated_at": {"type": "date"}
                }
            },
            "settings": {
                "number_of_shards": 1,
                "number_of_replicas": 0
            }
        }
        
        # 创建索引
        logger.info(f"正在创建索引: {index_name}")
        es.indices.create(index=index_name, body=mappings)
        logger.info(f"索引 {index_name} 创建成功")
        return True
    except Exception as e:
        logger.error(f"创建索引失败: {str(e)}")
        return False


def load_data(file_path):
    """
    加载数据
    
    Args:
        file_path: 数据文件路径
        
    Returns:
        list: 数据列表
    """
    try:
        logger.info(f"正在加载数据: {file_path}")
        with open(file_path, 'r') as f:
            data = json.load(f)
        logger.info(f"数据加载成功，共{len(data)}条记录")
        return data
    except Exception as e:
        logger.error(f"数据加载失败: {str(e)}")
        return []


def prepare_documents(data):
    """
    准备文档
    
    Args:
        data: 原始数据
        
    Returns:
        list: 处理后的文档列表
    """
    logger.info("正在准备文档...")
    documents = []
    
    for item in data:
        # 提取标签
        tags = item.get("tags", [])
        
        # 提取数据结构和算法
        data_structure = None
        algorithm = None
        
        for tag in tags:
            if tag in ["Array", "LinkedList", "Stack", "Queue", "HashMap", "Tree", "Graph", "String"]:
                data_structure = tag
            elif tag in ["Recursion", "DynamicProgramming", "Greedy", "DFS", "BFS", "Sorting"]:
                algorithm = tag
        
        # 构建文档
        doc = {
            "id": item.get("id", ""),
            "title": item.get("title", ""),
            "description": item.get("description", ""),
            "difficulty": item.get("difficulty", "Medium"),
            "tags": tags,
            "data_structure": data_structure,
            "algorithm": algorithm
        }
        
        documents.append(doc)
    
    logger.info(f"文档准备完成，共{len(documents)}条记录")
    return documents


def index_documents(es, documents, index_name="kodcode", batch_size=1000):
    """
    索引文档
    
    Args:
        es: Elasticsearch客户端
        documents: 文档列表
        index_name: 索引名称
        batch_size: 批处理大小
        
    Returns:
        int: 成功索引的文档数量
    """
    try:
        logger.info(f"正在索引文档到 {index_name}...")
        
        # 生成批量索引操作
        actions = []
        for doc in documents:
            action = {
                "_index": index_name,
                "_id": doc["id"],
                "_source": doc
            }
            actions.append(action)
        
        # 批量索引
        success, failed = 0, 0
        for i in tqdm(range(0, len(actions), batch_size)):
            batch = actions[i:i+batch_size]
            success_count, failed_items = helpers.bulk(es, batch, stats_only=True)
            success += success_count
            failed += len(batch) - success_count
        
        logger.info(f"文档索引完成，成功: {success}，失败: {failed}")
        return success
    except Exception as e:
        logger.error(f"索引文档失败: {str(e)}")
        return 0


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="KodCode数据集Elasticsearch索引构建")
    parser.add_argument("--data", type=str, default="data/metadata.json", help="数据文件路径")
    parser.add_argument("--host", type=str, default="localhost", help="Elasticsearch主机地址")
    parser.add_argument("--port", type=int, default=9200, help="Elasticsearch端口号")
    parser.add_argument("--index", type=str, default="kodcode", help="索引名称")
    parser.add_argument("--batch-size", type=int, default=1000, help="批处理大小")
    args = parser.parse_args()
    
    try:
        # 连接Elasticsearch
        es = connect_elasticsearch(args.host, args.port)
        if not es:
            return
        
        # 创建索引
        if not create_index(es, args.index):
            return
        
        # 加载数据
        data = load_data(args.data)
        if not data:
            return
        
        # 准备文档
        documents = prepare_documents(data)
        
        # 索引文档
        success_count = index_documents(es, documents, args.index, args.batch_size)
        
        logger.info(f"索引构建完成，成功索引{success_count}条文档")
        
    except Exception as e:
        logger.error(f"处理失败: {str(e)}")
        raise


if __name__ == "__main__":
    main()

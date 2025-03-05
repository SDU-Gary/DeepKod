"""
向量化处理脚本，用于生成FAISS向量数据
"""
import os
import json
import numpy as np
import pandas as pd
from tqdm import tqdm
import faiss
from sentence_transformers import SentenceTransformer
from datasets import load_dataset
import argparse
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_kodcode_data(sample_size=None):
    """
    加载KodCode数据集
    
    Args:
        sample_size: 样本大小，如果为None则加载全部数据
        
    Returns:
        pd.DataFrame: 加载的数据
    """
    try:
        logger.info("正在加载KodCode数据集...")
        ds = load_dataset("KodCode/KodCode-V1")
        
        # 转换为DataFrame
        df = pd.DataFrame(ds["train"])
        
        # 如果指定了样本大小，随机抽样
        if sample_size and sample_size < len(df):
            df = df.sample(sample_size, random_state=42)
        
        logger.info(f"成功加载数据集，共{len(df)}条记录")
        return df
    except Exception as e:
        logger.error(f"加载数据集失败: {str(e)}")
        raise


def preprocess_data(df):
    """
    预处理数据
    
    Args:
        df: 原始数据DataFrame
        
    Returns:
        list: 处理后的数据列表
    """
    logger.info("正在预处理数据...")
    processed = []
    
    for _, row in tqdm(df.iterrows(), total=len(df)):
        # 提取标签
        tags = []
        if "data_structure" in row and row["data_structure"]:
            tags.append(row["data_structure"])
        if "algorithm" in row and row["algorithm"]:
            tags.append(row["algorithm"])
        
        # 合并文本用于向量化
        search_text = " ".join([
            row.get("title", ""),
            row.get("description", ""),
            " ".join(tags)
        ])
        
        # 提取难度
        difficulty = "Medium"
        if "difficulty" in row:
            if row["difficulty"] in ["Easy", "Medium", "Hard"]:
                difficulty = row["difficulty"]
        
        # 构建处理后的记录
        processed.append({
            "id": row.get("id", str(len(processed))),
            "title": row.get("title", ""),
            "description": row.get("description", ""),
            "difficulty": difficulty,
            "tags": tags,
            "text": search_text
        })
    
    logger.info(f"数据预处理完成，共{len(processed)}条记录")
    return processed


def generate_embeddings(data, model_name="sentence-transformers/all-mpnet-base-v2", batch_size=32):
    """
    生成文本嵌入向量
    
    Args:
        data: 预处理后的数据
        model_name: 模型名称
        batch_size: 批处理大小
        
    Returns:
        np.ndarray: 嵌入向量
    """
    logger.info(f"正在加载模型: {model_name}")
    model = SentenceTransformer(model_name)
    
    logger.info("正在生成嵌入向量...")
    texts = [item["text"] for item in data]
    
    embeddings = model.encode(
        texts,
        batch_size=batch_size,
        show_progress_bar=True,
        convert_to_tensor=False
    )
    
    logger.info(f"嵌入向量生成完成，形状: {embeddings.shape}")
    return embeddings


def build_faiss_index(embeddings, index_type="IVF100,Flat"):
    """
    构建FAISS索引
    
    Args:
        embeddings: 嵌入向量
        index_type: 索引类型
        
    Returns:
        faiss.Index: FAISS索引
    """
    logger.info(f"正在构建FAISS索引，类型: {index_type}")
    
    # 获取维度
    dim = embeddings.shape[1]
    
    # 创建索引
    index = faiss.index_factory(dim, index_type, faiss.METRIC_INNER_PRODUCT)
    
    # 归一化向量
    faiss.normalize_L2(embeddings)
    
    # 训练索引（对于IVF类型的索引需要训练）
    if "IVF" in index_type:
        logger.info("正在训练索引...")
        index.train(embeddings)
    
    # 添加向量
    logger.info("正在添加向量到索引...")
    index.add(embeddings)
    
    logger.info(f"索引构建完成，包含{index.ntotal}个向量")
    return index


def save_data(data, embeddings, index, output_dir="data"):
    """
    保存数据、嵌入向量和索引
    
    Args:
        data: 预处理后的数据
        embeddings: 嵌入向量
        index: FAISS索引
        output_dir: 输出目录
    """
    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)
    
    # 保存元数据
    logger.info(f"正在保存元数据到 {output_dir}/metadata.json")
    with open(os.path.join(output_dir, "metadata.json"), "w") as f:
        json.dump(data, f)
    
    # 保存嵌入向量
    logger.info(f"正在保存嵌入向量到 {output_dir}/embeddings.npy")
    np.save(os.path.join(output_dir, "embeddings.npy"), embeddings)
    
    # 保存索引
    logger.info(f"正在保存FAISS索引到 {output_dir}/kodcode_index.faiss")
    faiss.write_index(index, os.path.join(output_dir, "kodcode_index.faiss"))
    
    logger.info("所有数据保存完成")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="KodCode数据集向量化处理")
    parser.add_argument("--sample", type=int, default=None, help="样本大小")
    parser.add_argument("--model", type=str, default="sentence-transformers/all-mpnet-base-v2", help="向量模型")
    parser.add_argument("--batch-size", type=int, default=32, help="批处理大小")
    parser.add_argument("--output-dir", type=str, default="data", help="输出目录")
    args = parser.parse_args()
    
    try:
        # 加载数据
        df = load_kodcode_data(args.sample)
        
        # 预处理数据
        processed_data = preprocess_data(df)
        
        # 生成嵌入向量
        embeddings = generate_embeddings(processed_data, args.model, args.batch_size)
        
        # 构建FAISS索引
        index = build_faiss_index(embeddings)
        
        # 保存数据
        save_data(processed_data, embeddings, index, args.output_dir)
        
        logger.info("向量化处理完成")
        
    except Exception as e:
        logger.error(f"处理失败: {str(e)}")
        raise


if __name__ == "__main__":
    main()

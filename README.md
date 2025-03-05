# DeepKod - 大学生一站式代码练习平台

![版本](https://img.shields.io/badge/版本-0.1.0-blue)
![Python](https://img.shields.io/badge/Python-3.9+-green)
![FastAPI](https://img.shields.io/badge/FastAPI-latest-brightgreen)
![React](https://img.shields.io/badge/React-latest-blue)

DeepKod是一个面向大学生的一站式代码练习平台，结合KodCode数据集与DeepSeek API，为用户提供智能化的编程题目推荐和解答服务。用户只需输入练习方向的关键词（如"反转链表"或"我想练习关于树结构操作的题目"），即可获得精准匹配的编程题目及详细题解。

## 📚 项目背景

现有代码练习平台存在题目陈旧、缺乏个性化推荐、无法覆盖长尾需求等痛点。DeepKod通过结合KodCode的权威数据与DeepSeek的生成能力，打造智能化的代码训练平台，解决这些问题。

## ✨ 核心功能

### 1. 智能题目推荐

- **自然语言查询**：支持口语化描述（如"教我写快排"）
- **多条件过滤**：难度/数据结构/算法类型三维筛选
- **语义扩展**：自动识别同义词（"二叉树" → "binary tree"）

### 2. 动态题目生成

- 当检索结果不足时，自动生成高质量编程题目
- 通过DeepSeek生成 → 沙箱验证 → 人工审核的流程保障质量
- 自动标注生成标签

### 3. 代码验证与评估

- 安全的Docker沙箱环境执行用户代码
- 自动化测试用例验证
- 性能分析与优化建议

## 🔧 技术架构

### 后端技术栈

- **Web框架**：FastAPI
- **数据库**：MySQL + Redis
- **搜索引擎**：Elasticsearch + FAISS向量检索
- **AI能力**：DeepSeek API
- **容器化**：Docker + Kubernetes

### 前端技术栈

- **框架**：React
- **UI组件**：自定义组件
- **代码编辑器**：Monaco Editor

## 🚀 快速开始

### 环境要求

- Python 3.9+
- Node.js 14+
- Docker
- Elasticsearch 7.x+

### 安装步骤

1. 克隆仓库

```bash
git clone https://github.com/yourusername/DeepKod.git
cd DeepKod
```

安装后端依赖

```bash
CopyInsert in Terminal
pip install -r requirements.txt
配置环境变量
```

```bash
CopyInsert
cp .env.example .env
# 编辑.env文件，填入必要的配置信息，如DeepSeek API密钥等
```

数据准备

```bash
cd backend/data_processing
python vectorize.py  # 生成向量数据
python es_indexer.py  # 构建Elasticsearch索引
```

启动后端服务

```bash
cd backend
uvicorn app:app --reload
```

安装并启动前端服务

```bash
cd frontend
npm install
npm start
```

## 📁 项目结构

```bash
.
├── backend
│   ├── app
│   │   ├── core              # 核心业务逻辑
│   │   │   ├── matching      # 智能匹配引擎
│   │   │   ├── NLP           # NLP意图解析
│   │   │   ├── generation    # 动态生成系统
│   │   │   └── validation    # 沙箱验证逻辑
│   │   ├── models            # 数据模型
│   │   ├── routes            # API端点
│   │   └── config.py         # 配置管理
│   ├── data_processing       # 数据处理脚本
│   │   ├── vectorize.py      # 向量化处理
│   │   └── es_indexer.py     # ES索引构建
├── frontend
│   ├── public
│   └── src
│       ├── components         # 可复用组件
│       │   ├── Editor         # 代码编辑器
│       │   └── QuestionCard   # 题目展示卡片
│       └── pages
│           ├── Practice       # 练习页面
│           └── History        # 练习历史
├── infrastructure
│   ├── docker
│   │   ├── api.Dockerfile     # API服务镜像
│   │   └── sandbox.Dockerfile # 沙箱环境镜像
│   └── k8s                    # K8s部署配置
└── docs
    ├── api-spec               # OpenAPI文档
    └── architecture           # 架构图资源
```

📊 数据来源
本项目使用KodCode数据集，该数据集包含447K条高质量编程问题-解决方案-测试三元组，涵盖从基础编程到高级算法的多难度任务。

KodCode数据集加载方式

```python
CopyInsert
from datasets import load_dataset

# 登录后使用
ds = load_dataset("KodCode/KodCode-V1")
```

## 🔄 工作流程

用户输入自然语言查询（如"反转链表"）
DeepSeek NLP模块解析用户意图
混合检索引擎在KodCode题库中匹配最相关题目
如果匹配结果不足，动态生成新题目
返回题目、测试用例和题解
用户提交代码，在安全沙箱中验证

## 🤝 贡献指南

欢迎贡献代码、报告问题或提出新功能建议！请遵循以下步骤：

# 项目文件结构

```bash
.
├── backend
│   ├── app
│   │   ├── core              # 核心业务逻辑
│   │   │   ├── matching      # 智能匹配引擎
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

以下是项目文件结构的详细说明，分模块解释每个目录的作用：

## **1. Backend（后端服务）**

```bash
backend
├── app
│   ├── core              # 核心业务逻辑
│   │   ├── matching      # 智能匹配引擎实现
│   │   │   └── hybrid_search.py  # 混合检索算法
│   │   ├── NLP           # NLP意图解析
│   │   │   └── deepseek_nlp.py # 使用DeepSeek进行NLP解析
│   │   ├── generation    # 动态题目生成系统
│   │   │   └── deepseek_generation.py # 使用DeepSeek进行题目生成
│   │   └── validation    # 沙箱验证逻辑
│   │       └── docker_sandbox.py  # 安全执行环境
│   ├── models            # 数据模型定义
│   │   └── question.py   # 题目数据ORM模型
│   ├── routes            # API端点定义
│   │   └── practice.py   # 练习相关API路由
│   └── config.py         # 配置管理（数据库连接等）
├── data_processing       # 数据预处理脚本
│   ├── vectorize.py      # 生成FAISS向量数据
│   └── es_indexer.py     # 构建Elasticsearch索引
```

**核心作用**：

- `core/` 实现核心业务逻辑的Python模块
- `models/` 定义数据库表结构和DTO对象
- `routes/` 处理HTTP请求与响应（REST API入口）
- `data_processing/` 运行一次性的数据处理任务

---

## **2. Frontend（前端应用）**

```bash
frontend
├── public                # 静态资源
│   └── favicon.ico       # 网站图标
└── src
    ├── components        # 可复用UI组件
    │   ├── Editor        # 代码编辑器组件
    │   │   └── MonacoWrapper.tsx  # 集成Monaco编辑器
    │   └── QuestionCard  # 题目展示卡片组件
    │       └── index.tsx # 题目详情布局
    └── pages             # 页面级组件
        ├── Practice      # 练习主页面
        │   └── index.tsx # 题目搜索与展示逻辑
        └── History       # 练习历史页面
            └── Chart.tsx # 练习数据可视化
```

**核心作用**：

- `components/` 封装可复用的UI组件
- `pages/` 实现具体功能页面（路由对应页面）
- `public/` 存放不需要编译的静态资源

---

## **3. Infrastructure（基础设施）**

```bash
infrastructure
├── docker
│   ├── api.Dockerfile     # API服务容器构建文件
│   └── sandbox.Dockerfile # 沙箱环境镜像配置
└── k8s                    # Kubernetes部署配置
    ├── deployment.yaml    # 服务部署定义
    └── service.yaml       # 网络服务暴露配置
```

**核心作用**：

- `docker/` 定义各服务的容器化构建流程
- `k8s/` 声明生产环境的集群部署方式

---

## **4. Docs（文档）**

```bash
docs
├── api-spec               # API文档
│   └── openapi.yaml      # OpenAPI 3.0规范文件
└── architecture           # 架构设计资源
    └── system-diagram.png # 系统架构图
```

**核心作用**：

- `api-spec/` 维护API接口的机器可读文档
- `architecture/` 存放系统设计图等可视化资源

---

## **典型开发工作流程**

```bash
1. **数据准备**：运行 `data_processing/vectorize.py` 生成题目向量
2. **后端开发**：在 `app/core/` 添加新业务逻辑模块
3. **前端联调**：在 `pages/Practice/` 开发新页面，调用后端API
4. **部署验证**：通过 `infrastructure/k8s/` 的配置更新生产环境
```

该结构遵循"关注点分离"原则，实现了：
• 业务逻辑与基础设施解耦
• 前后端代码物理隔离
• 文档与代码同步维护
• 一次性的数据处理脚本独立存放

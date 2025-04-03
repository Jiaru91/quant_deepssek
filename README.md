# 量化分析系统

一个基于Python的智能量化分析系统，集成新闻分析、财报分析和量化预测功能，为投资决策提供全方位的数据支持。

## 功能特点

### 1. 新闻智能分析
- 自动抓取和分析相关新闻
- 提供长期发展战略分析
- 评估市场竞争力和行业地位
- 跟踪技术创新和研发进展
- 分析财务状况和业绩表现
- 识别潜在风险因素

### 2. 财报深度分析
- 核心财务指标分析
- 收入和利润增长趋势
- 毛利率和净利率变化
- 现金流状况评估
- 资产负债结构分析
- 研发投入跟踪
- 业务板块表现分析

### 3. 量化预测系统
- 整合新闻情感分析
- 财务指标分析
- 技术指标计算
- 综合预测模型

## 技术架构

### 后端技术栈
- Python 3.9
- FastAPI
- OpenAI/DeepSeek API
- Pandas & NumPy
- SQLAlchemy
- scikit-learn

### 数据采集
- Yahoo Finance API
- 财报数据接口

### 分析引擎
- 深度学习模型
- 自然语言处理
- 技术指标分析
- 量化预测算法

## 快速开始

### 环境要求
- Python 3.9+
- Docker (可选)
- MySQL

### 安装步骤

1. 克隆项目并安装依赖
```bash
git clone <repository_url>
cd quant
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

2. 配置环境变量
```bash
cp .env.example .env
# 编辑 .env 文件，配置必要的环境变量
```


### 启动服务

#### 后端服务
##### 使用Python直接启动
```bash
uvicorn app.main:app --reload
```

##### 使用Docker启动
```bash
docker-compose up -d
```

#### 前端服务
##### 使用Python直接启动
```bash
streamlit run app/FrontPoint/app.py
```

##### 使用Docker启动
```bash
docker-compose up -d frontend
```

## 项目结构
```
.
├── app/                    # 应用主目录
│   ├── api/               # API接口
│   ├── core/              # 核心配置
│   ├── crawlers/          # 数据爬虫
│   ├── models/            # 数据模型
│   ├── services/          # 业务服务
│   └── utils/             # 工具函数
├── config/                # 配置文件
├── scripts/               # 管理脚本
├── tests/                 # 测试用例
└── logs/                  # 日志文件
```

## 开发指南

### 代码规范
- 遵循PEP 8规范
- 使用类型注解
- 编写单元测试
- 保持代码文档更新

### 提交规范
- feat: 新功能
- fix: 修复问题
- docs: 文档变更
- style: 代码格式
- refactor: 代码重构
- test: 测试相关
- chore: 其他修改



## 许可证

MIT License
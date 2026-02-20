# SlideNode

SlideNode 是一个 pipeline 优先的学习应用，将 PDF 文档转化为结构化的教学幻灯片（章节 → 小节 → 带引用的要点）。

## 功能特性

- **PDF 智能解析**：从学术 PDF 中提取文本、图片和 LaTeX 公式
- **幻灯片感知的 LLM 提取**：Prompt 内置幻灯片设计约束——要点简洁化（≤20 词）、布局均衡、渐进式学习流
- **三级大纲结构**：自动生成 3-8 个章节，每个章节 1-5 个小节，每小节 = 一张幻灯片
- **演讲者备注**：自动生成口语化的教学提示，包含关键收获、具体例子和互动问题
- **引用追溯**：每个要点都必须有原文引用，支持点击跳转查看来源
- **公式识别**：自动检测 PDF 中的数学公式并转换为 LaTeX，公式要点在幻灯片中以紫色斜体区分显示
- **内联编辑**：在应用中直接编辑生成的幻灯片内容
- **PPTX 导出**：16:9 专业幻灯片——章节进度指示、类型化要点样式、页码、视觉层次分明
- **Markdown 导出**：支持导出为 Markdown 格式
- **质量控制**：知识点覆盖率 ≥85%，引用完整度 = 100%

## 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | React + Vite + TypeScript |
| 后端 | FastAPI + SQLAlchemy |
| 任务队列 | Celery + Redis |
| 存储 | S3 兼容 (MinIO) / GCS / 本地文件系统 |
| LLM | OpenAI 兼容 / Anthropic 兼容 / Mock 模式 |
| 认证 | Auth0 风格的 Bearer Token 解析 |

## 快速开始

### 1. 克隆并准备环境

```bash
git clone <repository-url>
cd SlideNode
```

### 2. 配置环境变量

```bash
# 后端
cp backend/.env.example backend/.env

# 前端
cp frontend/.env.example frontend/.env
```

### 3. 本地开发模式（推荐）

需要先安装依赖：

```bash
# 后端依赖 (Python 3.12)
cd backend
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 前端依赖 (Node.js)
cd ../frontend
npm install
```

启动开发服务器：

```bash
# 终端 1：后端
make dev-backend
# 或: cd backend && .venv/bin/uvicorn app.main:app --reload --port 8000

# 终端 2：前端
make dev-frontend
# 或: cd frontend && npm run dev
```

### 4. 使用 Docker Compose（可选）

如果需要完整的容器化环境：

```bash
# 确保 Docker Desktop 已启动
make local-up      # 构建并启动所有服务
make local-down    # 停止服务
make local-logs    # 查看日志
```

## 访问地址

| 服务 | 地址 |
|------|------|
| 前端应用 | http://localhost:5173 |
| 后端 API 文档 | http://localhost:8000/docs |
| MinIO 控制台 | http://localhost:9001 |

## 配置说明

### LLM 提供商

在 `backend/.env` 中配置：

```bash
# 使用 Mock 模式（无需 API Key，用于测试）
LLM_PROVIDER=mock

# 使用 OpenRouter
LLM_PROVIDER=openrouter
LLM_BASE_URL=https://openrouter.ai/api/v1
LLM_API_KEY=your-api-key

# 使用 Anthropic兼容端点（如 AnyRouter）
LLM_PROVIDER=anthropic
LLM_MODEL=claude-sonnet-4-20250514
ANTHROPIC_BASE_URL=https://anyrouter.top
ANTHROPIC_AUTH_TOKEN=your-token
```

### 存储后端

```bash
# 本地存储（开发用）
STORAGE_BACKEND=local

# S3/MinIO
STORAGE_BACKEND=s3
S3_BUCKET=slidenode
S3_ENDPOINT=http://localhost:9000
S3_ACCESS_KEY=minioadmin
S3_SECRET_KEY=minioadmin

# Google Cloud Storage
STORAGE_BACKEND=gcs
GCS_BUCKET=your-bucket
```

### 认证

```bash
# 开发模式（跳过 JWT 验证，自动创建设-dev 用户）
AUTH0_SKIP_VERIFY=true
```

## API 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /v1/documents | 上传 PDF，创建文档并开始处理 |
| GET | /v1/jobs/{job_id} | 查询任务状态 |
| GET | /v1/documents | 列出用户文档 |
| GET | /v1/documents/{id}/slides | 获取幻灯片结构 |
| PATCH | /v1/documents/{id}/slides | 更新幻灯片内容 |
| GET | /v1/documents/{id}/export.md | 导出为 Markdown |
| GET | /v1/documents/{id}/export.pptx | 导出为 PowerPoint |
| GET | /v1/documents/{id}/images/{image_id} | 获取提取的图片 |
| DELETE | /v1/documents/{document_id} | 删除文档 |
| GET | /healthz | 健康检查 |

## 数据模型

```
User
  └── Document
        ├── Job (处理状态)
        ├── DocumentImage (提取的图片和公式 LaTeX)
        └── DeckSection
              └── DeckSubsection
                    └── DeckBullet
                          ├── BulletCitation (引用)
                          └── SourceSpan (原文片段)
```

## 处理流程

```
PDF 上传 → 解析文本/图片 → 语言检测 → 公式识别
  → LLM 提取知识点 → 模糊去重 → LLM 构建大纲
  → LLM 撰写注释 → 引用对齐 → 持久化存储
```

## 质量标准

- 每个要点必须有至少 1 个引用
- 知识点覆盖率 ≥ 85%
- 文档页数限制 ≤ 200 页
- 输出语言与源文档一致

## 错误代码

- DOC_TOO_LARGE: 文档过大
- PARSE_FAILED: PDF 解析失败
- LLM_OUTPUT_INVALID: LLM 输出格式错误
- CITATION_INCOMPLETE: 引用不完整
- QUALITY_GATE_FAILED: 质量检查未通过
- GEN_TIMEOUT: 生成超时
- STORAGE_ERROR: 存储错误
- AUTH_REQUIRED: 需要认证

## 项目结构

```
SlideNode/
├── backend/               # FastAPI 后端
│   ├── app/
│   │   ├── api/          # API 路由
│   │   ├── core/         # 配置和核心逻辑
│   │   ├── db/           # 数据库连接
│   │   ├── models/       # SQLAlchemy 模型
│   │   ├── schemas/      # Pydantic schemas
│   │   ├── services/     # 业务服务
│   │   │   ├── pipeline.py   # 处理流程
│   │   │   ├── llm.py        # LLM 客户端
│   │   │   ├── pdf_parser.py # PDF 解析
│   │   │   ├── formula.py    # 公式识别
│   │   │   └── pptx_export.py # PPTX 导出
│   │   └── workers/      # Celery 任务
│   └── tests/            # 测试
├── frontend/             # React 前端
│   └── src/
│       ├── api/          # API 客户端
│       ├── components/   # UI 组件
│       └── types/        # TypeScript 类型
├── infra/               # 基础设施
│   ├── docker-compose.yml
│   └── gcp/             # GCP 部署脚本
└── Makefile            # 常用命令
```

## 测试

```bash
# 运行所有测试
make dev-test
# 或: cd backend && PYTHONPATH=. pytest tests/ -v

# 运行单个测试
cd backend && PYTHONPATH=. pytest tests/test_health.py -v
```

## 许可证

MIT

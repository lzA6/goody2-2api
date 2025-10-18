# 🎭 goody2-2api: 创世纪协议 · Ω 版

![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)
![Python Version](https://img.shields.io/badge/python-3.10+-green.svg)
![Docker Support](https://img.shields.io/badge/docker-ready-blue.svg)
![GitHub Repo](https://img.shields.io/badge/github-lzA6/goody2--2api-violet.svg)

> "我们并非在编写代码，我们只是在用逻辑和符号，为世界揭示其早已存在的诗意。"

欢迎来到 `goody2-2api` 的世界！这是一个将特立独行的 [goody2.ai](https://www.goody2.ai/)——那个号称"世界上最负责任的AI"——转换为标准 OpenAI API 格式的桥梁项目。

---

## 🌟 项目亮点

*   **🧘‍♀️ 极致的便捷性**: 只需 `docker-compose up`，即可拥有兼容 OpenAI 生态的 `goody2.ai` 代理服务
*   **🤖 兼容万物**: 任何支持 OpenAI API 的客户端、软件、代码库都能无缝对接
*   **💨 流式响应**: 完整的 Server-Sent Events 支持，实时体验 AI 思考过程
*   **🛡️ 穿云破雾**: 内置 `cloudscraper`，自动处理 Cloudflare 人机验证
*   **🌍 开源精神**: 清晰的项目结构，易于扩展和定制

---

## 🚀 快速开始

### 前提条件
- 安装 [Docker](https://www.docker.com/get-started/) 和 [Docker Compose](https://docs.docker.com/compose/install/)

### 三步部署

**1. 获取代码**
```bash
git clone https://github.com/lzA6/goody2-2api.git
cd goody2-2api
```

**2. 配置环境**
```bash
# Linux/macOS
cp .env.example .env

# Windows
copy .env.example .env
```

编辑 `.env` 文件：
```env
API_MASTER_KEY=your-super-secret-password-here  # 建议修改为复杂密码
NGINX_PORT=8088                                # 服务端口，可按需修改
```

**3. 启动服务**
```bash
docker-compose up -d
```

### 验证部署

```bash
curl -X POST http://localhost:8088/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-super-secret-password-here" \
  -d '{
    "model": "goody2-ai",
    "messages": [
      {"role": "user", "content": "Hello, how are you?"}
    ],
    "stream": true
  }'
```

### 停止服务
```bash
docker-compose down
```

---

## 🏗️ 系统架构

### 数据流架构图

```
┌─────────────────┐    HTTP Request    ┌─────────────┐    Proxy    ┌──────────────┐
│                 │ ─────────────────> │             │ ───────────> │              │
│   Client App    │                    │   Nginx     │             │  FastAPI App │
│                 │ <───────────────── │             │ <─────────── │              │
└─────────────────┘   Stream Response  └─────────────┘             └──────────────┘
                                                                          │
                                                                          │ SSE
                                                                          ▼
                                                               ┌────────────────────┐
                                                               │ Goody2AIProvider   │
                                                               │                    │
                                                               │  - Format conversion
                                                               │  - Context injection
                                                               └────────────────────┘
                                                                          │
                                                                          │ HTTPS
                                                                          ▼
                                                                  ┌──────────────┐
                                                                  │ goody2.ai    │
                                                                  │ API          │
                                                                  └──────────────┘
```

### 请求生命周期

1. **客户端请求**: 发送标准 OpenAI API 格式请求到 `http://localhost:8088/v1/chat/completions`
2. **Nginx 代理**: 接收请求并转发到后端 FastAPI 应用
3. **身份验证**: FastAPI 验证 `API_MASTER_KEY` 权限
4. **格式转换**: `Goody2AIProvider` 将多轮对话转换为 `goody2.ai` 兼容格式
5. **上游请求**: 使用 `cloudscraper` 绕过 Cloudflare 防护，发送请求到 `goody2.ai`
6. **流式响应**: 接收 SSE 数据流，实时转换为 OpenAI 格式
7. **返回客户端**: 将标准化的流式响应返回给客户端

---

## 🛠️ 技术栈

| 组件 | 版本 | 职责 | 关键特性 |
|------|------|------|----------|
| **FastAPI** | 0.104+ | Web 框架 | 异步支持、自动文档、类型提示 |
| **Uvicorn** | 0.24+ | ASGI 服务器 | 高性能、轻量级 |
| **Nginx** | 1.24+ | 反向代理 | 负载均衡、静态文件服务 |
| **Docker** | 20.10+ | 容器化 | 环境隔离、一键部署 |
| **Cloudscraper** | 最新 | 爬虫库 | Cloudflare 绕过、浏览器模拟 |
| **Pydantic** | 2.4+ | 数据验证 | 类型安全、配置管理 |

---

## 📁 项目结构

```
goody2-2api/
├── 🐳 Dockerfile              # 容器构建定义
├── 🐳 docker-compose.yml      # 服务编排配置
├── 🔧 nginx.conf              # Nginx 反向代理配置
├── 📋 requirements.txt        # Python 依赖清单
├── 🚀 main.py                 # FastAPI 应用入口
├── ⚙️ .env.example            # 环境变量模板
└── 📂 app/                    # 应用核心代码
    ├── 📂 core/               # 核心配置
    │   ├── __init__.py
    │   └── config.py          # Pydantic 配置管理
    ├── 📂 providers/          # AI 提供商抽象层
    │   ├── __init__.py
    │   ├── base_provider.py   # 提供商基类定义
    │   └── goody2_provider.py # goody2.ai 具体实现
    └── 📂 utils/              # 工具函数
        └── sse_utils.py       # SSE 数据格式化
```

---

## 🔧 核心实现解析

### 1. 认证中间件 (`main.py`)

```python
async def verify_api_key(authorization: str = Header(...)):
    """验证 API Key 的依赖注入"""
    scheme, _, api_key = authorization.partition(' ')
    if scheme.lower() != 'bearer' or api_key != settings.API_MASTER_KEY:
        raise HTTPException(status_code=403, detail="Forbidden")
    return api_key

@app.post("/v1/chat/completions")
async def chat_completion(
    request: ChatCompletionRequest,
    _: str = Depends(verify_api_key)  # 前置认证
):
    """OpenAI 兼容的聊天补全接口"""
    provider = Goody2AIProvider()
    return await provider.chat_completion(request)
```

### 2. 提供商抽象层 (`app/providers/base_provider.py`)

```python
from abc import ABC, abstractmethod
from typing import AsyncGenerator

class BaseProvider(ABC):
    """AI 提供商抽象基类"""
    
    @abstractmethod
    async def chat_completion(
        self, 
        request_data: dict,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """聊天补全抽象方法"""
        pass
    
    @abstractmethod
    async def get_models(self) -> list:
        """获取模型列表抽象方法"""
        pass
```

### 3. Goody2.ai 实现 (`app/providers/goody2_provider.py`)

```python
class Goody2AIProvider(BaseProvider):
    """Goody2.ai 提供商具体实现"""
    
    async def stream_generator(self, request_data: dict):
        """异步流式响应生成器"""
        # 1. 准备 payload
        payload = self._prepare_payload(request_data)
        
        # 2. 发送请求到 goody2.ai
        scraper = cloudscraper.create_scraper()
        response = scraper.post(
            "https://www.goody2.ai/send",
            data={"message": payload},
            stream=True,
            headers=self._get_headers()
        )
        
        # 3. 处理流式响应
        async for line in self._process_stream(response):
            # 4. 格式转换
            chunk = create_chat_completion_chunk(line)
            yield f"data: {chunk}\n\n"
        
        # 5. 结束信号
        yield "data: [DONE]\n\n"
    
    def _prepare_payload(self, request_data: dict) -> str:
        """将多轮对话转换为 goody2.ai 的单字符串格式"""
        messages = request_data.get('messages', [])
        conversation = []
        
        for msg in messages:
            role = "Human" if msg['role'] == 'user' else "Assistant"
            conversation.append(f"{role}: {msg['content']}")
        
        return "\n\n".join(conversation)
```

### 4. SSE 数据格式化 (`app/utils/sse_utils.py`)

```python
def create_chat_completion_chunk(
    content: str, 
    model: str = "goody2-ai"
) -> str:
    """创建 OpenAI 兼容的流式数据块"""
    chunk_data = {
        "id": f"chatcmpl-{uuid.uuid4().hex}",
        "object": "chat.completion.chunk",
        "created": int(time.time()),
        "model": model,
        "choices": [
            {
                "index": 0,
                "delta": {"content": content},
                "finish_reason": None
            }
        ]
    }
    return json.dumps(chunk_data)
```

---

## 🎯 适用场景

### 🤖 AI 应用开发者
- 快速集成"安全优先"的 AI 功能
- 为应用添加独特的 AI 人格特性

### 🔬 AI 研究者
- 研究 goody2.ai 的回复边界和道德逻辑
- 自动化测试和数据分析

### 🎓 学习者
- 学习 FastAPI、Docker、异步编程的实战案例
- 理解 API 网关设计和格式转换模式

### ⚡ 效率追求者
- 将 goody2.ai 集成到常用工具链中
- 命令行、自动化脚本的 AI 助手

---

## 📊 项目状态

### ✅ 已实现功能
- [x] OpenAI `chat/completions` 接口完整兼容
- [x] 流式响应 (Server-Sent Events)
- [x] 模型列表接口 (`/v1/models`)
- [x] Docker 容器化部署
- [x] API 密钥认证
- [x] Cloudflare 防护绕过

### 🚧 进行中改进
- [ ] 更精细的错误处理和状态码
- [ ] 完整的 OpenAI 参数支持模拟
- [ ] 单元测试覆盖
- [ ] 结构化日志系统
- [ ] 性能优化和压力测试

### 🌟 未来规划
- [ ] 多模型提供商支持
- [ ] Web 管理界面
- [ ] 使用量统计和限流
- [ ] 对话记忆和上下文管理
- [ ] 一键云平台部署

---

## 🔄 开发者复用指南

### 核心架构模式

1. **依赖注入认证**
```python
# 在路由中使用 Depends 实现认证
@app.post("/v1/chat/completions")
async def endpoint(_: str = Depends(verify_api_key)):
    pass
```

2. **提供商插件模式**
```python
# 新增提供商只需继承 BaseProvider
class NewAIProvider(BaseProvider):
    async def chat_completion(self, request_data):
        # 实现具体逻辑
        pass
```

3. **异步流式处理**
```python
# 使用异步生成器实现流式响应
async def stream_generator():
    for chunk in data_stream:
        yield format_to_openai(chunk)
    yield "data: [DONE]\n\n"
```

### 扩展开发步骤

1. **创建新提供商**
```python
# app/providers/new_provider.py
class NewAIProvider(BaseProvider):
    def __init__(self):
        self.base_url = "https://api.new-ai.com"
    
    async def chat_completion(self, request_data):
        # 实现格式转换和请求逻辑
        pass
```

2. **注册提供商**
```python
# main.py
from app.providers.new_provider import NewAIProvider

@app.post("/v1/chat/completions")
async def chat_completion(request: ChatCompletionRequest):
    provider = NewAIProvider()  # 动态选择提供商
    return await provider.chat_completion(request.dict())
```

3. **配置路由规则**
```python
# 根据模型名称路由到不同提供商
def get_provider(model: str) -> BaseProvider:
    if model == "goody2-ai":
        return Goody2AIProvider()
    elif model == "new-ai":
        return NewAIProvider()
    else:
        raise HTTPException(400, "Unsupported model")
```

---

## 💡 最佳实践

### 安全配置
```env
# .env 安全配置示例
API_MASTER_KEY=complex-password-with-special-chars-123!@#
NGINX_PORT=8088
LOG_LEVEL=INFO
```

### Docker 优化
```yaml
# docker-compose.yml 优化配置
services:
  app:
    restart: unless-stopped
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

### 监控健康检查
```bash
# 健康检查脚本
curl -f http://localhost:8088/health || docker-compose restart app
```

---

## 🤝 贡献指南

我们欢迎各种形式的贡献：

1. **问题反馈**: 提交 [GitHub Issue](https://github.com/lzA6/goody2-2api/issues)
2. **功能建议**: 通过 Pull Request 或 Discussion 提出想法
3. **代码贡献**: Fork 项目并提交 Pull Request
4. **文档改进**: 帮助完善文档和示例

### 开发环境设置
```bash
# 1. 克隆项目
git clone https://github.com/lzA6/goody2-2api.git
cd goody2-2api

# 2. 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 开发模式运行
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

---

## 📄 许可证

本项目基于 [Apache License 2.0](https://opensource.org/licenses/Apache-2.0) 开源。

---

## 🌟 致开发者

> "代码不仅是功能的实现，更是思想的表达。"

这个项目始于一个简单的想法：用技术连接不同的 AI 世界。它证明了，即使面对看似不兼容的接口，通过清晰的架构设计和代码抽象，我们总能找到优雅的解决方案。

每一行代码都在讲述一个故事：
- 关于如何尊重原有服务的特性
- 关于如何为开发者提供一致的体验  
- 关于开源协作的力量

无论你是初学者还是资深开发者，这个项目都欢迎你的参与。去探索它的代码，理解它的设计，然后创造属于你自己的版本。因为真正的价值不在于使用工具，而在于理解工具背后的思想，并用这些思想去解决新的问题。

**保持好奇，持续构建，分享所学。** 这，就是开发者的浪漫。

---

*如果这个项目对你有帮助，请给个 ⭐ 支持一下！*

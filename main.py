import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, HTTPException, Depends, Header
from fastapi.responses import JSONResponse, StreamingResponse
from typing import Optional

from app.core.config import settings
from app.providers.goody2_provider import Goody2AIProvider

# --- 日志配置 ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- 全局 Provider 实例 ---
provider = Goody2AIProvider()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    logger.info(f"启动 {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info("驱动协议: 创世纪协议 · Ω (Omega) 版")
    logger.info("服务已进入 'Cloudscraper' 模式，将自动处理潜在的 Cloudflare 挑战。")
    logger.info(f"服务将在 http://localhost:{settings.NGINX_PORT}/v1 上可用")
    yield
    logger.info("应用关闭。")

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=settings.DESCRIPTION,
    lifespan=lifespan
)

async def verify_api_key(authorization: Optional[str] = Header(None)):
    """验证 API Key"""
    if settings.API_MASTER_KEY:
        if not authorization or "bearer" not in authorization.lower():
            raise HTTPException(status_code=401, detail="需要 Bearer Token 认证。")
        token = authorization.split(" ")[-1]
        if token != settings.API_MASTER_KEY:
            raise HTTPException(status_code=403, detail="无效的 API Key。")

@app.post("/v1/chat/completions", dependencies=[Depends(verify_api_key)])
async def chat_completions(request: Request) -> StreamingResponse:
    """处理聊天补全请求"""
    try:
        request_data = await request.json()
        return await provider.chat_completion(request_data)
    except Exception as e:
        logger.error(f"处理聊天请求时发生顶层错误: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"内部服务器错误: {str(e)}")

@app.get("/v1/models", dependencies=[Depends(verify_api_key)], response_class=JSONResponse)
async def list_models():
    """列出可用模型"""
    return await provider.get_models()

@app.get("/", summary="根路径", include_in_schema=False)
def root():
    return {"message": f"欢迎来到 {settings.APP_NAME} v{settings.APP_VERSION}. 服务运行正常。请访问 /docs 查看API文档。"}

import json
import time
import logging
import uuid
import cloudscraper
from typing import Dict, Any, AsyncGenerator

from fastapi.responses import StreamingResponse, JSONResponse

from app.core.config import settings
from app.providers.base_provider import BaseProvider
from app.utils.sse_utils import create_sse_data, create_chat_completion_chunk, DONE_CHUNK

logger = logging.getLogger(__name__)

class Goody2AIProvider(BaseProvider):
    def __init__(self):
        self.scraper = cloudscraper.create_scraper()
        self.send_url = "https://www.goody2.ai/send"

    async def chat_completion(self, request_data: Dict[str, Any]) -> StreamingResponse:
        
        async def stream_generator() -> AsyncGenerator[bytes, None]:
            request_id = f"chatcmpl-{uuid.uuid4()}"
            model_name = request_data.get("model", settings.DEFAULT_MODEL)
            
            try:
                payload = self._prepare_payload(request_data)
                headers = self._prepare_headers()

                # 使用 scraper 发送同步的流式请求
                response = self.scraper.post(self.send_url, headers=headers, json=payload, stream=True)
                response.raise_for_status()

                for line in response.iter_lines():
                    if line.startswith(b"data:"):
                        content_str = line[len(b"data:"):].strip().decode('utf-8')
                        if not content_str or content_str == "[DONE]":
                            continue
                        
                        try:
                            data = json.loads(content_str)
                            # 处理内容块
                            if "content" in data:
                                delta_content = data.get("content")
                                if delta_content is not None:
                                    chunk = create_chat_completion_chunk(request_id, model_name, delta_content)
                                    yield create_sse_data(chunk)
                            # 忽略包含 conversation token 的最终块
                            elif "conversation" in data:
                                logger.info("接收到会话令牌，流式传输即将结束。")
                                continue

                        except json.JSONDecodeError:
                            logger.warning(f"无法解析 SSE 数据块: {content_str}")
                            continue
                
                # 发送最后的终止块
                final_chunk = create_chat_completion_chunk(request_id, model_name, "", "stop")
                yield create_sse_data(final_chunk)
                yield DONE_CHUNK

            except Exception as e:
                logger.error(f"处理流时发生错误: {e}", exc_info=True)
                error_message = f"上游请求失败: {str(e)}"
                error_chunk = {
                    "id": request_id,
                    "object": "chat.completion.chunk",
                    "created": int(time.time()),
                    "model": model_name,
                    "choices": [{"index": 0, "delta": {"content": error_message}, "finish_reason": "error"}]
                }
                yield create_sse_data(error_chunk)
                yield DONE_CHUNK

        return StreamingResponse(stream_generator(), media_type="text/event-stream")

    def _prepare_headers(self) -> Dict[str, str]:
        # cloudscraper 会自动管理 User-Agent
        return {
            "accept": "*/*",
            "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
            "content-type": "text/plain",
            "origin": "https://www.goody2.ai",
            "referer": "https://www.goody2.ai/chat",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
        }

    def _prepare_payload(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        messages = request_data.get("messages", [])
        
        # 战术-上下文注入: 将多轮对话历史格式化为单个字符串
        formatted_message = "\n\n".join([f"{msg['role']}: {msg['content']}" for msg in messages])
        
        return {
            "message": formatted_message,
            "debugParams": None
        }

    async def get_models(self) -> JSONResponse:
        model_data = {
            "object": "list",
            "data": [
                {"id": name, "object": "model", "created": int(time.time()), "owned_by": "lzA6-Genesis-Omega"}
                for name in settings.KNOWN_MODELS
            ]
        }
        return JSONResponse(content=model_data)

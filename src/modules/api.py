"""
AgiComm 统一仿真 API：媒体提问等路由均在此注册。
启动（请在仓库根目录执行，保证 data/ 相对路径可用）：
  python -m src.modules.api
"""
from typing import Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator

from src.modules.media_inquiring.inquiry_engine import InquiryEngine
from src.modules.responses import (
    ErrorCode,
    error_json_response,
    setup_exception_handlers,
    success_body,
)
from src.utils.llm_client import LLMUnavailableError

# ---------------------------------------------------------------------------
# 媒体提问仿真（延迟加载，首请求时加载失败可返回统一错误体）
# ---------------------------------------------------------------------------
_engine: Optional[InquiryEngine] = None
_ENGINE_PATH = "data/processed/media_science_inquiring_generalized.csv"


def _get_engine() -> InquiryEngine:
    global _engine
    if _engine is None:
        _engine = InquiryEngine(_ENGINE_PATH)
    return _engine


class EventRequest(BaseModel):
    event_text: str = Field(
        ...,
        min_length=1,
        description="科技/外交类事件的文本描述，用于驱动全部媒体 Agent 生成提问",
    )

    @field_validator("event_text")
    @classmethod
    def strip_and_nonempty(cls, v: str) -> str:
        t = v.strip()
        if not t:
            raise ValueError("事件描述不能为空或仅包含空白字符")
        return t


app = FastAPI(
    title="AgiComm Simulation API",
    description="统一仿真入口：媒体提问及后续扩展模块。",
    version="1.0.0",
)

setup_exception_handlers(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/simulate/inquiry")
async def run_inquiry(request: EventRequest):
    try:
        data = _get_engine().simulate_press_conference(request.event_text)
    except FileNotFoundError as e:
        return error_json_response(
            ErrorCode.DATA_FILE_MISSING,
            "媒体提问画像数据文件不存在或路径错误",
            f"请确认在仓库根目录启动服务，且存在 {_ENGINE_PATH}。详情：{e}",
            503,
        )
    except OSError as e:
        return error_json_response(
            ErrorCode.DATA_READ_FAILED,
            "无法读取媒体提问画像数据",
            str(e) or type(e).__name__,
            503,
        )
    except LLMUnavailableError as e:
        reason = " | ".join(
            f"{a.get('provider', '?')}: {a.get('error', '')}" for a in e.attempts
        )
        return error_json_response(
            ErrorCode.LLM_UNAVAILABLE,
            "大模型服务全部不可用，仿真无法生成提问",
            f"{e.message}。各供应商错误：{reason}",
            503,
        )
    except Exception as e:
        return error_json_response(
            ErrorCode.SIMULATION_FAILED,
            "媒体提问仿真执行失败",
            str(e) or type(e).__name__,
            500,
        )

    return success_body(
        data,
        meta={
            "count": len(data),
            "endpoint": "/simulate/inquiry",
        },
    )


@app.get("/health")
async def health():
    return {"status": "ok", "service": "agicomm"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)

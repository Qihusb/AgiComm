"""
统一 API 响应体与异常处理（媒体提问及后续模块可复用）。
成功：{ "status": "success", "data": ..., "meta": { ... } }
失败：{ "status": "error", "error": { "code", "message", "reason" } }
"""
from __future__ import annotations

from typing import Any, Optional

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


class ErrorCode:
    """业务/协议层错误码（与 HTTP 状态码配合使用）"""

    VALIDATION_ERROR = "VALIDATION_ERROR"
    EMPTY_EVENT = "EMPTY_EVENT"
    DATA_FILE_MISSING = "DATA_FILE_MISSING"
    DATA_READ_FAILED = "DATA_READ_FAILED"
    SIMULATION_FAILED = "SIMULATION_FAILED"
    LLM_UNAVAILABLE = "LLM_UNAVAILABLE"
    INTERNAL_ERROR = "INTERNAL_ERROR"


def success_body(
    data: Any,
    meta: Optional[dict[str, Any]] = None,
) -> dict[str, Any]:
    out: dict[str, Any] = {"status": "success", "data": data}
    if meta:
        out["meta"] = meta
    return out


def error_body(
    code: str,
    message: str,
    reason: str,
) -> dict[str, Any]:
    return {
        "status": "error",
        "error": {
            "code": code,
            "message": message,
            "reason": reason,
        },
    }


def error_json_response(
    code: str,
    message: str,
    reason: str,
    http_status: int = status.HTTP_400_BAD_REQUEST,
) -> JSONResponse:
    return JSONResponse(
        status_code=http_status,
        content=error_body(code, message, reason),
    )


def setup_exception_handlers(app: FastAPI) -> None:
    """仅注册可安全统一格式的异常；业务错误在路由内显式返回。"""

    @app.exception_handler(RequestValidationError)
    async def validation_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        errs = exc.errors()
        first = errs[0] if errs else {}
        loc = " -> ".join(str(x) for x in first.get("loc", ()))
        msg = first.get("msg", "参数校验失败")
        reason = f"{loc}: {msg}" if loc else msg
        return error_json_response(
            ErrorCode.VALIDATION_ERROR,
            "请求参数不符合接口约定",
            reason,
            status.HTTP_422_UNPROCESSABLE_ENTITY,
        )

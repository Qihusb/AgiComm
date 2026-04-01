"""
AgiComm 统一仿真 API：媒体提问等路由均在此注册。
启动（请在仓库根目录执行，保证 data/ 相对路径可用）：
  python -m src.modules.api
"""
import json
from typing import Optional
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import StreamingResponse, FileResponse
from pydantic import BaseModel, Field, field_validator

from src.modules.media_inquiring.inquiry_engine import InquiryEngine
from src.modules.news_generation.news_generation_engine import NewsGenerationEngine
from src.modules.responses import (
    ErrorCode,
    error_body,
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


# ---------------------------------------------------------------------------
# 媒体报道仿真（新闻生成，延迟加载）
# ---------------------------------------------------------------------------
_news_engine: Optional[NewsGenerationEngine] = None
_NEWS_ENGINE_PATH = "data/processed/media_science_news_generalized.csv"


def _get_engine() -> InquiryEngine:
    global _engine
    if _engine is None:
        _engine = InquiryEngine(_ENGINE_PATH)
    return _engine


def _get_news_engine() -> NewsGenerationEngine:
    global _news_engine
    if _news_engine is None:
        _news_engine = NewsGenerationEngine(_NEWS_ENGINE_PATH)
    return _news_engine


class EventRequest(BaseModel):
    event_text: str = Field(
        ...,
        min_length=1,
        description="科技/外交类事件的文本描述，用于驱动媒体 Agent 生成提问",
    )
    media_ids: Optional[list] = Field(
        None,
        description="指定媒体 ID 列表，为空则使用全部媒体",
    )

    @field_validator("event_text")
    @classmethod
    def strip_and_nonempty(cls, v: str) -> str:
        t = v.strip()
        if not t:
            raise ValueError("事件描述不能为空或仅包含空白字符")
        return t

    @field_validator("media_ids")
    @classmethod
    def validate_media_ids(cls, v: list) -> list:
        if v is None:
            return []
        return v


class NewsRequest(BaseModel):
    event_text: str = Field(
        ...,
        min_length=1,
        description="科技事件的文本描述",
    )
    event_date: Optional[str] = Field(
        None,
        description="事件发生日期（YYYY-MM-DD 格式）",
    )
    media_ids: Optional[list] = Field(
        None,
        description="指定媒体 ID 列表（最多 10 个），为空则使用全部媒体",
    )

    @field_validator("event_text")
    @classmethod
    def strip_and_nonempty(cls, v: str) -> str:
        t = v.strip()
        if not t:
            raise ValueError("事件描述不能为空或仅包含空白字符")
        return t

    @field_validator("media_ids")
    @classmethod
    def validate_media_ids(cls, v: list) -> list:
        if v is None:
            return []
        if len(v) > 10:
            raise ValueError("最多只能选择 10 个媒体")
        return v


app = FastAPI(
    title="AgiComm Simulation API",
    description="统一仿真入口：媒体提问及后续扩展模块。",
    version="1.0.0",
    docs_url="/docs",  # 确保文档可用
    redocs_url="/redoc",
)

setup_exception_handlers(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from src.utils.llm_client import llm_client
# 在 app 定义后添加
@app.on_event("startup")
async def startup_event():
    """服务启动时自动检查模型状态"""
    results = llm_client.check_health()
    ok_count = sum(1 for r in results if r["status"] == "ok")
    print(f"✅ LLM 自检完成: {ok_count}/{len(results)} 个模型可用")
    if ok_count == 0:
        print("❌ 警告：当前没有任何可用的 LLM 配置，请检查 .env 文件！")

# 暴露一个接口供前端查看状态
@app.get("/llm/status")
async def get_llm_status():
    """
    美化后的 LLM 状态检查接口
    """
    raw_results = llm_client.check_health()
    
    # 统计数据
    total = len(raw_results)
    online = sum(1 for r in raw_results if r["status"] == "ok")
    
    # 分组展示
    available_models = [r["model"] for r in raw_results if r["status"] == "ok"]
    errors = []
    
    for r in raw_results:
        if r["status"] != "ok":
            # 简写错误信息，避免暴露完整的 OpenAI 报错链接，显得凌乱
            short_error = r["error"].split(" - ")[-1] if " - " in r["error"] else r["error"]
            errors.append({
                "model": r["model"],
                "reason": short_error
            })

    # 构造美化后的响应
    styled_data = {
        "summary": {
            "title": "AgiComm 模型服务监控",
            "status_icon": "✅ 运行中" if online > 0 else "❌ 全线宕机",
            "health_rate": f"{online}/{total}",
            "last_check": "刚刚"
        },
        "active_pool": {
            "count": online,
            "models": available_models
        },
        "error_log": errors if errors else "无异常"
    }

    return success_body(styled_data)

# ---------------------------------------------------------------------------
# 【修复 1】健康检查接口（确保 GET 可访问）
# ---------------------------------------------------------------------------
@app.get("/health")
async def health():
    return {"status": "ok", "service": "agicomm"}

# ---------------------------------------------------------------------------
# 【核心提问接口 - 流式响应】支持媒体选择和流式输出
# ---------------------------------------------------------------------------
@app.post("/simulate/inquiry")
async def inquiry_stream_generator(request: EventRequest):
    """
    流式提问接口：
    - 支持 media_ids 参数指定媒体（为空则全部媒体）
    - 返回 NDJSON 格式流式响应（每行一个 JSON 对象）
    """
    try:
        media_ids = request.media_ids if request.media_ids else None
        generator = _get_engine().simulate_press_conference_stream(
            request.event_text, 
            media_ids
        )
        
        def stream_generator():
            try:
                for result in generator:
                    yield json.dumps(result, ensure_ascii=False) + '\n'
            except FileNotFoundError as e:
                yield json.dumps(
                    error_body(
                        ErrorCode.DATA_FILE_MISSING,
                        "媒体提问画像数据文件不存在或路径错误",
                        f"请确认在仓库根目录启动服务，且存在 {_ENGINE_PATH}。详情：{e}"
                    ),
                    ensure_ascii=False
                ) + '\n'
            except OSError as e:
                yield json.dumps(
                    error_body(
                        ErrorCode.DATA_READ_FAILED,
                        "无法读取媒体提问画像数据",
                        str(e) or type(e).__name__
                    ),
                    ensure_ascii=False
                ) + '\n'
            except LLMUnavailableError as e:
                reason = " | ".join(
                    f"{a.get('provider', '?')}: {a.get('error', '')}" for a in e.attempts
                )
                yield json.dumps(
                    error_body(
                        ErrorCode.LLM_UNAVAILABLE,
                        "大模型服务全部不可用，仿真无法生成提问",
                        f"{e.message}。各供应商错误：{reason}"
                    ),
                    ensure_ascii=False
                ) + '\n'
            except Exception as e:
                yield json.dumps(
                    error_body(
                        ErrorCode.SIMULATION_FAILED,
                        "媒体提问仿真执行失败",
                        str(e) or type(e).__name__
                    ),
                    ensure_ascii=False
                ) + '\n'
        
        return StreamingResponse(stream_generator(), media_type="application/x-ndjson")
    
    except Exception as e:
        return error_json_response(
            ErrorCode.SIMULATION_FAILED,
            "媒体提问仿真执行失败",
            str(e) or type(e).__name__,
            500,
        )


# ---------------------------------------------------------------------------
# 【新闻生成】核心接口（支持流式响应）
# ---------------------------------------------------------------------------
async def news_stream_generator(request: NewsRequest):
    """异步生成器：流式输出每个媒体的报道"""
    print(f"🔷 news_stream_generator 启动 - event_text: {request.event_text[:50]}, media_ids: {request.media_ids}")
    
    try:
        data = _get_news_engine().simulate_news(
            event_description=request.event_text,
            event_date=request.event_date,
            media_ids=request.media_ids if request.media_ids else None,
        )
        print(f"🔶 生成 {len(data)} 份报道")
        
        # 流式输出每个报告
        report_count = 0
        for report in data:
            try:
                # 确保 report 有 has_error 标记
                if 'has_error' not in report:
                    report['has_error'] = False
                json_str = json.dumps(report, ensure_ascii=False) + '\n'
                print(f"📤 输出报告 #{report_count + 1}: {report.get('media_id')} - {len(json_str)} 字节")
                yield json_str
                report_count += 1
            except Exception as e:
                # 个别报告序列化失败时，输出错误对象
                error_report = {
                    "media_id": report.get("media_id", "unknown"),
                    "media_name": report.get("media_name", "未知媒体"),
                    "has_error": True,
                    "content": f"报告序列化失败: {str(e)}"
                }
                print(f"⚠️  报告 {report.get('media_id')} 序列化失败: {e}")
                yield json.dumps(error_report, ensure_ascii=False) + '\n'
                report_count += 1
        
        print(f"✅ 流发送完成，共 {report_count} 份报道")
            
    except FileNotFoundError as e:
        print(f"❌ 文件不存在: {e}")
        error_obj = error_body(
            ErrorCode.DATA_FILE_MISSING,
            "媒体报道画像数据文件不存在或路径错误",
            f"请确认在仓库根目录启动服务，且存在 {_NEWS_ENGINE_PATH}。详情：{e}",
        )
        yield json.dumps(error_obj, ensure_ascii=False) + '\n'
        
    except OSError as e:
        print(f"❌ 文件读取错误: {e}")
        error_obj = error_body(
            ErrorCode.DATA_READ_FAILED,
            "无法读取媒体报道画像数据",
            str(e) or type(e).__name__,
        )
        yield json.dumps(error_obj, ensure_ascii=False) + '\n'
        
    except LLMUnavailableError as e:
        print(f"❌ LLM 不可用: {e}")
        reason = " | ".join(
            f"{a.get('provider', '?')}: {a.get('error', '')}" for a in e.attempts
        )
        error_obj = error_body(
            ErrorCode.LLM_UNAVAILABLE,
            "大模型服务全部不可用，无法生成报道",
            f"{e.message}。各供应商错误：{reason}",
        )
        yield json.dumps(error_obj, ensure_ascii=False) + '\n'
        
    except Exception as e:
        print(f"❌ 未知错误: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        error_obj = error_body(
            ErrorCode.SIMULATION_FAILED,
            "媒体报道仿真执行失败",
            str(e) or type(e).__name__,
        )
        yield json.dumps(error_obj, ensure_ascii=False) + '\n'


@app.post("/simulate/news")
async def run_news(request: NewsRequest):
    return StreamingResponse(
        news_stream_generator(request),
        media_type="application/x-ndjson",
    )

# ---------------------------------------------------------------------------
# 【SPA 路由】提供前端应用支持（处理客户端路由）
# ---------------------------------------------------------------------------
frontend_dist = Path(__file__).parent.parent.parent / "frontend" / "dist"

@app.get("/{path_name:path}")
async def serve_spa(path_name: str):
    """
    SPA 路由处理：
    1. 如果请求的文件存在（如 js, css, favicon），直接返回
    2. 否则返回 index.html，由前端 Vue Router 处理路由
    """
    if frontend_dist.exists():
        file_path = frontend_dist / path_name
        # 检查文件是否存在且在允许的目录内
        try:
            if file_path.exists() and file_path.is_file():
                return FileResponse(file_path)
        except (ValueError, OSError):
            pass
    
    # 找不到具体文件时，返回 index.html 让前端处理
    index_path = frontend_dist / "index.html"
    if index_path.exists():
        return FileResponse(index_path)
    
    # 前端未构建时的友好提示
    return {
        "error": "Frontend not built",
        "message": "请在 frontend 目录运行 npm run build，然后重启服务。",
        "solution": "cd frontend && npm run build"
    }

# 根路由特殊处理
@app.get("/")
async def root():
    index_path = frontend_dist / "index.html"
    if index_path.exists():
        return FileResponse(index_path)
    return {
        "error": "Frontend not built",
        "message": "请构建前端应用"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
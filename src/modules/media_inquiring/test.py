"""
媒体提问接口联调脚本：直接向已启动的后端端口发送事件文本，打印 JSON 响应。

使用前请先启动服务（在仓库根目录）：
  python -m src.modules.api

用法：
  python src/modules/media_inquiring/test.py
  python src/modules/media_inquiring/test.py "你的科技事件描述"

可选环境变量：
  AGICOMM_API_BASE  默认 http://127.0.0.1:8000
"""
from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request


def _default_event() -> str:
    return "中国宣布在月球南极发现大量水冰矿藏"


def main() -> int:
    base = os.environ.get("AGICOMM_API_BASE", "http://127.0.0.1:8000").rstrip("/")
    event_text = sys.argv[1] if len(sys.argv) > 1 else _default_event()

    url = f"{base}/simulate/inquiry"
    payload = json.dumps({"event_text": event_text}, ensure_ascii=False).encode("utf-8")

    req = urllib.request.Request(
        url,
        data=payload,
        method="POST",
        headers={"Content-Type": "application/json; charset=utf-8"},
    )

    print(f"POST {url}", file=sys.stderr)
    print(f"event_text: {event_text!r}\n", file=sys.stderr)

    try:
        with urllib.request.urlopen(req, timeout=600) as resp:
            body = resp.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8", errors="replace")
        print(err_body)
        return 1
    except urllib.error.URLError as e:
        print(
            f"无法连接后端：{e}\n请确认已启动：python -m src.modules.api\n"
            f"或设置 AGICOMM_API_BASE 指向正确地址。",
            file=sys.stderr,
        )
        return 1

    try:
        obj = json.loads(body)
        print(json.dumps(obj, ensure_ascii=False, indent=2))
    except json.JSONDecodeError:
        print(body)
        return 1

    status = obj.get("status")
    return 0 if status == "success" else 1


if __name__ == "__main__":
    raise SystemExit(main())

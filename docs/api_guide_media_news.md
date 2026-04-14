# 媒体报道模块 API 使用手册

## 1. 接口概述

本接口用于生成多家媒体对给定科技事件的报道文本。通过读取新闻画像数据，决定哪些媒体会发布报道，并以流式方式返回每家媒体的报道结果。

- **返回模式**：流式 JSON 响应（NDJSON，每行一个对象）
- **媒体覆盖**：可指定多个媒体或使用全部媒体
- **响应内容**：每个媒体的报道信息或错误状态

## 2. 基础信息

| 项                | 值                                    |
| ----------------- | ------------------------------------- |
| **URL**           | `http://localhost:8001/simulate/news` |
| **Method**        | `POST`                                |
| **Content-Type**  | `application/json; charset=utf-8`     |
| **Response-Type** | `application/x-ndjson`                |
| **Timeout**       | 建议设置 60 秒以上                    |

## 3. 请求参数

| 参数名       | 类型          | 必选 | 说明                                 |
| ------------ | ------------- | ---- | ------------------------------------ |
| `event_text` | String        | 是   | 事件描述；不可为空或纯空白           |
| `event_date` | String        | 否   | 事件日期，格式为 `YYYY-MM-DD`        |
| `media_ids`  | Array[String] | 否   | 指定媒体 ID 列表；为空则使用全部媒体 |

### 请求示例

```json
{
  "event_text": "中国成功发射第八颗低轨气象卫星，提升全球气象观测能力。",
  "event_date": "2026-04-12",
  "media_ids": ["media_001", "media_025"]
}
```

## 4. 响应格式

接口以流式方式返回每家媒体的报道对象，响应内容为独立 JSON 对象，每行一个。

### 单条结果字段

| 字段            | 类型    | 说明                                   |
| --------------- | ------- | -------------------------------------- |
| `media_id`      | String  | 媒体 ID                                |
| `media_name`    | String  | 媒体名称                               |
| `country`       | String  | 国家或地区                             |
| `behavior_tag`  | String  | 行为标记，固定为 `媒体报道`            |
| `report_type`   | String  | 报道类型，如 `首发` 或 `转载`          |
| `delay_seconds` | Number  | 模拟报道延迟参考值                     |
| `content`       | String  | 媒体报道正文                           |
| `has_error`     | Boolean | 可选，若为 `true` 表示该条报道存在异常 |

### 响应示例

```json
{"media_id":"media_001","media_name":"新华社","country":"中国","behavior_tag":"媒体报道","report_type":"首发","delay_seconds":12,"content":"中国在气象卫星领域取得重要进展，将显著提升全球天气预报精度。","has_error":false}
{"media_id":"media_025","media_name":"路透社","country":"英国","behavior_tag":"媒体报道","report_type":"转载","delay_seconds":20,"content":"路透社报道称，此次发射进一步巩固了中国在低轨道气象监测方面的能力。","has_error":false}
```

## 5. 错误响应

如果请求参数不符合要求或后端运行异常，接口将返回标准错误响应。错误响应为完整 JSON 对象，并可能伴随 HTTP 4xx/5xx 状态码。

```json
{
  "status": "error",
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "请求参数不符合接口约定",
    "reason": "event_text: 事件描述不能为空或仅包含空白字符"
  }
}
```

## 6. 常见错误码

| error.code          | HTTP 状态 | 典型场景                                 |
| ------------------- | --------- | ---------------------------------------- |
| `VALIDATION_ERROR`  | 422       | 请求体非法、缺少 `event_text` 或内容为空 |
| `DATA_FILE_MISSING` | 503       | 新闻画像数据文件不存在或路径错误         |
| `DATA_READ_FAILED`  | 503       | 数据文件读取失败                         |
| `LLM_UNAVAILABLE`   | 503       | 所有大模型供应商均不可用                 |
| `SIMULATION_FAILED` | 500       | 生成过程发生异常                         |

## 7. 使用建议

- 若仅需部分媒体，可通过 `media_ids` 控制输出范围。
- 推荐在前端使用流式解析方式逐行读取结果，避免一次性等待全部生成完成。
- 若请求返回 `has_error: true`，说明该条报道生成存在异常，应当单独处理。

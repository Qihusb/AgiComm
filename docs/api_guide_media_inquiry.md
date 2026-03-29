# 媒体提问模块 API 使用手册

## 1. 接口概述

本接口模拟外交部/科技发布会场景：根据输入的科技事件，调度媒体仿真引擎，生成多国媒体针对该事件的反应决策与提问。

- **返回模式**：流式 JSON 响应（Server-Sent 事件或分块传输）
- **媒体覆盖**：全球 116 个媒体（可选择部分或全部）
- **响应内容**：是否参与 + 具体提问（如参与）或异常标记

## 2. 基础信息

| 项                | 值                                        |
| ----------------- | ----------------------------------------- |
| **URL**           | `http://localhost:8000/simulate/inquiry`  |
| **Method**        | `POST`                                    |
| **Content-Type**  | `application/json; charset=utf-8`         |
| **Response-Type** | **流式 JSON**（逐条返回）+ 可选元数据     |
| **Timeout**       | 建议设置 60 秒以上（取决于 LLM 响应延迟） |

## 3. 请求参数

| 参数名       | 类型          | 必选 | 范围         | 说明                                                      |
| :----------- | :------------ | :--- | :----------- | :-------------------------------------------------------- |
| `event_text` | String        | 是   | 1–10000 字符 | 科技/外交事件描述；不可为空或纯空白；支持中英文、特殊字符 |
| `media_ids`  | Array[String] | 否   | 1–15 个 ID   | 指定媒体 ID 列表（可选）；若不指定，则使用全部 116 个媒体 |

**媒体 ID 格式示例**：`media_001`、`media_081`、`media_092` 等（共 116 个）

**媒体 ID 完整列表**查询方式：

- 前端已包含完整列表（117 个媒体数据）
- 或通过调用本接口后查看响应中的 `media_id` 字段

## 4. 响应约定

### 4.1 流式 JSON 对象

接口按流式方式逐条返回媒体的仿真结果。**每条记录为独立的 JSON 对象**（非数组，便于逐条解析）。

**单条结果字段**

| 字段               | 类型    | 说明                                                            |
| ------------------ | ------- | --------------------------------------------------------------- |
| `media_id`         | String  | 媒体画像 ID（如 `media_081`）                                   |
| `media_name`       | String  | 媒体名称（如 `路透社`)                                          |
| `country`          | String  | 国家/地区（如 `英国`）                                          |
| `is_participating` | Boolean | 媒体是否参与提问（`true` = 有参与意愿，`false` = 无）           |
| `content`          | String  | 媒体的提问内容；若 `is_participating=false`，内容为空或原因说明 |
| `behavior_tag`     | String  | 行为标记（固定为 `媒体提问`)                                    |

**流式响应示例**（逐行）

```json
{"media_id":"media_081","media_name":"路透社","country":"英国","is_participating":true,"content":"鉴于水冰在太空探索中的战略价值...","behavior_tag":"媒体提问"}
{"media_id":"media_092","media_name":"新华社","country":"中国","is_participating":true,"content":"中方此次发现是否将参与国际月球基地建设计划...","behavior_tag":"媒体提问"}
{"media_id":"media_042","media_name":"半岛电视台","country":"卡塔尔","is_participating":false,"content":"","behavior_tag":"媒体提问"}
```

### 4.2 元数据（可选）

流式响应的最后可能返回一条元数据记录：

```json
{
  "meta": {
    "total_count": 116,
    "processed_count": 116,
    "endpoint": "/simulate/inquiry"
  }
}
```

### 4.3 错误响应

当请求参数非法或后端服务异常时，返回 HTTP 错误状态码和 JSON 错误信息：

| 字段            | 类型   | 说明               |
| --------------- | ------ | ------------------ |
| `status`        | String | 固定为 `error`     |
| `error.code`    | String | 机器可读错误码     |
| `error.message` | String | 用户友好的错误说明 |
| `error.reason`  | String | 技术细节           |

**错误响应示例**

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

## 5. 错误码与 HTTP 状态

| error.code          | HTTP 状态   | 典型场景                                           | 前端处理                                         |
| ------------------- | ----------- | -------------------------------------------------- | ------------------------------------------------ |
| `VALIDATION_ERROR`  | 422         | 请求体非法 JSON、缺少 `event_text`、或内容为空     | 显示参数校验提示，引导用户重新输入               |
| `DATA_FILE_MISSING` | 503         | 媒体数据 CSV 文件不存在或路径错误                  | 显示"后端配置错误"，建议启动后端或检查项目完整性 |
| `DATA_READ_FAILED`  | 503         | 文件存在但读取失败（权限、磁盘等）                 | 显示"文件读取失败"，建议重启后端或检查权限       |
| `LLM_UNAVAILABLE`   | 503         | 全部大模型供应商（智谱、DeepSeek、OpenAI）调用失败 | 显示"大模型服务不可用"，列出故障排查步骤         |
| `SIMULATION_FAILED` | 500         | 仿真过程中的其他异常（如引擎内部错误）             | 显示"仿真执行失败"，建议查看后端日志             |
| `NETWORK_ERROR`     | 无法连接    | 前端无法连接后端服务                               | 显示"网络连接失败"，确认后端已启动               |
| `TIMEOUT_ERROR`     | 408/Timeout | 请求超过 60 秒未响应                               | 显示"请求超时"，建议减少媒体数量或检查网络       |

## 6. 前端集成策略

### 6.1 流式响应解析

前端使用 `fetch` 的流式读取：

```javascript
const response = await fetch("http://localhost:8000/simulate/inquiry", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    event_text: "中国宣布在月球南极发现大量水冰矿藏",
    media_ids: ["media_081", "media_092"], // 可选：若不提供则使用全部媒体
  }),
  signal: AbortSignal.timeout(60000), // 60秒超时
});

const reader = response.body.getReader();
let buffer = "";

while (true) {
  const { value, done } = await reader.read();
  if (done) break;

  buffer += new TextDecoder().decode(value);

  // 逐条解析 JSON 对象
  let start = buffer.indexOf("{");
  while (start !== -1) {
    let end = buffer.indexOf("}", start);
    if (end === -1) break;

    const jsonStr = buffer.slice(start, end + 1);
    try {
      const obj = JSON.parse(jsonStr);
      // 处理媒体记录或元数据
      console.log(obj);
    } catch {}

    buffer = buffer.slice(end + 1);
    start = buffer.indexOf("{");
  }
}
```

### 6.2 异常检测机制

前端在接收到流式数据后，检测 `content` 字段中的异常关键字：

```javascript
const errorKeywords = [
  "模块异常",
  "降级处理",
  "不可用",
  "无法连接",
  "失败",
  "错误",
  "异常",
];

if (errorKeywords.some((kw) => obj.content.includes(kw))) {
  obj.has_error = true; // 标记为异常
  obj.is_participating = false; // 转换为不参与
}
```

**场景示例**：当所有 LLM API 均失败时，后端返回：

```json
{
  "media_id": "media_081",
  "media_name": "路透社",
  "country": "英国",
  "is_participating": true,
  "content": "模块异常，降级处理：所有已配置的模型供应商均不可用",
  "behavior_tag": "媒体提问"
}
```

前端会将其标记为异常，显示为**红色警告**而非蓝色的参与状态。

### 6.3 结果统计

前端基于异常标记重新计算统计数据：

```javascript
const validResults = results.filter((r) => !r.has_error); // 排除异常
const participatingCount = validResults.filter(
  (r) => r.is_participating,
).length;
const participationRate =
  ((100 * participatingCount) / validResults.length).toFixed(1) + "%";
```

**显示格式**：

- 总计：仅有效结果的计数
- 参与提问：有效且 `is_participating=true` 的计数
- 不参与：有效且 `is_participating=false` 的计数
- **异常处理**：单独显示异常数量和故障排查提示

## 7. 媒体选择功能

前端支持两种调用模式：

| 模式             | 媒体\_ID    | 调用参数                     | 适用场景                              |
| ---------------- | ----------- | ---------------------------- | ------------------------------------- |
| **全媒体模式**   | 全部 116 个 | 不指定 `media_ids` 或传 `[]` | 对事件的全球反应评估；耗时较长        |
| **精选媒体模式** | 1–15 个     | 指定 `media_ids: [...]`      | 聚焦特定国家/地区的媒体反应；快速评估 |

**前端 UI 交互**：

- 搜索框：按媒体名称或国家实时过滤
- 复选框：勾选要包含的媒体
- 清空按钮：一键清空所有选择，回到全媒体模式
- 数量提示：显示已选数量和 15 个的上限

## 8. 服务启动与健康检查

### 8.1 启动后端服务

```bash
# 在项目根目录执行（以确保 data/ 路径有效）
python -m src.modules.api
```

预期输出：

```
INFO:     Uvicorn running on http://127.0.0.1:8000
```

### 8.2 健康检查端点

**请求**

```bash
GET http://localhost:8000/health
```

**成功响应（200）**

```json
{ "status": "ok", "service": "agicomm" }
```

**失败响应**

- 连接拒绝 → 后端未启动
- 404 → 后端版本过旧，不支持此端点

### 8.3 前端连接检测

Navbar 组件每 30 秒自动检查一次后端连接，用户也可点击"重试"按钮手动检查。

## 9. 调用示例

### 9.1 使用 cURL 调用全媒体模式

```bash
curl -s -X POST "http://localhost:8000/simulate/inquiry" \
     -H "Content-Type: application/json" \
     -d '{"event_text": "中国宣布在月球南极发现大量水冰矿藏"}' \
     | head -c 500  # 显示前 500 字符
```

### 9.2 使用 Python 调用精选媒体模式

```python
import json
import urllib.request

url = "http://localhost:8000/simulate/inquiry"
payload = json.dumps({
    "event_text": "ChatGPT 突破 1 亿用户大关",
    "media_ids": ["media_045", "media_048", "media_092"]  # 纽约时报、CNN、新华社
}, ensure_ascii=False).encode("utf-8")

req = urllib.request.Request(
    url,
    data=payload,
    method="POST",
    headers={"Content-Type": "application/json; charset=utf-8"}
)

with urllib.request.urlopen(req, timeout=60) as resp:
    print(resp.read().decode("utf-8"))
```

### 9.3 前端发送请求

```javascript
// InquiryView.vue 内实现
const runInquiry = async () => {
  const body = {
    event_text: eventText.value,
    media_ids:
      selectedMedia.value.length > 0
        ? selectedMedia.value.slice(0, 15) // 精选模式
        : [], // 全媒体模式
  };

  const response = await fetch("http://localhost:8000/simulate/inquiry", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
    signal: AbortSignal.timeout(60000),
  });

  // 使用前端流式解析逻辑处理响应
};
```

## 10. 常见问题与故障排查

| 问题                       | 原因                   | 解决方案                                                                              |
| -------------------------- | ---------------------- | ------------------------------------------------------------------------------------- |
| 后端连接失败               | 后端未启动             | 在项目根目录运行 `python -m src.modules.api`                                          |
| 请求超时（>60秒）          | LLM 响应慢或网络不稳定 | 减少选中媒体数量；检查网络；尝试增加超时时间                                          |
| 错误码 `DATA_FILE_MISSING` | 媒体数据文件不存在     | 确认 `data/processed/media_science_inquiring_generalized.csv` 存在；重新下载项目      |
| 错误码 `LLM_UNAVAILABLE`   | 所有 LLM API 不可用    | 检查 `.env` 中的 API 密钥；验证网络可访问 OpenAI/智谱/DeepSeek；更换可用的 API 供应商 |
| 异常率过高（>50%）         | LLM 供应商间歇性故障   | 等待 API 服务恢复；检查后端日志获取详细错误                                           |
| 前端显示空白               | 流式解析失败或网络断开 | 打开浏览器控制台（F12）查看错误日志；刷新页面重试                                     |

## 11. 性能指标与建议

| 指标              | 值                   | 说明                         |
| ----------------- | -------------------- | ---------------------------- |
| 全媒体调用耗时    | 120–300s             | 116 个媒体 × ~1–2s/LLM 调用  |
| 精选 5 个媒体耗时 | 5–15s                | 推荐用于快速原型验证         |
| 同时连接数上限    | 1                    | 当前为单线程阻塞，不支持并发 |
| 单次超时设置      | 60s 最小，建议 120s+ | LLM 响应不稳定时需增加       |

**建议使用策略**：

- 开发/调试阶段：使用精选 3–5 个媒体，快速迭代
- 最终评估：使用全媒体模式或按地区精选，等待完整结果
- 批量测试：避免频繁调用，单个事件充分测试后再批量

## 12. 更新与演进

_文档最后更新时间：2026-03-29_

**已实现特性**：

- ✓ 流式 JSON 响应
- ✓ 媒体精选模式（1～15 个）
- ✓ 异常检测与降级处理
- ✓ 实时进度显示
- ✓ 详细错误分类

**计划中特性**：

- 异步调用支持（批量事件）
- 媒体参数精细化（按行业、地区或语言筛选）
- 响应缓存与去重
- WebSocket 实时推送

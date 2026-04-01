# `src/modules/news_generation/` 报道生成模块

该模块负责“平台报道新闻生成”的仿真：基于 `data/processed/media_science_news_generalized.csv` 中的**媒体动态画像**（科学活动度、叙事权重、语体风格、语言与长度约束等），决定哪些媒体会触发报道、报道内容的叙事重心与写作风格，并调用 LLM 生成最终稿件。

## 核心入口

- `news_generation_engine.py` 中的 `NewsGenerationEngine`
  - 读取并加载新闻画像 CSV
  - `simulate_news(event_text)`：返回本次事件下的报道列表（每家媒体一条或不报道）

## 画像字段与实现对应关系

- 触发逻辑（是否报道）
  - `sci_activity_level`：用于设置触发阈值
  - 低活跃媒体会在事件与媒体 `country`（或其主称）强相关时才触发
  - `sci_activity_level` 也用于计算“首发/转载”的时间延迟 `delay_seconds`

- 叙事重心（报道什么）
  - `sci_weight_frontier / sci_weight_security / sci_weight_infrastructure / sci_weight_collab`
  - 在 Prompt 中以“权重→关键词与段落要求”的方式分配叙事重点

- 基调与风格（怎么写）
  - `sci_report_style`：映射到写作风格模板（如 `Grand_Official`、`Analytical_Critical`）
  - `primary_report_lang`：强制输出语言
  - Prompt 注入 `ownership_type` 与 `region`

- 文本结构与长度（写多深）
  - `sci_word_count_range`：解析为输出长度目标，并限制 LLM 输出上限（通过 `max_tokens` 近似）

## 与系统对接

- 在 `src/modules/api.py` 中新增路由（例如 `POST /simulate/news`），并与媒体提问模块同入口启动。

## 对外接口与返回结构

- 端点：`POST /simulate/news`
  - 请求体：`{ "event_text": "..." }`（与媒体提问一致，事件描述不能为空或仅为空白）
- 返回（统一结构）
  - 成功：`{ "status": "success", "data": [...], "meta": { "count", "endpoint" } }`
  - 失败：`{ "status": "error", "error": { "code", "message", "reason" } }`

`data[]` 内每条报道的字段（来自引擎生成）：
- `media_id`
- `media_name`
- `country`
- `behavior_tag`: 固定为 `媒体报道`
- `report_type`: `首发` 或 `转载`（按时效延迟排序后确定）
- `delay_seconds`: 模拟延迟参考（未实际 sleep，仅用于排序/展示）
- `content`: LLM 生成的报道正文

常见错误码：
- `VALIDATION_ERROR`（422）
- `DATA_FILE_MISSING` / `DATA_READ_FAILED`（503）
- `LLM_UNAVAILABLE`（503：全部供应商均失败）
- `SIMULATION_FAILED`（500）

## 落地总结（对应你的四个核心逻辑）

1. **触发逻辑（是否报道）**
   - 使用 `sci_activity_level` 设定“高活跃阈值”；高活跃直接触发。
   - 低活跃需要事件文本与媒体 `country`（主称）/`region` 强相关才触发。
   - 同时用活跃度生成 `delay_seconds`，并按延迟排序确定 `首发/转载`。
2. **叙事重心逻辑（报道什么）**
   - 依据四个子领域权重（frontier/security/infrastructure/collab）在 Prompt 里显式写出关键词约束与段落展开建议。
3. **基调与风格约束（怎么写）**
   - 直接使用 `sci_report_style` 映射到 Prompt 风格描述。
   - 使用 `primary_report_lang` 强制输出语言。
4. **文本结构约束（写多深）**
   - 解析 `sci_word_count_range` 得到目标范围，并把 `word_max` 近似映射为 `max_tokens` 上限（与 LLM API 的长度控制联动）。
   - Prompt 中必须注入该媒体的 `ownership_type` 与 `region`，并要求其影响措辞与关注点。


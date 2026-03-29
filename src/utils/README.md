# 工具文件说明
> 可重复使用的功能性代码，包括数据处理（json->csv、向上泛化到科技类）

## [media_processor.py](src\utils\media_processor.py)
- **功能概述**
  - 将 `media_profiles.json` 中的媒体画像数据进行扁平化与清洗。
  - 将同一份原始数据拆分为两个实验数据集 `data\processed\`：
    - 媒体提问动态数据（Press Conference 侧）
    - 媒体报道动态数据（News & Social 侧）

- **输入**
  - `input_json`：原始媒体画像 JSON 文件，默认：
    - `data\raw\media_profiles.json`
  - 数据结构要求（核心）：
    - 顶层为 `media_id -> content` 的映射
    - `content.static_profile`：静态属性
    - `content.behavior_dynamic`：动态行为属性（可嵌套）

- **输出**
  - `output_inquiring`（默认）：
    - `data\processed\media_inquiring_dynamic.csv`
    - 包含静态核心字段 + 提问相关动态字段
  - `output_news`（默认）：
    - `data\processed\media_news_dynamic.csv`
    - 包含静态核心字段 + 报道/社媒相关动态字段

- **处理过程**
  1. 读取 JSON  
     使用 `json.load` 加载媒体画像原始数据。
  2. 展平动态字段  
     通过 `flatten_dict()` 递归展开 `behavior_dynamic`，将嵌套结构变为路径式列名（用 `_` 连接）。
     - 普通列表：转为逗号分隔字符串
     - `history` 列表：提取最后一条记录的 `value`，写入 `*_latest_value`
  3. 合并静态+动态  
     将 `static_profile` 与展平后的动态字段合并为单行，累计成表。
  4. 清洗与补全  
     - 所有 `topic_focus` 相关列缺失值填充为 `0`
     - 确保静态字段存在：`media_id/media_name/country/region/ownership_type`
       - 若缺失则补为 `"Unknown"`
  5. 按用途拆分数据集  
     - 提问动态：筛选列名含 `press_conference` 或 `consistency`
     - 报道动态：筛选列名含 `news_reports` 或 `social_metrics`
     - 两者均保留核心静态列（含 `is_press_conference_regular`）
  6. 导出 CSV  
     使用 `utf-8-sig` 编码保存，便于中文环境（如 Excel）打开。


## [media_upward_generalization.py](src\utils\media_upward_generalization.py)
- **功能概述**
  - 将 `data\processed\media_science_inquiring_dynamic.csv` 中与航天提问相关的特征，上升泛化为“通用科学传播画像”。
  - 生成用于后续分析/建模的精简特征表，输出到 `data\processed\media_science_generalized.csv`。

- **输入**
  - `input_path`（默认）：
    - `../../data/processed/media_science_inquiring_dynamic.csv`
  - 主要依赖字段：
    - 航天话题关注度列（5个 `press_conference_topic_focus_Science_航空航天_*` 列）
    - 提问意图结构列（`press_conference_question_intent_focus_structure_*`）
    - 核心静态列（`media_id/media_name/country/ownership_type`）

- **输出**
  - `output_path`（默认）：
    - `../../data/processed/media_science_inquiring_generalized.csv`
  - 输出字段由三部分构成：
    - 核心静态字段：`media_id/media_name/country/ownership_type`
    - 科学泛化指标：`sci_interest_breadth/sci_specialization/sci_dominant_tag`
    - 通用意图字段：`intent_*`（由原始提问意图字段重命名而来）

- **处理过程**
  1. 读取输入 CSV  
     使用 `pandas.read_csv` 载入媒体提问动态数据。
  2. 计算科学关注广度 `sci_interest_breadth`  
     对 5 个航天话题列判断是否大于 0，统计非零话题数并除以 5。
  3. 计算科学特化度 `sci_specialization`  
     对 5 个航天话题列按行计算标准差（离散程度越大，特化倾向越明显）。
  4. 提取主导科学标签 `sci_dominant_tag`  
     - 取 5 个话题列中最大值对应列（`idxmax`）
     - 通过 `topic_map` 映射为通用标签（如 `Frontier_Exploration` 等）
     - 若 5 列之和为 0，则标为 `Universal_Reporter`
  5. 意图字段泛化重命名  
     将场景化字段 `press_conference_question_intent_focus_structure_*` 重命名为通用 `intent_*` 字段（如 `intent_risk_assessment`）。
     包括如下字段：
      - `intent_agenda_setting`:议程设置意图，数值高的Agent关注“下一步要做什么”
      - `intent_fact_checking`:事实核查意图，该数值高的Agent不容易被宏大叙事忽悠，反映了媒体的“技术硬度”
      - `intent_diplomacy_collab`:外交与协作意向，衡量媒体对该事件在“地缘政治”与“国际合作”框架下的关注度，决定了Agent是否会问“该科学发现对中欧合作有何影响”或者“是否会排斥特定国家参与”
      - `intent_social_impact`:社会影响评估，将纯粹的科学事实转化为价值判断，高权重的Agent会将科技进步解读为“人类福祉”或“社会变革”
      - `intent_causal_logic`:因果逻辑挖掘，代表媒体的“深度报道倾向”，Agent可能会追溯“为什么中国能做到这一点？”或“这一突破背后的政策驱动力是什么？”
      - `intent_risk_assessment`:风险评估/防御性视角，该数值高可能会在模拟中扮演“反对者”或“质疑者”,专门挖掘技术的双刃剑效应、伦理危机或安全漏洞
  6. 选择最终字段并导出  
     拼接核心静态字段 + 3 个科学指标 + 意图字段，保存为 `utf-8-sig` 编码 CSV。

## [llm_client.py](src\utils\llm_client.py)
- **功能概述**
  - 提供统一的 LLM 调用客户端，封装对 `OpenAI Chat Completions` 接口的访问。
  - 通过系统提示词和用户提示词输入，生成媒体 Agent 的文本输出（如提问内容）。

- **输入**
  - `system_prompt`：系统级角色设定与行为约束。
  - `user_prompt`：当前任务或事件描述。
  - 配置来源：`configs/llm_settings.py` 中的 `LLM_CONFIG`（`api_key/base_url/model_name/temperature/max_tokens`）。

- **输出**
  - 成功时返回模型生成的字符串结果（去除首尾空白）。
  - 失败时返回兜底提示：`提问生成失败，请检查网络或API配置。`

- **处理过程**
  1. 初始化 `LLMClient`  
     使用 `LLM_CONFIG` 创建 `openai.OpenAI` 客户端并设置默认模型名。
  2. 调用 `ask(system_prompt, user_prompt)`  
     发送 `system + user` 双消息到 `chat.completions.create`。
  3. 参数控制  
     推理参数使用配置中的 `temperature` 与 `max_tokens`。
  4. 结果返回与异常处理  
     - 正常：返回第一条候选回复文本  
     - 异常：打印错误并返回固定失败提示
  5. 全局实例  
     文件末尾实例化 `llm_client = LLMClient()`，方便其他模块直接复用。

## [netizen_science_upward_generalization.py](src\utils\netizen_science_upward_generalization.py)
- **功能概述**
  - 面向**网民画像**（Excel 原始表），将多个科技领域文件**字段对齐**并合并为一套**标准列结构**，实现“向上泛化”后的统一网民画像库。
  - 与 `media_upward_generalization.py`（媒体侧 CSV）不同：本脚本读 **`.xlsx`**，按领域配置批量处理。

- **输入**
  - 函数参数 `file_configs`：`{ 领域名: xlsx 路径 }` 字典；领域名会写入标准字段 `interest_domain`。
  - 脚本内默认配置（相对 `src/utils/`）示例：
    - `health` → `../../data/raw/netizen_tech_health_profile.xlsx`
    - `aerospace` → `../../data/raw/netizen_tech_aerospace_profile.xlsx`
    - `ai` → `../../data/raw/netizen_tech_ai_profile.xlsx`
    - `data` → `../../data/raw/netizen_tech_data_profile.xlsx`
  - 原始表需能通过列名映射或分支逻辑导出标准字段；常见源列包括：`Handle`、`Location`、`Language`、`FollowersCount`、`Daily_Post_Rate`、`Influence_Score`、`Bot_Score`、`Tone_Emotional_Score`、`Strategy_Label`、`Interest_Entropy` 等（详见脚本内 `mapping` 与条件分支）。

- **输出**
  - 默认保存：`../../data/processed/netizen_standardized_profiles.csv`（`utf-8-sig`）。
  - 标准列（`standard_schema`）：`handle`、`location`、`language`、`followers`、`daily_activeness`、`influence_index`、`bot_probability`、`tech_stance_score`、`emotion_intensity`、`strategy_type`、`interest_domain`、`is_verified`、`propagation_speed`、`cognitive_entropy`。

- **处理过程**
  1. 按领域遍历 `file_configs`，用 `pandas.read_excel` 读取每个 xlsx。
  2. **立场数值化** `tech_stance_score`：优先 `Stance_Numeric`；否则将 `Stance` 文本映射为 ±1/0；都没有则填 0。
  3. **认证** `is_verified`：来自 `Is_Blue` 或 `Verified` 布尔列，映射为 0/1；缺失则 0。
  4. **传播速度** `propagation_speed`：优先 `RT_Ratio`，否则 `Sample_Avg_Retweet`，否则用 `Influence_Score * 0.1` 近似。
  5. 按 `mapping` 重命名列，并设置 `interest_domain` 为当前领域键名。
  6. 仅保留 `standard_schema` 列（缺失列以 NaN 补齐），纵向合并全部领域。
  7. 对部分字段做缺失填充：`location`→`Global`，`strategy_type`→`Generalist`，`language`→`en`。
  8. `__main__` 中写出 CSV 并打印行数与列名；异常时打印错误信息。

# AgiComm 社会传播仿真系统 - 完整架构分析

## 📋 文档概述

本文档从 API 入口点 `@app.post("/simulate/social")` 出发，全面分析社会传播仿真模块的：

- **调用关系链**：从请求到响应的完整数据流
- **模块功能**：各个文件实现的核心功能
- **架构设计**：规则驱动 + LLM 语义增强的混合架构

---

## 🔄 调用链路 - 从 API 到仿真完成

```
HTTP POST /simulate/social
    ↓
[api.py] @app.post("/simulate/social")
    ↓
[social_simulation_api.py] run_social_simulation(request, data_path)
    ├─→ [data_loader.py] load_agents_from_csv()
    │   └─→ 返回: List[UserAgent]
    │
    ├─→ [agent.py] UserAgent.__init__()
    │   └─→ 初始化 Agent 属性（立场、情感、活跃度等）
    │
    ├─→ [network_builder.py] build_network(agents)
    │   └─→ 返回: NetworkX DiGraph (社交网络)
    │
    ├─→ [simulator.py] Simulator.__init__(enable_llm)
    │   ├─→ [semantic_engine.py] SemanticEngine(enable_llm)
    │   ├─→ [sentiment_analyzer.py] SentimentAnalyzer()
    │   ├─→ [recommendation_engine.py] RecommendationEngine()
    │   └─→ [llm_generator.py] LLMGenerator(enable_llm) [可选]
    │
    ├─→ [event_generator.py] EventGenerator.generate_custom_event()
    │   └─→ 返回: Message (初始事件)
    │
    ├─→ [simulator.py] Simulator.run_simulation()
    │   └─→ 仿真核心循环 (max_steps)
    │       ├─→ [exposure_model.py] compute_exposure_prob()
    │       │   └─→ 计算 Agent 接触信息的概率
    │       │
    │       ├─→ [semantic_engine.py] SemanticEngine.process()
    │       │   ├─→ RuleDecisionLayer.decide_action()
    │       │   │   └─→ 纯规则决策：repost/comment/ignore
    │       │   │
    │       │   ├─→ [llm_generator.py] LLMGenerator.generate_forward_text()
    │       │   │   └─→ LLM 生成文本或规则模板回退
    │       │   │
    │       │   └─→ 返回: semantic_result (action, text, scores)
    │       │
    │       ├─→ [message.py] Message.clone_with_modifications()
    │       │   └─→ 创建新 Message 副本，传播深度 +1
    │       │
    │       ├─→ [llm_generator.py] compute_semantic_quality()
    │       │   └─→ 计算文本语义质量 [0, 1]
    │       │
    │       ├─→ [llm_generator.py] compute_controversy_score()
    │       │   └─→ 计算争议性指数 [0, 1]
    │       │
    │       ├─→ [propagation_model.py] compute_propagation_prob()
    │       │   ├─→ 纳入语义质量权重
    │       │   ├─→ 纳入争议性权重
    │       │   ├─→ 纳入社群因子、疲劳因子、国际化因子
    │       │   └─→ 返回: 最终传播概率
    │       │
    │       ├─→ [recommendation_engine.py] RecommendationEngine.get_recommendations()
    │       │   └─→ 推荐引擎传播路径
    │       │
    │       ├─→ [sentiment_analyzer.py] SentimentAnalyzer.update_agent_state()
    │       │   └─→ 更新 Agent 情感/立场/疲劳
    │       │
    │       └─→ [metrics.py] calculate_metrics()
    │           └─→ 汇总仿真指标
    │
    └─→ 返回: SimulationResponse(status, data, meta)
        └─→ JSON 响应给前端
```

---

## 📁 模块详细功能说明

### 1. **api.py** - API 层入口

**位置**: `src/modules/api.py`

**核心功能**:

- 提供 HTTP 路由 `@app.post("/simulate/social")`
- 请求参数验证和转换
- 调用 `run_social_simulation()` 执行仿真
- 返回 JSON 响应

**关键代码段**:

```python
@app.post("/simulate/social")
async def social_propagation_simulation(request: SocialSimulationRequest):
    # 数据文件检查
    # 运行仿真
    response = run_social_simulation(sim_request, data_path)
    # 返回结果
```

**依赖**:

- `social_simulation_api.py::run_social_simulation`

---

### 2. **social_simulation_api.py** - 仿真协调器

**位置**: `src/modules/social_simulation/social_simulation_api.py`

**核心功能**:

- **主函数 `run_social_simulation()`**: 仿真的总体协调逻辑
  1. 加载 Agent 数据
  2. 按情感/立场/影响力筛选
  3. 构建社交网络
  4. 创建 Simulator 实例
  5. 生成初始事件
  6. 选择种子节点
  7. 运行仿真
  8. 计算指标
  9. 返回结果

- **参数**:
  - `event_text`: 事件描述
  - `event_emotion`: 事件情感 [0, 1]
  - `event_stance`: 事件立场 [-1, 1]
  - `num_seeds`: 种子数量
  - `seed_strategy`: "influence" | "emotion" | "random"
  - `max_steps`: 仿真步数
  - `enable_llm`: 是否启用 LLM

**依赖**:

- `data_loader.py::load_agents_from_csv`
- `network_builder.py::build_network`
- `simulator.py::Simulator`
- `event_generator.py::EventGenerator`
- `metrics.py::calculate_metrics`

---

### 3. **simulator.py** - 仿真引擎核心

**位置**: `src/modules/social_simulation/simulator.py`

**核心功能**:

- 主方法 `run_simulation()`: 执行 max_steps 轮仿真循环
  - **每一步**:
    1. 遍历消息队列
    2. 对每条消息，获取其源节点的邻接节点
    3. 计算每个邻接节点的曝光概率
    4. 调用语义引擎决策是否转发/评论/忽略
    5. 若传播，创建新 Message 副本
    6. 计算语义质量和争议性
    7. 调用传播模型计算最终传播概率
    8. 更新 Agent 状态（情感、立场、疲劳）
    9. 处理推荐引擎的传播路径

- **初始化参数**:
  - `enable_llm`: 启用 LLM 生成层

- **关键属性**:
  - `semantic_engine`: 语义决策引擎
  - `sentiment_analyzer`: 情感分析器
  - `recommendation_engine`: 推荐引擎
  - `llm_generator`: LLM 文本生成器（可选）

**依赖**:

- `semantic_engine.py::SemanticEngine`
- `sentiment_analyzer.py::SentimentAnalyzer`
- `propagation_model.py::compute_propagation_prob`
- `exposure_model.py::compute_exposure_prob`
- `recommendation_engine.py::RecommendationEngine`
- `message.py::Message`

---

### 4. **semantic_engine.py** - 规则决策 + LLM 生成层

**位置**: `src/modules/social_simulation/semantic_engine.py`

**架构**: 分离规则和 LLM

```
SemanticEngine (统一入口)
├─→ RuleDecisionLayer (纯规则，无LLM)
│   ├─→ decide_action()
│   ├─→ compute_emotion_shift()
│   ├─→ compute_stance_shift()
│   ├─→ compute_international_penalty()
│   └─→ compute_memory_bias()
│
└─→ LLMGenerationLayer (文本生成，见 llm_generator.py)
```

**核心功能**:

#### **RuleDecisionLayer** - 纯规则决策

- **`decide_action(agent_stance, message_stance, ...)`**: 决定传播行为
  - 输入: Agent 立场/情感、Message 立场/情感、Agent 活跃度、Bot概率、记忆奖励
  - 规则: `score = 0.4*stance_sim + 0.3*emotion + 0.2*activeness + 0.1*memory`
  - 输出: action ∈ {"repost", "comment", "ignore"}, semantic_score ∈ [0, 1]

- **`compute_emotion_shift(agent_emotion, message_emotion, action)`**:
  - 转发: emotion_shift = (msg_emotion - agent_emotion) × 0.5
  - 评论: emotion_shift = (msg_emotion - agent_emotion) × 0.2
  - 忽略: emotion_shift = 0

- **`compute_stance_shift(agent_stance, message_stance, action)`**:
  - 转发: stance_shift = (msg_stance - agent_stance) × 0.3
  - 评论: stance_shift = (msg_stance - agent_stance) × 0.1

- **`compute_international_penalty(agent, message)`**: 国际化惩罚
  - 不同国家: -0.2
  - 不同语言: -0.15
  - 最大惩罚: -0.4

- **`compute_memory_bias(agent, message)`**: 记忆驱动奖励
  - 每条匹配的记忆条目: +0.02
  - 最大奖励: +0.2

#### **SemanticEngine** - 统一入口

- **`process(agent, message, semantic_result_cache=None)`**:
  1. 调用 `_rule_decision()` → RuleDecisionLayer.decide_action()
  2. 调用 `_generate_text()` → LLMGenerator.generate\_\*\_text()
  3. 返回: `{"should_forward": bool, "action": str, "emotion_shift": float, "stance_shift": float, "generated_text": str, "semantic_score": float}`

**依赖**:

- `llm_generator.py::LLMGenerator` (可选)
- `message.py::Message`

---

### 5. **llm_generator.py** - LLM 文本生成层

**位置**: `src/modules/social_simulation/llm_generator.py`

**核心功能**:

#### **文本生成**

- **`generate_forward_text(agent, message, use_llm=None)`**:
  - 尝试 LLM 生成 或 规则模板
  - LRU 缓存支持（避免重复计算）

- **`generate_comment(agent, message, use_llm=None)`**:
  - 结合 `_get_recent_stance_views()` 保证意见一致性
  - 从 Agent 记忆中提取最近3条观点，确保评论的一致性

#### **语义质量计算**

- **`compute_semantic_quality(generated_text, agent, message)`**:
  - 长度奖励: 20-200 字符 → +0.2
  - 多样性奖励: 独特词汇 > 5 → +0.15
  - 立场一致性: 立场差异 < 0.5 → +0.15
  - 返回: [0.5, 1.0]

#### **争议性计算**

- **`compute_controversy_score(generated_text, message)`**:
  - 情感强度贡献: +0.2 × emotion
  - 立场极端性: |stance| > 0.7 → +0.2
  - 文本长度: > 100 字符 → +0.1
  - 返回: [0.5, 1.0]

#### **文化/多语言支持**

- **CULTURE_TEMPLATES**: 按国家/语言定制表达
  ```python
  {
    "CN": {"repost_prefix": ["转发", "分享", "同意观点"], ...},
    "US": {"repost_prefix": ["Reposting", "Sharing", "I agree"], ...},
    "DE": {...}, "FR": {...}
  }
  ```

#### **缓存机制**

- LRU 缓存 (大小可配: `SimulationConfig.LLM_CACHE_SIZE`)
- 缓存键: `"forward_{agent_id}_{message_id}"` 或 `"comment_{agent_id}_{message_id}"`
- 缓存统计: `get_cache_stats()` → hit rate, size, hits/misses

**依赖**:

- `llm_client.py::llm_client` (可选)
- `simulation_config.py::SimulationConfig`
- `message.py::Message`

---

### 6. **message.py** - 文本传播对象

**位置**: `src/modules/social_simulation/message.py`

**核心功能**:

#### **Message 类属性**

```python
Message(
    content: str,           # 消息内容
    emotion: float,         # 情感 [0, 1]
    stance: float,          # 立场 [-1, 1]
    source_id: str,         # 源Agent ID
    narrative_type: str,    # 叙事类型
    origin_country: str,    # 来源国家
    language: str,          # 语言
    propagation_depth: int, # 传播深度
    semantic_quality: float,       # 文本语义质量 [0, 1] ✨ 新增
    controversy_score: float,      # 争议性指数 [0, 1] ✨ 新增
    emotional_intensity: float     # 情绪强度 [0, 1] ✨ 新增
)
```

#### **关键方法**

- **`clone_with_modifications(new_emotion, new_stance, new_content, ...)`**:
  - 创建 Message 副本，传播深度 +1
  - 语义质量衰减: `semantic_quality *= 0.95`
  - 争议性衰减: `controversy_score *= 0.9`
  - 保留叙事类型和国际化信息

- **`to_dict()`**: 序列化为字典
  - 包含所有属性（包括新增的语义属性）

**依赖**:

- `datetime`

---

### 7. **propagation_model.py** - 传播概率模型

**位置**: `src/modules/social_simulation/propagation_model.py`

**核心功能**:

#### **传播概率计算**

- **`compute_propagation_prob(agent_i, message, semantic_result=None)`**:
  ```
  P_base = sigmoid(0.2*A + 0.25*I + 0.2*E + 0.2*S - 0.15*B)
    × semantic_score (来自RuleDecisionLayer)
    × action_multiplier (repost=1.0, comment=0.6)
    × community_factor (同社群=1.2, 异社群=0.85)
    × fatigue_factor ([0.2, 1.0])
    × attention_factor ([0.3, 1.0])
    × international_factor ([0.7, 1.0])
    × competition_penalty ([0.5, 1.0])
    × semantic_quality_factor ([0.8, 1.2])  ✨ 新增
    × controversy_factor ([0.9, 1.2])       ✨ 新增
  ```

#### **新增权重因子**

- **`_semantic_quality_factor(message)`**:
  - 返回: 0.8 + semantic_quality × 0.4 = [0.8, 1.2]
  - 高质量文本传播增益

- **`_controversy_factor(message)`**:
  - 返回: 0.9 + controversy_score × 0.3 = [0.9, 1.2]
  - 争议性话题更容易传播

#### **其他因子**

- `sigmoid(x)`: Logistic 激活函数
- `stance_similarity()`: 立场相似度 [0, 1]
- `_community_factor()`: 社群内/外传播系数
- `_fatigue_factor()`: Agent 疲劳衰减
- `_attention_factor()`: 注意力容量衰减
- `_international_factor()`: 国际化衰减
- `_competition_penalty()`: 信息竞争惩罚

**依赖**:

- `math`

---

### 8. **exposure_model.py** - 曝光模型

**位置**: `src/modules/social_simulation/exposure_model.py`

**核心功能**:

- **`compute_exposure_prob(agent, message, context=None)`**:
  - 计算 Agent 接触信息的概率
  - 输入加权: 0.25×activeness + 0.25×interest_match + 0.2×relationship + 0.2×hotness + 0.1×platform
  - 乘以时区因子
  - 返回: [0, 1]

**作用**: 在决策层之前，先判断 Agent 是否能接触到信息

**依赖**:

- `propagation_model.py::stance_similarity`

---

### 9. **recommendation_engine.py** - 推荐引擎

**位置**: `src/modules/social_simulation/recommendation_engine.py`

**核心功能**:

- **`get_recommendations(agent, target_agents, message, top_k=4)`**:
  - 基于 Agent 特征，推荐目标接收者
  - 考虑: 关系强度、平台权重、时区
  - 返回: top_k 个推荐的 Agent

**作用**: 提供除邻接关系外的额外传播路径（平台算法推荐）

---

### 10. **sentiment_analyzer.py** - 情感分析与状态更新

**位置**: `src/modules/social_simulation/sentiment_analyzer.py`

**核心功能**:

- **`update_agent_state(agent, message, action, emotion_shift, stance_shift)`**:
  - 根据 Agent 的传播行为，更新其内部状态
  - 更新: emotion, stance, fatigue, memory
  - 情感变化: agent.emotion += emotion_shift
  - 立场变化: agent.stance += stance_shift
  - 疲劳增加: agent.fatigue += fatigue_increment

**作用**: 实现 Agent 的动态演化

---

### 11. **network_builder.py** - 社交网络构建

**位置**: `src/modules/social_simulation/network_builder.py`

**核心功能**:

- **`build_network(agents, community_capacity=4)`**:
  1. 按国家/社群分组 Agent
  2. 构建社区内强链接 (followers / 120)
  3. 构建社区间弱链接 (followers / 300, 概率35%)
  4. 构建社区桥接 (不同社群的影响力用户连接)
  5. 返回: NetworkX DiGraph

**网络特点**:

- 社群化结构（国家/社群）
- 幂律分布（高影响力用户连接更多）
- 跨社群低概率连接

**依赖**:

- `networkx`

---

### 12. **agent.py** - Agent 数据对象

**位置**: `src/modules/social_simulation/agent.py`

**核心功能**:

- **`UserAgent` 类**:
  - 从 CSV 数据行初始化
  - 属性:
    - **传播属性**: followers, activeness, influence, bot_prob, speed
    - **观点属性**: stance, emotion, entropy
    - **身份属性**: country, language, ideology, culture_bias, community_id
    - **状态属性**: fatigue, attention_capacity, current_attention
    - **历史记录**: exposure_history, memory, trust_history, interaction_history
    - **时间属性**: timezone_offset, active_time_distribution

**依赖**:

- `agent.py::data_loader` 提供 CSV 加载

---

### 13. **event_generator.py** - 初始事件生成

**位置**: `src/modules/social_simulation/event_generator.py`

**核心功能**:

- **`EventGenerator` 类**:
  - 预定义事件类型: tech_positive, tech_negative, tech_neutral, social_hotspot, science_breakthrough, controversial_opinion
  - **`generate_custom_event(content, emotion, stance, source_id)`**:
    - 根据参数创建初始 Message
  - **`generate_event(event_type, source_id)`**:
    - 从预设模板随机生成事件

**依赖**:

- `message.py::Message`

---

### 14. **metrics.py** - 指标计算

**位置**: `src/modules/social_simulation/metrics.py`

**核心功能**:

- **`calculate_metrics(history, agents, active_nodes, detailed_metrics)`**:
  返回指标包括:
  - **覆盖指标**: coverage_rate, final_size, steps_to_reach
  - **增长指标**: growth_rates, avg_growth_rate, max_growth_rate
  - **情感指标**: active_emotion_mean, active_emotion_std, active_emotion_max/min, inactive_emotion_mean
  - **立场指标**: active_stance_mean, active_stance_var, active_stance_std, polarization_index, stance_divergence
  - **深度指标**: propagation_depth

**依赖**:

- `numpy`

---

### 15. **simulation_config.py** - 仿真配置（Task 8）

**位置**: `src/modules/social_simulation/simulation_config.py`

**核心功能**:

#### **SimulationConfig 类**

- **配置参数**: ~25 个可调参数，覆盖:
  - 传播机制 (STANCE_SIMILARITY_THRESHOLD, EMOTION_COMMENT_THRESHOLD, ...)
  - 状态变化 (EMOTION_SHIFT_REPOST, STANCE_SHIFT_REPOST, ...)
  - 国际化 (INTERNATIONAL_PENALTY_COUNTRY, ...)
  - 社群/疲劳/记忆/竞争/语义/争议/LLM/性能参数
- **方法**:
  - `set_seed(seed)`: 设置随机种子，保证可复现
  - `update_from_dict(config_dict)`: 从字典更新
  - `to_dict()`: 导出为字典
  - `load_from_file(config_file)`: 从 JSON 加载
  - `save_to_file(config_file)`: 保存到 JSON

#### **ExperimentConfig 类**

- `get_rule_only_config()`: 纯规则模式
- `get_hybrid_config()`: 混合模式（推荐）
- `get_llm_only_config()`: LLM 模式
- `create_ab_test_configs()`: 创建 A/B 测试配置

**依赖**:

- `random`, `json`, `os`

---

### 16. **data_loader.py** - 数据加载

**位置**: `src/modules/social_simulation/data_loader.py`

**核心功能**:

- **`load_agents_from_csv(csv_path)`**:
  - 从 CSV 文件加载 Agent 数据
  - 返回: List[UserAgent]

---

## 🏗️ 总体架构设计

### 系统分层

```
┌─────────────────────────────────────────┐
│        FastAPI HTTP 层                   │
│     (@app.post("/simulate/social"))     │
└────────────┬────────────────────────────┘
             │
┌────────────▼────────────────────────────┐
│      仿真协调层                          │
│  (social_simulation_api.py)             │
│  - 加载数据                              │
│  - 筛选用户                              │
│  - 初始化仿真器                          │
│  - 选择种子                              │
│  - 计算指标                              │
└────────────┬────────────────────────────┘
             │
┌────────────▼────────────────────────────┐
│      仿真核心层                          │
│  (simulator.py)                         │
│  - 仿真循环                              │
│  - 消息传播                              │
│  - Agent 状态更新                        │
└────────────┬────────────────────────────┘
             │
   ┌─────────┴──────────┬─────────────────┐
   │                    │                 │
┌──▼──────────┐  ┌─────▼───────┐  ┌─────▼──────┐
│ 决策层       │  │ 生成层      │  │ 概率模型   │
│semantic_    │  │llm_generator│  │propagation_│
│engine.py    │  │.py          │  │model.py    │
│             │  │             │  │            │
│RuleDecision │  │·文本生成    │  │·语义质量   │
│Layer        │  │·缓存        │  │·争议性     │
│·决策动作    │  │·文化模板    │  │·社群因子   │
│·情感变化    │  │·语义质量    │  │·疲劳因子   │
│·立场变化    │  │·争议性      │  │·国际化     │
│·国际化惩罚  │  │            │  │            │
│·记忆奖励    │  │            │  │            │
└─────────────┘  └─────────────┘  └─────────────┘
```

### 规则 vs LLM 的职能分工

| 层级       | 模块              | 职能                   | LLM使用              |
| ---------- | ----------------- | ---------------------- | -------------------- |
| **决策层** | RuleDecisionLayer | 决定是否传播/转发/评论 | ❌ 纯规则            |
| **生成层** | LLMGenerator      | 生成文本表达           | ✅ 可选LLM，回退规则 |
| **概率层** | propagation_model | 计算最终传播概率       | ❌ 纯数学模型        |

**核心原则**: "规则负责传播逻辑，LLM负责语义表达"

---

## 🚀 当前传播仿真的总体实现功能

### 功能矩阵

| 功能维度           | 实现状态 | 详细说明                               |
| ------------------ | -------- | -------------------------------------- |
| **消息传播**       | ✅ 完整  | Message 对象传播、深度追踪、多路径传播 |
| **Agent 状态演化** | ✅ 完整  | 情感、立场、疲劳、注意力动态更新       |
| **社群结构**       | ✅ 完整  | 基于国家/社群的网络划分，社群内外差异  |
| **推荐引擎**       | ✅ 完整  | 平台算法推荐路径，非邻接传播           |
| **国际化支持**     | ✅ 完整  | 多国家、多语言、时区感知               |
| **记忆机制**       | ✅ 完整  | Agent 记忆驱动的意见一致性             |
| **语义质量**       | ✅ 完整  | 文本语义质量计算、衰减模型             |
| **争议性建模**     | ✅ 完整  | 争议性话题的传播增益                   |
| **LLM 文本生成**   | ✅ 完整  | 文化适配、缓存优化、回退规则           |
| **曝光模型**       | ✅ 完整  | Agent 接触信息的前置概率               |
| **指标计算**       | ✅ 完整  | 覆盖率、增长率、情感/立场分布          |
| **可复现性**       | ✅ 完整  | 种子设置、配置导入导出、实验模式       |
| **性能优化**       | ⏳ 部分  | LRU 缓存实现，异步框架就位             |
| **实验对照**       | ✅ 完整  | rule_only/hybrid/llm_only 模式         |

### 核心传播模式

#### **邻接传播**

```
Message 在网络中通过 Agent 的粉丝关系传播
Agent i 看到来自 Agent j (j ∈ neighbors of i) 的 Message
├─→ 曝光概率 = compute_exposure_prob()
├─→ 决策动作 = RuleDecisionLayer.decide_action()
├─→ 生成文本 = LLMGenerator.generate_text()
└─→ 传播概率 = compute_propagation_prob()
```

#### **推荐传播**

```
平台推荐系统将 Message 推荐给相关 Agent
├─→ 推荐候选 = RecommendationEngine.get_recommendations()
├─→ 曝光概率 = compute_exposure_prob() (+ 推荐权重)
└─→ 同邻接传播流程
```

#### **状态反馈**

```
Agent 的传播行为影响其内部状态
转发/评论 → Agent 的情感/立场/疲劳改变
    ↓
新状态 → 影响对后续消息的反应
    ↓
动态演化 → 整体舆论景观变化
```

### 时间尺度

- **单条消息**: 从源 Agent 出发，经过 max_steps 轮传播
- **单轮传播**: 同时处理所有当前消息的邻接和推荐传播
- **仿真总时长**: ~O(max_steps × avg_degree)

### 参数影响

| 参数                       | 范围                     | 影响                 |
| -------------------------- | ------------------------ | -------------------- |
| `num_seeds`                | 1-100                    | 初始覆盖             |
| `max_steps`                | 1-100                    | 传播深度/广度        |
| `enable_llm`               | True/False               | 文本生成质量         |
| `emotion_threshold`        | 0.0-1.0                  | Agent 选择           |
| `seed_strategy`            | influence/emotion/random | 种子多样性           |
| `SEMANTIC_QUALITY_MIN/MAX` | [0.8, 1.2]               | 语义对传播的增益幅度 |

---

## 📊 数据流示例

```
请求:
{
  "event_text": "某公司推出革命性新技术",
  "event_emotion": 0.8,
  "event_stance": 0.7,
  "num_seeds": 5,
  "max_steps": 10,
  "enable_llm": true
}
    ↓
加载 Agent (n=10000) → 筛选 (n=8000) → 构建网络 (edges=~50000)
    ↓
初始化 EventGenerator + Simulator
    ↓
生成初始 Message:
{
  id: "narrative_0_media_source_1234567890",
  content: "某公司推出革命性新技术",
  emotion: 0.8,
  stance: 0.7,
  semantic_quality: 0.5,
  controversy_score: 0.6,
  propagation_depth: 0
}
    ↓
选择 5 个种子 Agent (高影响力)
    ↓
第 1 步: 种子 Agent 转发消息
  ├─→ 150 个邻接 Agent 收到
  ├─→ 90 个 Agent 选择转发/评论
  ├─→ 生成 90 条新 Message (深度=1)
  └─→ 更新 Agent 状态 (emotion±0.1, stance±0.05, ...)

第 2-10 步: 递归传播
  └─→ 指数级增长，直到趋稳

最终结果:
{
  "coverage_rate": 0.35,        // 35% Agent 参与
  "active_nodes": 2800,          // 参与 Agent 数
  "metrics": {
    "avg_emotion": 0.72,         // 参与者平均情感上升
    "polarization": 0.18,        // 意见分化程度
    ...
  }
}
```

---

## 🔍 架构亮点

### 1. **规则与 LLM 的清晰分工**

- 决策逻辑完全由规则控制 → 可解释性高
- 文本生成由 LLM 处理 → 质量高、可定制
- 不会因 LLM 失败而影响传播逻辑

### 2. **多维度的状态空间**

- 每个 Agent 跟踪: 情感、立场、疲劳、注意力、记忆
- 每条 Message 跟踪: 语义质量、争议性、传播深度
- 支持细粒度的动态分析

### 3. **文化与语言的本土化**

- 基于国家代码的模板库
- 支持 CN, US, DE, FR 等多地区表达
- 自动回退到默认英文

### 4. **可复现的实验框架**

- SimulationConfig 统一管理所有参数
- 支持导入/导出配置 JSON
- 种子设置保证完全可复现
- A/B 测试支持

### 5. **性能优化就位**

- LRU 缓存减少重复计算
- 异步框架已嵌入（可扩展）
- 批量模式参数已预留

---

## 📝 总结

**社会传播仿真系统** 是一个多层次、参数可控、规则透明的复杂网络传播模型，具有以下核心特征：

| 维度         | 特征                                       |
| ------------ | ------------------------------------------ |
| **架构**     | 规则决策 + LLM 生成 + 概率模型三层分离     |
| **网络**     | 社群化、幂律分布、动态演化                 |
| **Agent**    | 多维状态（情感、立场、疲劳、记忆、注意力） |
| **消息**     | 具有语义质量和争议性权重                   |
| **国际化**   | 多国家、多语言、时区感知、文化适配         |
| **可复现性** | 完整参数配置、种子控制、模式选择           |

从 API 请求到仿真完成，系统通过 **社会协调→网络构建→消息传播→状态更新→指标计算** 的完整流程，实现了对真实社交媒体舆论扩散的建模和分析。

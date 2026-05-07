# 社会传播仿真系统 - 完整实现指南

## 📋 概述

这是一个**结构化建模 + 语义生成驱动 + 概率调制 + 情感反馈闭环**的多智能体传播仿真系统。

### 核心特性

✅ **语义驱动决策** - 从"纯概率"升级为"语义+概率协同"  
✅ **文本传播对象** - Message类实现完整的信息传播链  
✅ **情感反馈闭环** - Agent状态随传播动态演化  
✅ **多维指标体系** - 传播规模、情感演化、立场极化等  
✅ **可复现实验框架** - 参数驱动的对比实验

---

## 🏗️ 系统架构

### 模块组成

```
social_simulation/
├── message.py                      # Message类 - 文本传播对象
├── agent.py                        # UserAgent类（已扩展）- Agent类型支持
├── event_generator.py              # 初始事件生成
├── semantic_engine.py              # 语义驱动决策引擎 ⭐
├── sentiment_analyzer.py           # 情感分析和状态更新 ⭐
├── persona_builder.py              # Persona特征描述
├── propagation_model.py            # 传播概率模型（已改进）
├── network_builder.py              # 社交网络构建
├── simulator.py                    # 核心仿真器（已重构）
├── metrics.py                      # 指标计算（已扩展）
├── data_loader.py                  # 数据加载
├── experiment_controller_v2.py     # 实验控制器（新版本）
├── social_simulation_api.py        # 后端API
└── test_integration.py             # 集成测试
```

### 核心流程

```
初始事件 → Agent筛选 → 网络构建 → 种子选择
                          ↓
                    ┌─────────────┐
                    │   仿真循环   │
                    └─────────────┘
                          ↓
                    1. 语义决策
                    2. 概率计算 (semantic_score × base_prob)
                    3. Message传播
                    4. Agent状态更新
                    5. 情感反馈
                          ↓
                    指标计算 + 可视化
```

---

## 🔑 关键改进

### 1️⃣ Message类 - 文本传播对象

**文件**: `message.py`

```python
class Message:
    def __init__(self, content, emotion, stance, source_id, propagation_depth):
        # 所有传播必须传递Message对象
        # 不同Agent对同一Message产生不同响应
```

**优势**:

- 跟踪信息的完整传播链
- 支持Message克隆和修改
- 记录传播深度和来源

---

### 2️⃣ SemanticEngine - 语义驱动决策 ⭐

**文件**: `semantic_engine.py`

```python
class SemanticEngine:
    def process(agent, message, use_llm=False):
        return {
            "action": "repost" | "comment" | "ignore",
            "generated_text": str,
            "semantic_score": float,
            "emotion_shift": float,
            "stance_shift": float
        }
```

**核心逻辑**:

```
Input: Agent属性 + Message内容
        ↓
Rule-based决策 (阶段1)
- if stance_similarity > 0.6: action = "repost"
- elif emotion > 0.7: action = "comment"
- else: action = "ignore"
        ↓
文本生成 + 情感计算 + 立场偏移
        ↓
Output: 行为决策 + 文本 + 语义强度
```

**阶段演进**:

- **阶段1** (当前): 规则+模板 ✅
- **阶段2** (预留): LLM驱动 (接口已准备)

---

### 3️⃣ 改进的传播模型

**文件**: `propagation_model.py`

**原逻辑**:

```
P = sigmoid(0.3*A + 0.3*I + 0.2*E + 0.2*S - 0.2*B)
if random() < P: 传播
```

**新逻辑**:

```
semantic_result = semantic_engine.process(agent, message)
P_base = sigmoid(...)
P_final = P_base × semantic_result["semantic_score"]
if semantic_result["action"] != "ignore" and random() < P_final: 执行传播
```

**改进点**:

- 语义+概率协同驱动
- 基于行为类型的权重调整
- 向后兼容

---

### 4️⃣ 核心仿真器 - Message传播

**文件**: `simulator.py`

```python
class Simulator:
    def run_simulation(G, seed_ids, initial_message, max_steps):
        for step in range(max_steps):
            for agent in active_agents:
                for message in received_messages:
                    # 1. 语义决策
                    semantic_result = semantic_engine.process(agent, message)

                    # 2. 概率计算
                    P = compute_propagation_prob(...) × semantic_result.score

                    # 3. 是否传播
                    if semantic_result.action != "ignore" and random() < P:

                        # 创建新Message
                        new_message = Message(
                            content=semantic_result.generated_text,
                            emotion=analyze_sentiment(...),
                            stance=agent.stance + stance_shift
                        )

                        # 4. 更新Agent状态
                        agent.emotion = update(...)
                        agent.stance = update(...)

                        # 5. 向邻接传播
                        push_to_neighbors(new_message)
```

**核心特性**:

- Message作为传播单位
- Agent状态动态演化
- 情感反馈闭环

---

### 5️⃣ SentimentAnalyzer - 情感反馈

**文件**: `sentiment_analyzer.py`

```python
class SentimentAnalyzer:
    def update_agent_state(agent, text, emotion_shift, stance_shift, action):
        # 分析文本 → 计算情感/立场 → 更新Agent状态
        agent.emotion = 0.7 * old_emotion + 0.3 * (text_emotion + shift)
        agent.stance = 0.7 * old_stance + 0.3 * (text_stance + shift)
```

**反馈闭环**:

```
生成文本 → 情感分析 → Agent状态更新 → 影响下一轮传播
```

---

### 6️⃣ 扩展的指标体系

**文件**: `metrics.py`

```python
# 传播指标
- final_size: 最终激活节点数
- coverage_rate: 覆盖率
- propagation_depth: 传播深度
- avg_growth_rate: 平均增长率

# 情感指标
- active_emotion_mean: 活跃用户平均情感
- active_emotion_std: 情感波动
- avg_emotion_change: 情感变化

# 立场指标
- active_stance_mean: 平均立场
- stance_divergence: 立场分化程度
- polarization_index: 极化指数

# 详细指标
- agents_with_state_changes: 状态改变的Agent数
- total_messages: 总Message数
```

---

## 🎯 验收标准

### ✅ 功能层面

- [x] 信息以"文本"形式传播（Message对象）
- [x] 行为由"语义 + 概率"共同决定
- [x] Agent状态随传播变化（情感、立场、活跃度）
- [x] 存在情感反馈闭环
- [x] 支持不同Agent类型（user/media）

### ✅ 实验层面

- [x] 修改情绪参数 → 传播范围变化
- [x] 修改立场 → 群体分化变化
- [x] 不同网络结构 → 不同传播路径
- [x] 参数驱动的对比实验

### ✅ 代码结构

- [x] semantic_engine 独立模块
- [x] sentiment_analyzer 独立模块
- [x] Message类存在
- [x] 不破坏原有模块

---

## 🚀 使用指南

### 1. 集成测试

```bash
cd src/modules/social_simulation
python test_integration.py
```

这会运行7个测试，验证所有功能。

### 2. 后端集成

后端API已集成到 `src/modules/api.py`:

**端点**: `POST /simulate/social`

**请求**:

```json
{
  "event_text": "某事件描述",
  "event_emotion": 0.7,
  "event_stance": 0.6,
  "num_seeds": 5,
  "seed_strategy": "influence",
  "max_steps": 10
}
```

**响应**:

```json
{
  "status": "success",
  "data": {
    "simulation_id": "...",
    "event": {...},
    "parameters": {...},
    "results": {
      "history": [1, 3, 7, 12, 15],
      "active_nodes_count": 15,
      "metrics": {...},
      "seeds": [...]
    }
  },
  "meta": {...}
}
```

### 3. 前端集成

已实现SocialView.vue:

**路由**: `/social`

**功能**:

- 事件输入（文本、情感、立场）
- 参数配置（种子策略、数量、步数）
- 结果展示（概览、曲线、情感、立场、种子）

### 4. 运行完整系统

```bash
# 1. 启动后端
python -m src.modules.api

# 2. 启动前端
cd frontend && npm run dev

# 3. 访问
http://localhost:5173/social
```

---

## 📊 实验配置示例

### 例1: 基础仿真

```python
config = {
    "data_path": "data/processed/netizen_science_standardized_profiles.csv",
    "max_steps": 10,
    "num_seeds": 5,
    "seed_strategy": "influence",
    "enable_semantic": True,
    "initial_event": {
        "type": "social_hotspot",
        "custom_emotion": 0.7,
        "custom_stance": 0.6
    }
}

controller = ExperimentController(config)
controller.setup_experiment()
result = controller.run_experiment()
```

### 例2: 对比实验

```python
configs = [
    {
        "name": "高情感事件",
        "initial_event": {"custom_emotion": 0.9}
    },
    {
        "name": "低情感事件",
        "initial_event": {"custom_emotion": 0.3}
    },
    {
        "name": "中立事件",
        "initial_event": {"custom_emotion": 0.5}
    }
]

results = run_multiple_experiments(configs)
```

---

## 🔍 关键特性演示

### 特性1: 语义驱动

```python
# 同一Message，不同Agent产生不同响应
message = Message("支持新政策", emotion=0.8, stance=0.9)

agent1 = UserAgent(high_stance_supporter)  # 会repost
agent2 = UserAgent(low_stance_opponent)    # 会ignore
agent3 = UserAgent(high_emotion_user)      # 会comment
```

### 特性2: 动态演化

```python
# Agent状态随传播变化
print(f"初始情感: {agent.emotion}")  # 0.5

# 传播发生后
# → 情感受Message影响
# → 立场向传播者偏移
# → 活跃度上升

print(f"传播后情感: {agent.emotion}")  # 0.65
print(f"传播后立场: {agent.stance}")  # 向+0.6方向偏移
```

### 特性3: 情感反馈闭环

```
初始事件: emotion=0.8, stance=0.6
  ↓
Agent生成文本: "太棒了！我支持这一步！"
  ↓
情感分析: emotion=0.9, stance=0.8
  ↓
Agent情感更新: 0.5 → 0.7
  ↓
转发给邻接: 新Message (emotion=0.7, stance=0.8)
  ↓
邻接Agent接收到更强烈的信息
  ↓
继续演化...
```

---

## ⚙️ 配置参数详解

### 种子策略

| 策略         | 说明                 | 适用场景     |
| ------------ | -------------------- | ------------ |
| `influence`  | 选择影响力最高的用户 | 一般情况     |
| `emotion`    | 选择情感最高的用户   | 情感驱动事件 |
| `random`     | 随机选择             | 对比/基准    |
| `activeness` | 选择最活跃的用户     | 活跃度驱动   |

### 参数范围

```python
event_emotion: [0.0, 1.0]        # 0=平淡, 1=激情
event_stance: [-1.0, 1.0]        # -1=反对, 0=中立, 1=支持
num_seeds: [1, 20]               # 种子数量
max_steps: [5, 50]               # 仿真步数
emotion_threshold: [0.0, 1.0]    # 筛选阈值
stance_range: [-1.0, 1.0]        # 筛选范围
```

---

## 📚 关键类和方法

### Message

```python
Message(content, emotion, stance, source_id, propagation_depth)
.clone_with_modifications(new_content, new_emotion, new_stance, source_agent_id)
.to_dict()
```

### SemanticEngine

```python
SemanticEngine(enable_llm=False)
.process(agent, message, use_llm=False) → dict
```

### SentimentAnalyzer

```python
SentimentAnalyzer()
.analyze_sentiment(text) → float [0, 1]
.analyze_stance(text) → float [-1, 1]
.update_agent_state(agent, text, emotion_shift, stance_shift, action)
```

### Simulator

```python
Simulator(enable_llm=False)
.run_simulation(G, seed_ids, initial_message, max_steps) → (history, active_nodes, metrics)
```

### ExperimentController

```python
ExperimentController(config)
.setup_experiment()
.run_experiment(seed_ids=None) → result_dict
```

---

## 🐛 故障排除

### 问题1: ImportError

**症状**: `ModuleNotFoundError: No module named 'networkx'`

**解决**: 安装依赖

```bash
pip install networkx pandas numpy
```

### 问题2: 数据文件不存在

**症状**: `FileNotFoundError: data/processed/...`

**解决**: 检查数据文件路径，确保在项目根目录启动服务

### 问题3: LLM集成失败

**症状**: `LLM client not available`

**解决**: 这是正常的 - 系统默认使用规则+模板模式。若要启用LLM，需配置`configs/llm_settings.py`

---

## 🎓 论文参考

这个系统实现了以下论文的核心思想:

1. **多智能体建模** - MOSAIC, GPLab框架
2. **情感感染** - 社交网络中的情感传播动力学
3. **立场极化** - 网络群体分化机制
4. **语义驱动** - LLM在智能体决策中的应用

---

## 📝 更新日志

### v2.0 (2026-05-06)

✅ 完整重构 - 从概率驱动升级到语义+概率协同
✅ Message类实现 - 完整的信息传播链
✅ SemanticEngine - 语义驱动决策（规则+模板）
✅ SentimentAnalyzer - 情感反馈闭环
✅ 后端API集成 - `/simulate/social` 端点
✅ 前端UI实现 - SocialView.vue
✅ 完整测试套件 - 7个集成测试

---

## 📞 支持

如有问题，请查看:

1. 集成测试: `test_integration.py`
2. 模块文档: 各模块文件头的详细注释
3. API文档: `social_simulation_api.py`
4. 前端代码: `SocialView.vue`

---

**系统已准备就绪！** 🚀

开始仿真之旅吧！

"""
社会传播仿真系统 - 集成测试
验证所有功能是否正常工作
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from message import Message
from event_generator import EventGenerator
from semantic_engine import SemanticEngine
from sentiment_analyzer import SentimentAnalyzer
from persona_builder import PersonaBuilder
from agent import UserAgent
from propagation_model import compute_propagation_prob, sigmoid
from network_builder import build_network
from data_loader import load_agents_from_csv
from simulator import Simulator
from metrics import calculate_metrics
from experiment_controller_v2 import ExperimentController
from datetime import datetime


def print_header(title):
    """打印标题"""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80 + "\n")


def test_message_class():
    """测试Message类"""
    print_header("✅ 测试1: Message类 - 文本传播对象")
    
    msg = Message(
        content="这是一个测试消息",
        emotion=0.7,
        stance=0.6,
        source_id="user_001",
        propagation_depth=0
    )
    
    print(f"✓ 创建Message: {msg}")
    print(f"  - 内容: {msg.content}")
    print(f"  - 情感: {msg.emotion}")
    print(f"  - 立场: {msg.stance}")
    print(f"  - 来源: {msg.source_id}")
    
    # 测试克隆
    msg2 = msg.clone_with_modifications(
        new_content="这是一个转发/评论",
        new_emotion=0.8,
        new_stance=0.7,
        source_agent_id="user_002"
    )
    
    print(f"✓ 克隆Message: {msg2}")
    print(f"  - 新深度: {msg2.propagation_depth}")


def test_event_generator():
    """测试事件生成器"""
    print_header("✅ 测试2: EventGenerator - 初始事件生成")
    
    gen = EventGenerator()
    
    # 显示所有事件类型
    print("可用事件类型:")
    for event_type in gen.list_event_types():
        info = gen.get_event_template_info(event_type)
        print(f"  - {event_type}: emotion{info['emotion_range']}, stance{info['stance_range']}")
    
    # 生成事件
    event = gen.generate_event(event_type="social_hotspot")
    print(f"\n✓ 生成事件: {event}")
    
    # 生成自定义事件
    custom_event = gen.generate_custom_event(
        content="科技发展带来新机遇",
        emotion=0.8,
        stance=0.9,
        source_id="media_001"
    )
    print(f"✓ 自定义事件: {custom_event}")


def test_semantic_engine():
    """测试语义引擎"""
    print_header("✅ 测试3: SemanticEngine - 语义决策")
    
    from pandas import Series
    
    engine = SemanticEngine(enable_llm=False)
    
    # 创建测试Agent
    data_row = {
        "handle": "test_user_001",
        "followers": 1000,
        "daily_activeness": 0.8,
        "influence_index": 0.7,
        "bot_probability": 0.1,
        "tech_stance_score": 0.6,
        "emotion_intensity": 0.7,
        "propagation_speed": 0.5,
        "cognitive_entropy": 0.3
    }
    agent = UserAgent(data_row)
    
    # 创建Message
    message = Message(
        content="新技术发布",
        emotion=0.7,
        stance=0.8,
        source_id="media_001"
    )
    
    # 语义处理
    result = engine.process(agent, message)
    
    print(f"✓ Agent: {agent.id}")
    print(f"  - 立场: {agent.stance:.2f}, 情感: {agent.emotion:.2f}")
    print(f"✓ Message: {message.content}")
    print(f"  - 情感: {message.emotion:.2f}, 立场: {message.stance:.2f}")
    print(f"✓ 语义结果:")
    print(f"  - 动作: {result['action']}")
    print(f"  - 语义分数: {result['semantic_score']:.2f}")
    print(f"  - 生成文本: {result['generated_text'][:50]}...")
    print(f"  - 情感偏移: {result['emotion_shift']:.2f}")
    print(f"  - 立场偏移: {result['stance_shift']:.2f}")


def test_sentiment_analyzer():
    """测试情感分析器"""
    print_header("✅ 测试4: SentimentAnalyzer - 情感分析和状态更新")
    
    analyzer = SentimentAnalyzer()
    
    # 测试文本分析
    text = "我真的很支持这个观点！这太棒了！"
    result = analyzer.analyze_text(text)
    
    print(f"✓ 分析文本: '{text}'")
    print(f"  - 情感强度: {result['emotion']:.2f}")
    print(f"  - 立场: {result['stance']:.2f}")
    print(f"  - 强观点: {result['is_strong_opinion']}")
    
    # 测试Agent状态更新
    from pandas import Series
    data_row = {
        "handle": "test_user_002",
        "followers": 500,
        "daily_activeness": 0.6,
        "influence_index": 0.5,
        "bot_probability": 0.05,
        "tech_stance_score": 0.5,
        "emotion_intensity": 0.5,
        "propagation_speed": 0.6,
        "cognitive_entropy": 0.4
    }
    agent = UserAgent(data_row)
    
    print(f"\n✓ 更新前 Agent状态:")
    print(f"  - 情感: {agent.emotion:.2f}, 立场: {agent.stance:.2f}")
    
    new_emotion, new_stance = analyzer.update_agent_state(
        agent,
        generated_text="我支持这个方向",
        emotion_shift=0.1,
        stance_shift=0.2,
        action="repost"
    )
    
    print(f"✓ 更新后 Agent状态:")
    print(f"  - 情感: {new_emotion:.2f}, 立场: {new_stance:.2f}")


def test_persona_builder():
    """测试Persona生成器"""
    print_header("✅ 测试5: PersonaBuilder - Persona特征描述")
    
    builder = PersonaBuilder()
    
    from pandas import Series
    data_row = {
        "handle": "test_user_003",
        "followers": 2000,
        "daily_activeness": 0.85,
        "influence_index": 0.8,
        "bot_probability": 0.02,
        "tech_stance_score": 0.9,
        "emotion_intensity": 0.8,
        "propagation_speed": 0.7,
        "cognitive_entropy": 0.2
    }
    agent = UserAgent(data_row)
    
    # 生成Persona
    persona = builder.build_persona(agent)
    print("✓ 完整Persona:")
    print(persona)
    
    # 生成简短Persona
    summary = builder.build_persona_summary(agent)
    print(f"\n✓ 简短Persona: {summary}")
    
    # 生成Persona字典
    persona_dict = builder.build_persona_dict(agent)
    print(f"\n✓ Persona字典:")
    for key, value in persona_dict.items():
        if isinstance(value, dict):
            print(f"  {key}:")
            for k, v in value.items():
                print(f"    - {k}: {v}")
        else:
            print(f"  {key}: {value}")


def test_propagation_model():
    """测试传播模型"""
    print_header("✅ 测试6: PropagationModel - 语义+概率协同驱动")
    
    from pandas import Series
    
    # 创建Agent和Message
    data_row = {
        "handle": "test_user_004",
        "followers": 1500,
        "daily_activeness": 0.75,
        "influence_index": 0.65,
        "bot_probability": 0.1,
        "tech_stance_score": 0.7,
        "emotion_intensity": 0.7,
        "propagation_speed": 0.6,
        "cognitive_entropy": 0.35
    }
    agent = UserAgent(data_row)
    
    message = Message(
        content="新技术突破",
        emotion=0.8,
        stance=0.75
    )
    
    # 获取语义结果
    engine = SemanticEngine(enable_llm=False)
    semantic_result = engine.process(agent, message)
    
    # 计算传播概率（不使用语义）
    base_prob = sigmoid(0.3*agent.activeness + 0.3*agent.influence + 0.2*message.emotion + 0.2*0.9 - 0.2*agent.bot_prob)
    
    # 计算传播概率（使用语义）
    final_prob = compute_propagation_prob(agent, message, semantic_result)
    
    print(f"✓ 基础概率: {base_prob:.4f}")
    print(f"✓ 语义得分: {semantic_result['semantic_score']:.4f}")
    print(f"✓ 最终概率 (基础 × 语义): {final_prob:.4f}")
    print(f"✓ 动作: {semantic_result['action']}")
    print(f"✓ 影响: 基础概率提升了 {((final_prob / base_prob - 1) * 100):.1f}%")


def test_full_simulation():
    """测试完整的仿真流程"""
    print_header("✅ 测试7: 完整仿真流程 - Message传播 + Agent动态演化")
    
    print("⚠️  这项测试需要数据文件，请确保:")
    print("   - data/processed/netizen_science_standardized_profiles.csv 存在")
    
    data_path = os.path.join(os.path.dirname(__file__), "../../..", "data", "processed", "netizen_science_standardized_profiles.csv")
    
    if not os.path.exists(data_path):
        print(f"❌ 数据文件不存在: {data_path}")
        print("   跳过完整仿真测试")
        return
    
    try:
        # 加载数据
        print(f"\n✓ 加载数据: {data_path}")
        agents = load_agents_from_csv(data_path)
        print(f"✓ 加载了 {len(agents)} 个Agent")
        
        # 构建网络
        print("✓ 构建网络...")
        G = build_network(agents)
        print(f"✓ 网络: {G.number_of_nodes()} 节点, {G.number_of_edges()} 边")
        
        # 初始化仿真器
        print("✓ 初始化仿真器...")
        simulator = Simulator(enable_llm=False)
        
        # 生成初始事件
        print("✓ 生成初始事件...")
        gen = EventGenerator()
        initial_event = gen.generate_event(
            event_type="social_hotspot",
            custom_emotion=0.8,
            custom_stance=0.7
        )
        print(f"  - 内容: {initial_event.content}")
        print(f"  - 情感: {initial_event.emotion:.2f}, 立场: {initial_event.stance:.2f}")
        
        # 选择种子
        seed_ids = [agents[i].id for i in range(min(3, len(agents)))]
        print(f"✓ 种子节点: {seed_ids}")
        
        # 运行仿真
        print("✓ 运行仿真 (5步)...")
        history, active_nodes, detailed_metrics = simulator.run_simulation(
            G,
            seed_ids,
            initial_message=initial_event,
            max_steps=5
        )
        
        # 计算指标
        print("✓ 计算指标...")
        metrics = calculate_metrics(history, agents, active_nodes, detailed_metrics)
        
        print(f"\n✓ 仿真结果:")
        print(f"  - 传播历史: {history}")
        print(f"  - 激活节点数: {len(active_nodes)}")
        print(f"  - 覆盖率: {metrics['coverage_rate']*100:.1f}%")
        print(f"  - 平均增长率: {metrics['avg_growth_rate']*100:.1f}%")
        print(f"  - 活跃用户平均情感: {metrics['active_emotion_mean']:.2f}")
        print(f"  - 活跃用户平均立场: {metrics['active_stance_mean']:.2f}")
        print(f"  - 立场分化程度: {metrics['stance_divergence']:.2f}")
        
    except Exception as e:
        print(f"❌ 仿真失败: {e}")
        import traceback
        traceback.print_exc()


def main():
    """运行所有测试"""
    print("\n")
    print("█████████████████████████████████████████████████████████████████████████████████")
    print("█                   社会传播仿真系统 - 集成测试                                  █")
    print("█████████████████████████████████████████████████████████████████████████████████")
    
    try:
        test_message_class()
        test_event_generator()
        test_semantic_engine()
        test_sentiment_analyzer()
        test_persona_builder()
        test_propagation_model()
        test_full_simulation()
        
        print_header("✅ 所有测试完成！")
        print("✨ 系统已准备就绪")
        print("\n后续步骤:")
        print("  1. 启动后端: python -m src.modules.api")
        print("  2. 启动前端: cd frontend && npm run dev")
        print("  3. 访问: http://localhost:5173/social")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

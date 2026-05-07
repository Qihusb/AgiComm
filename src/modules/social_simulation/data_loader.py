import pandas as pd
import numpy as np
from src.modules.social_simulation.agent import UserAgent

def load_agents_from_csv(file_path):
    """
    数据入口（Data Loader）
    核心逻辑：
    将原始 CSV 数据 → 转换为标准化智能体对象
    具体做三件事：
    读取数据（CSV）
    清洗异常值（空值 / 字符串 / 缺失）
    映射为 UserAgent
    本质：非结构化数据 → 可计算状态变量
    """
    df = pd.read_csv(file_path)

    # 清洗异常值
    df = clean_data(df)

    agents = []
    for _, row in df.iterrows():
        agent = UserAgent(row)
        agents.append(agent)

    return agents

def clean_data(df):
    numeric_cols = [
        'followers', 'daily_activeness', 'influence_index', 'bot_probability',
        'tech_stance_score', 'emotion_intensity', 'propagation_speed', 'cognitive_entropy'
    ]

    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            median = df[col].median()
            df[col] = df[col].fillna(median)

    if 'handle' in df.columns:
        df['handle'] = df['handle'].astype(str)

    # 防 NaN / inf（这里很关键，很多仿真 crash 在这）
    df = df.replace([np.inf, -np.inf], np.nan)

    # clip 前必须确保无 NaN
    df = df.fillna(0)

    df['followers'] = df['followers'].clip(0, df['followers'].max())
    df['daily_activeness'] = df['daily_activeness'].clip(0, 1)
    df['influence_index'] = df['influence_index'].clip(0, 1)
    df['bot_probability'] = df['bot_probability'].clip(0, 1)
    df['tech_stance_score'] = df['tech_stance_score'].clip(-1, 1)
    df['emotion_intensity'] = df['emotion_intensity'].clip(0, 1)
    df['propagation_speed'] = df['propagation_speed'].clip(0, 1)
    df['cognitive_entropy'] = df['cognitive_entropy'].clip(0, 1)

    return df
# 负责媒体提问意图的通用化处理,生成【媒体科学传播通用画像】
import pandas as pd
import numpy as np

def generalize_media_distribution(input_path, output_path):
    # 读取数据（指定编码）
    df = pd.read_csv(input_path, encoding='utf-8')
    
    # 航天关注度占比列
    topic_cols = [
        'press_conference_topic_focus_Science_航天_其他',
        'press_conference_topic_focus_Science_航天_月球与深空探测',
        'press_conference_topic_focus_Science_航天_载人航天与空间站',
        'press_conference_topic_focus_Science_航天_运载火箭与航天安全',
        'press_conference_topic_focus_Science_航天_卫星技术与国际合作'
    ]
    
    # 1. 计算科学关注广度 (Science Interest Breadth)
    df['sci_interest_breadth'] = (df[topic_cols] > 0).sum(axis=1) / len(topic_cols)
    
    # 2. 计算科学特化度 (Science Specialization)
    df['sci_specialization'] = df[topic_cols].std(axis=1)
    
    # 3. 提取核心偏好标签 (Dominant Science Topic)
    topic_map = {
        'press_conference_topic_focus_Science_航天_其他': 'General_Science',
        'press_conference_topic_focus_Science_航天_月球与深空探测': 'Frontier_Exploration',
        'press_conference_topic_focus_Science_航天_载人航天与空间站': 'Infrastructure_Tech',
        'press_conference_topic_focus_Science_航天_运载火箭与航天安全': 'Safety_and_Defense',
        'press_conference_topic_focus_Science_航天_卫星技术与国际合作': 'Diplomacy_and_Application'
    }
    df['sci_dominant_tag'] = df[topic_cols].idxmax(axis=1).map(topic_map)
    df.loc[df[topic_cols].sum(axis=1) == 0, 'sci_dominant_tag'] = 'Universal_Reporter'

    # 4. 意图重命名：将特定场景的意图转化为通用科学传播意图
    # 逻辑：媒体问航天风险的习惯，会迁移到问AI风险或生物风险上
    intent_mapping = {
        'press_conference_question_intent_focus_structure_计划与安排': 'intent_agenda_setting',
        'press_conference_question_intent_focus_structure_细节与信息': 'intent_fact_checking',
        'press_conference_question_intent_focus_structure_合作与关系': 'intent_diplomacy_collab',
        'press_conference_question_intent_focus_structure_意义与影响': 'intent_social_impact',
        'press_conference_question_intent_focus_structure_原因与背景': 'intent_causal_logic',
        'press_conference_question_intent_focus_structure_安全与风险': 'intent_risk_assessment'
    }
    df.rename(columns=intent_mapping, inplace=True)
    # ======================================================

    # 5. 意图字段保留
    intent_cols = list(intent_mapping.values())  # 直接用重命名后的列
    
    # 6. 最终列 + 导出（
    core_cols = ['media_id', 'media_name', 'country', 'ownership_type']
    df_final = df[core_cols + ['sci_interest_breadth', 'sci_specialization', 'sci_dominant_tag'] + intent_cols]
    
    df_final.to_csv(
        output_path,
        index=False,
        encoding='utf-8-sig'
    )
    return df_final

df_res = generalize_media_distribution(
    '../../data/processed/media_inquiring_dynamic.csv',
    '../../data/processed/media_science_generalized.csv'
)
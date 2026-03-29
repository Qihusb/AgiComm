import pandas as pd
import numpy as np

def generalize_media_distribution(input_path, output_path):
    # 1. 读取数据
    df = pd.read_csv(input_path, encoding='utf-8')
    
    # 航天关注度占比列（保持原有逻辑）
    topic_cols = [
        'press_conference_topic_focus_Science_航空航天_其他',
        'press_conference_topic_focus_Science_航空航天_月球与深空探测',
        'press_conference_topic_focus_Science_航空航天_载人航空航天与空间站',
        'press_conference_topic_focus_Science_航空航天_运载火箭与航空航天安全',
        'press_conference_topic_focus_Science_航空航天_卫星技术与国际合作'
    ]
    
    # --- 核心计算逻辑（保持不变） ---
    # 计算科学关注广度
    df['sci_interest_breadth'] = (df[topic_cols] > 0).sum(axis=1) / len(topic_cols)
    # 计算科学特化度
    df['sci_specialization'] = df[topic_cols].std(axis=1)
    
    # 提取核心偏好标签
    topic_map = {
        'press_conference_topic_focus_Science_航空航天_其他': 'General_Science',
        'press_conference_topic_focus_Science_航空航天_月球与深空探测': 'Frontier_Exploration',
        'press_conference_topic_focus_Science_航空航天_载人航空航天与空间站': 'Infrastructure_Tech',
        'press_conference_topic_focus_Science_航空航天_运载火箭与航空航天安全': 'Safety_and_Defense',
        'press_conference_topic_focus_Science_航空航天_卫星技术与国际合作': 'Diplomacy_and_Application'
    }
    
    # 确定主导标签，处理全 0 情况
    df['sci_dominant_tag'] = df[topic_cols].idxmax(axis=1).map(topic_map)
    df.loc[df[topic_cols].sum(axis=1) == 0, 'sci_dominant_tag'] = 'Universal_Reporter'

    # 意图重命名：转化为通用科学传播意图
    intent_mapping = {
        'press_conference_question_intent_focus_structure_计划与安排': 'intent_agenda_setting',
        'press_conference_question_intent_focus_structure_细节与信息': 'intent_fact_checking',
        'press_conference_question_intent_focus_structure_合作与关系': 'intent_diplomacy_collab',
        'press_conference_question_intent_focus_structure_意义与影响': 'intent_social_impact',
        'press_conference_question_intent_focus_structure_原因与背景': 'intent_causal_logic',
        'press_conference_question_intent_focus_structure_安全与风险': 'intent_risk_assessment'
    }
    df.rename(columns=intent_mapping, inplace=True)
    
    # --- 增强实验用的静态属性提取 ---
    # 增加媒体类型、语言、地区、覆盖面、以及是否有常态化提问习惯
    extra_static_cols = [
        'region', 
        'primary_language', 
        'media_type', 
        'coverage_areas', 
        'is_press_conference_regular'
    ]
    
    # 检查列是否存在，防止报错
    valid_extra_cols = [c for c in extra_static_cols if c in df.columns]
    
    # 2. 最终字段选择
    # 基础核心字段 + 新增实验维度 + 泛化后的科学指标 + 意图指标
    intent_cols = list(intent_mapping.values())
    core_cols = ['media_id', 'media_name', 'country', 'ownership_type']
    
    final_columns = (
        core_cols + 
        valid_extra_cols + 
        ['sci_interest_breadth', 'sci_specialization', 'sci_dominant_tag'] + 
        intent_cols
    )
    
    df_final = df[final_columns].copy()

    # 3. 导出数据
    df_final.to_csv(
        output_path,
        index=False,
        encoding='utf-8-sig'
    )
    return df_final

# 执行转换
df_res = generalize_media_distribution(
    '../../data/processed/media_science_inquiring_dynamic.csv',
    '../../data/processed/media_science_inquiring_generalized.csv'
)
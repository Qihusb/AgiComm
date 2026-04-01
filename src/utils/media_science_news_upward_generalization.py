import pandas as pd
import numpy as np

def generalize_media_news_profiles(input_path, output_path):
    # 1. 读取数据
    df = pd.read_csv(input_path, encoding='utf-8')

    # ---------------------------------------------------------
    # 任务 A：处理占比字段 (Proportions) 与 活跃度
    # ---------------------------------------------------------
    # 定义原始占比列
    prop_cols_map = {
        'news_reports_topic_focus_Science_航空航天_探月与深空探测': 'sci_weight_frontier',
        'news_reports_topic_focus_Science_航空航天_运载火箭与航空航天安全': 'sci_weight_security',
        'news_reports_topic_focus_Science_航空航天_载人航空航天与空间站': 'sci_weight_infrastructure',
        'news_reports_topic_focus_Science_航空航天_卫星技术与国际合作': 'sci_weight_collab'
    }
    
    # 重命名并填充缺失（无占比数据默认为 0）
    df.rename(columns=prop_cols_map, inplace=True)
    new_prop_cols = list(prop_cols_map.values())
    df[new_prop_cols] = df[new_prop_cols].fillna(0)

    # 计算报道活跃度评分 (Activity Level)
    # 逻辑：常态化参与发布会 +1，社交影响力取 log 后作为增益
    influence_score = np.log10(df['social_metrics_x_followers_latest_value'].fillna(0) + 10)
    df['sci_activity_level'] = (df['is_press_conference_regular'].map({True: 0.7, False: 0.2}) + 
                                (influence_score / influence_score.max()) * 0.3).round(2)

    # ---------------------------------------------------------
    # 任务 B：模拟报道字数 (Word Count Range) - 基于媒体类型
    # ---------------------------------------------------------
    # 标注：模拟数据。通讯社偏短，报纸偏长，互联网媒体跨度大
    def simulate_word_count(m_type):
        m_type = str(m_type)
        if '报纸' in m_type: return "800-1500"
        if '通讯社' in m_type: return "300-600"
        if '电视' in m_type or '广播' in m_type: return "200-500"
        if '互联网' in m_type: return "100-400"
        return "400-800"

    df['sci_word_count_range'] = df['media_type'].apply(simulate_word_count)

    # ---------------------------------------------------------
    # 任务 C：模拟报道风格 (Reporting Style) - 基于所有权与地区
    # ---------------------------------------------------------
    # 标注：模拟数据。国有倾向宏大叙事，私营倾向分析/评论
    def simulate_style(row):
        owner = str(row['ownership_type'])
        if '国有' in owner: return "Grand_Official"
        if '私营' in owner: return "Analytical_Critical"
        return "General_Informative"

    df['sci_report_style'] = df.apply(simulate_style, axis=1)

    # ---------------------------------------------------------
    # 任务 D：语言清洗
    # ---------------------------------------------------------
    # 统一取第一语言作为模拟报道语言
    df['primary_report_lang'] = df['primary_language'].str.split(',').str[0].str.strip()

    # ---------------------------------------------------------
    # 3. 最终列筛选与导出
    # ---------------------------------------------------------
    # 仅保留实验强相关列
    core_cols = ['media_id', 'media_name', 'country', 'region', 'media_type', 'ownership_type']
    simulation_cols = [
        'primary_report_lang', 
        'sci_activity_level', 
        'sci_report_style', 
        'sci_word_count_range'
    ]
    
    df_final = df[core_cols + simulation_cols + new_prop_cols].copy()

    # 导出
    df_final.to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f"✅ 媒体报道泛化画像已生成。")
    print(f"   - 包含占比权重列: {new_prop_cols}")
    print(f"   - 已注入模拟字段: sci_word_count_range, sci_report_style")
    
    return df_final

# 执行
df_news_gen = generalize_media_news_profiles(
    '../../data/processed/media_science_news_dynamic.csv',
    '../../data/processed/media_science_news_generalized.csv'
)


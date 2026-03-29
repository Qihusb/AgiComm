import pandas as pd
import numpy as np

def process_and_generalize_netizens(file_configs):
    """
    向上泛化：统一多个科技领域网民数据 → 生成标准化网民画像库
    file_configs: 字典 {领域名: 文件路径}
    """
    all_profiles = []

    # 最终统一的标准字段（所有文件都会对齐成这个结构）
    standard_schema = [
        'handle', 'location', 'language', 'followers', 'daily_activeness',
        'influence_index', 'bot_probability', 'tech_stance_score',
        'emotion_intensity', 'strategy_type', 'interest_domain',
        'is_verified', 'propagation_speed', 'cognitive_entropy'
    ]

    for domain, file_path in file_configs.items():
        print(f"正在处理：{domain} -> {file_path}")

        # ===================== 修复点 1 =====================
        # 你的文件是 EXCEL，不是 CSV！必须用 read_excel
        # ====================================================
        df = pd.read_excel(file_path)

        # 字段映射：把不同文件的列名 → 统一标准名
        mapping = {
            'Handle': 'handle',
            'Location': 'location',
            'Language': 'language',
            'FollowersCount': 'followers',
            'Daily_Post_Rate': 'daily_activeness',
            'Influence_Score': 'influence_index',
            'Bot_Score': 'bot_probability',
            'Tone_Emotional_Score': 'emotion_intensity',
            'Strategy_Label': 'strategy_type',
            'Interest_Entropy': 'cognitive_entropy'
        }

        # 1. 立场分数（支持/中立/反对 → 数值化）
        if 'Stance_Numeric' in df.columns:
            df['tech_stance_score'] = df['Stance_Numeric']
        elif 'Stance' in df.columns:
            stance_map = {
                'Supportive': 1.0,
                'Neutral': 0.0,
                'Opposed': -1.0,
                'Optimist': 1.0,
                'Skeptic': -1.0
            }
            df['tech_stance_score'] = df['Stance'].map(stance_map).fillna(0)
        else:
            df['tech_stance_score'] = 0

        # 2. 是否认证（蓝V）
        #if 'Is_Blue' in df.columns:
        #    df['is_verified'] = df['Is_Blue'].map({True: 1, False: 0}).fillna(0)
        #elif 'Verified' in df.columns:
        #    df['is_verified'] = df['Verified'].map({True: 1, False: 0}).fillna(0)
        #else:
        #    df['is_verified'] = 0

        # 3. 传播速度（转发能力）
        if 'RT_Ratio' in df.columns:
            df['propagation_speed'] = df['RT_Ratio']
        elif 'Sample_Avg_Retweet' in df.columns:
            df['propagation_speed'] = df['Sample_Avg_Retweet']
        else:
            df['propagation_speed'] = df['Influence_Score'] * 0.1

        # 4. 重命名 → 对齐标准结构
        df_mapped = df.rename(columns=mapping)
        df_mapped['interest_domain'] = domain  # 领域标签

        # 5. 只保留标准字段，缺失自动补 NaN
        df_final = df_mapped.reindex(columns=standard_schema)
        all_profiles.append(df_final)

    # 合并所有领域
    master_df = pd.concat(all_profiles, ignore_index=True)

    # 缺失值填充
    master_df['location'] = master_df['location'].fillna('Global')
    master_df['strategy_type'] = master_df['strategy_type'].fillna('Generalist')
    master_df['language'] = master_df['language'].fillna('en')

    return master_df

# ===================== 配置 =====================
configs = {
    "health": "../../data/raw/netizen_tech_health_profile.xlsx",
    "aerospace": "../../data/raw/netizen_tech_aerospace_profile.xlsx",
    "ai": "../../data/raw/netizen_tech_ai_profile.xlsx",
    "data": "../../data/raw/netizen_tech_data_profile.xlsx"
}

# ===================== 运行 =====================
if __name__ == "__main__":
    try:
        # 生成标准化泛化数据库
        generalized_db = process_and_generalize_netizens(configs)

        # 保存结果
        save_path = "../../data/processed/netizen_science_standardized_profiles.csv"
        generalized_db.to_csv(save_path, index=False, encoding="utf-8-sig")

        print("\n✅ 处理完成！")
        print(f"📊 总数据量：{len(generalized_db)} 条")
        print(f"📁 标准化文件已保存：{save_path}")
        print("\n📌 标准字段列表：")
        print(list(generalized_db.columns))

    except Exception as e:
        print("\n❌ 报错：", str(e))
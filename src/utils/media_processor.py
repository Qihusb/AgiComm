import json
import pandas as pd

def flatten_dict(d, parent_key='', sep='_'):
    """递归提取嵌套字典，生成路径式列名，并对列表进行规范化处理"""
    if not isinstance(d, dict):
        return {}
    
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        
        if isinstance(v, dict):
            # 递归处理嵌套字典
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        elif isinstance(v, list):
            # 1. 对于 history 列表，提取最后一次记录的数值
            if k == 'history' and len(v) > 0 and isinstance(v[-1], dict):
                items.append((f"{parent_key}_latest_value", v[-1].get('value', 0)))
            # 2. 对于其他列表（如语言、领域、类型），转为逗号分隔的字符串，方便 CSV 阅读
            else:
                items.append((new_key, ", ".join(map(str, v)) if v else ""))
        else:
            items.append((new_key, v))
    return dict(items)

def process_media_json(input_json, output_inquiring, output_news):
    with open(input_json, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    all_data = []
    for m_id, content in data.items():
        # --- 核心修改点：对静态和动态属性都进行展平处理 ---
        static_raw = content.get('static_profile', {})
        behavior_raw = content.get('behavior_dynamic', {})
        
        # 展平静态属性（解决语言列表、社交账号嵌套问题）
        static_flat = flatten_dict(static_raw)
        # 展平动态行为
        behavior_flat = flatten_dict(behavior_raw)
        
        # 合并所有属性
        combined = {**static_flat, **behavior_flat}
        all_data.append(combined)
    
    df = pd.DataFrame(all_data)

    # 1. 科学补全与清洗
    # 确保所有话题权重列存在，缺失填充为 0
    topic_cols = [c for c in df.columns if 'topic_focus' in c]
    df[topic_cols] = df[topic_cols].fillna(0)
    
    # 2. 统一静态字段（确保核心列不缺失）
    required_static = ['media_id', 'media_name', 'country', 'region', 'ownership_type', 'primary_language']
    for col in required_static:
        if col not in df.columns: df[col] = "Unknown"
    
    # 3. 划分为两个实验专用文件
    # 定义静态核心列（增加了语言、类型、覆盖范围等更多背景信息）
    # 搜索包含 static 关键词的列，或者手动指定核心列
    core_cols = [c for c in df.columns if any(sub in c for sub in [
        'media_id', 'media_name', 'country', 'region', 'ownership_type', 
        'primary_language', 'media_type', 'coverage_areas', 'is_press_conference_regular'
    ])]

    # 3.1 媒体提问动态属性 (Press Conference 侧)
    inquiring_dynamic = [c for c in df.columns if 'press_conference' in c or 'consistency' in c]
    df_inquiring = df[list(set(core_cols + inquiring_dynamic))].copy()
    
    # 3.2 媒体报道动态属性 (News & Social 侧)
    news_dynamic = [c for c in df.columns if 'news_reports' in c or 'social_metrics' in c or 'social_presence' in c]
    df_news = df[list(set(core_cols + news_dynamic))].copy()

    # 排序：让 media_id 始终在第一列
    for temp_df in [df_inquiring, df_news]:
        cols = temp_df.columns.tolist()
        if 'media_id' in cols:
            cols.insert(0, cols.pop(cols.index('media_id')))
            temp_df = temp_df[cols]

    # 保存
    df_inquiring.to_csv(output_inquiring, index=False, encoding='utf-8-sig')
    df_news.to_csv(output_news, index=False, encoding='utf-8-sig')
    
    print(f"✅ 转换成功！包含完整静态属性。\n提问数据: {output_inquiring}\n报道数据: {output_news}")

# 执行
process_media_json('../../data/raw/media_profiles.json', '../../data/processed/media_science_inquiring_dynamic.csv', '../../data/processed/media_science_news_dynamic.csv')
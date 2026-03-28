import json
import pandas as pd
import ast

def flatten_dict(d, parent_key='', sep='_'):
    """递归提取嵌套字典，生成路径式列名"""
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        elif isinstance(v, list):
            # 对于 history 列表，提取最后一次记录的数值
            if k == 'history' and len(v) > 0 and isinstance(v[-1], dict):
                items.append((f"{parent_key}_latest_value", v[-1].get('value', 0)))
            else:
                items.append((new_key, ", ".join(map(str, v))))
        else:
            items.append((new_key, v))
    return dict(items)

def process_media_json(input_json, output_inquiring, output_news):
    with open(input_json, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    all_data = []
    for m_id, content in data.items():
        # 1. 提取静态属性
        static = content.get('static_profile', {})
        # 2. 提取动态属性
        behavior = content.get('behavior_dynamic', {})
        
        # 合并并展平
        combined = {**static, **flatten_dict(behavior)}
        all_data.append(combined)
    
    df = pd.DataFrame(all_data)

    # 3. 科学补全与清洗
    # A. 确保所有话题权重列存在，缺失填充为 0
    topic_cols = [c for c in df.columns if 'topic_focus' in c]
    df[topic_cols] = df[topic_cols].fillna(0)
    
    # B. 统一静态字段（防止 JSON 缺失导致 CSV 少列）
    required_static = ['media_id', 'media_name', 'country', 'region', 'ownership_type']
    for col in required_static:
        if col not in df.columns: df[col] = "Unknown"
    
    # 4. 划分为两个实验专用文件
    # 定义静态核心列
    core_cols = [c for c in required_static if c in df.columns] + ['is_press_conference_regular']

    # 4.1 媒体提问动态属性 (Press Conference 侧)
    inquiring_dynamic = [c for c in df.columns if 'press_conference' in c or 'consistency' in c]
    df_inquiring = df[core_cols + inquiring_dynamic].copy()
    
    # 4.2 媒体报道动态属性 (News & Social 侧)
    news_dynamic = [c for c in df.columns if 'news_reports' in c or 'social_metrics' in c]
    df_news = df[core_cols + news_dynamic].copy()

    # 保存
    df_inquiring.to_csv(output_inquiring, index=False, encoding='utf-8-sig')
    df_news.to_csv(output_news, index=False, encoding='utf-8-sig')
    
    print(f"✅ 转换成功！\n提问数据: {output_inquiring}\n报道数据: {output_news}")

# 执行转换
process_media_json(r'data\raw\media_profiles.json', r'data\processed\media_inquiring_dynamic.csv', r'data\processed\media_news_dynamic.csv')

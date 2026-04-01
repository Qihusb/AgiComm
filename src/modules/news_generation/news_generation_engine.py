import random
import re
from dataclasses import dataclass
from typing import Optional, Tuple, Dict, List, Any
import pandas as pd

from src.utils.llm_client import llm_client


_COUNTRY_SPLIT_RE = re.compile(r"[（(].*?$")
_WORD_RANGE_RE = re.compile(r"^\s*(\d+)\s*(?:-\s*(\d+)\s*)?$")


def _safe_float(v, default: float = 0.0) -> float:
    try:
        if v is None:
            return default
        if isinstance(v, float) and pd.isna(v):
            return default
        return float(v)
    except Exception:
        return default


def _parse_country_main(country: Optional[str]) -> str:
    if not country:
        return ""
    s = str(country).strip()
    if not s:
        return ""
    s = _COUNTRY_SPLIT_RE.sub("", s).strip()
    return s


def _parse_word_count_range(range_str: Optional[str]) -> Tuple[int, int]:
    if not range_str:
        return 200, 500
    m = _WORD_RANGE_RE.match(str(range_str))
    if not m:
        return 200, 500
    a = int(m.group(1))
    b = int(m.group(2)) if m.group(2) else a
    return min(a, b), max(a, b)


def _map_report_style(style: Optional[str]) -> str:
    s = (style or "").strip()
    if s == "Grand_Official":
        return (
            "采用 Grand_Official 风格：宏大叙事、语气中立偏积极、偏官方表述。\n"
            "避免过度情绪化或人身攻击；措辞更偏政策/机构语汇。"
        )
    if s == "Analytical_Critical":
        return (
            "采用 Analytical_Critical 风格：分析性叙述、强调对比与多角度论证，必要时提出质疑。\n"
            "使用更强的分析词（如：可能、值得关注、存在挑战等），但保持专业。"
        )
    return (
        "采用通用新闻风格：专业、具体、与科学/国际传播相关；保持中立与可读性。"
    )


def _build_narrative_keywords(weights: Dict[str, float]) -> Dict[str, Dict[str, Any]]:
    w_frontier = float(weights.get("frontier", 0.0))
    w_security = float(weights.get("security", 0.0))
    w_infra = float(weights.get("infrastructure", 0.0))
    w_collab = float(weights.get("collab", 0.0))

    frontier_kw = "前沿探索、技术边界、路线图、突破与未来影响"
    security_kw = "风险/安全/成本、双刃剑效应、合规与防御措施、缓解方案"
    infra_kw = "工程可行性、产业链、关键技术/模块、建设进度与落地路径"
    collab_kw = "国际协作、协议/合作机制、共同研发/监管与协调框架"

    security_hard = w_security >= 0.4

    return {
        "frontier": {"weight": w_frontier, "keywords": frontier_kw},
        "security": {"weight": w_security, "keywords": security_kw, "hard": security_hard},
        "infrastructure": {"weight": w_infra, "keywords": infra_kw},
        "collab": {"weight": w_collab, "keywords": collab_kw},
    }


@dataclass
class ReportCandidate:
    media_row: Dict[str, Any]
    related_score: float
    activity: float
    delay_seconds: int


class NewsGenerationEngine:
    def __init__(self, data_path: str):
        self.df = pd.read_csv(data_path)

        if "sci_activity_level" not in self.df.columns:
            raise ValueError("media_science_news_generalized.csv 缺少字段 `sci_activity_level`")

        self.activity_high_threshold = float(self.df["sci_activity_level"].quantile(0.75))
        self.low_related_threshold = 0.6

    def simulate_news(
        self,
        event_description: str,
        event_date: Optional[str] = None,
        media_ids: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        print(f"🔹 simulate_news 启动")
        print(f"  - event_description: {event_description[:50]}...")
        print(f"  - event_date: {event_date}")
        print(f"  - media_ids: {media_ids} (类型: {type(media_ids).__name__}, 长度: {len(media_ids) if media_ids else 0})")
        
        event_lower = event_description.lower()

        # ========== 关键修改 ==========
        # 如果用户明确指定了 media_ids，则为这些媒体强制生成报道（不应用阈值过滤）
        if media_ids:
            print(f"  🎯 用户明确指定了 {len(media_ids)} 个媒体 - 将强制为这些媒体生成报道")
            results: List[Dict[str, Any]] = []
            
            for media_id in media_ids:
                # 查找对应的媒体
                matching_rows = self.df[self.df['media_id'] == media_id]
                
                if matching_rows.empty:
                    print(f"  ❌ 媒体 {media_id} 未找到")
                    results.append({
                        "media_id": media_id,
                        "media_name": "未知媒体",
                        "country": "未知",
                        "behavior_tag": "媒体报道",
                        "content": f"媒体 {media_id} 不在数据库中",
                        "has_error": True,
                    })
                    continue
                
                media_row = matching_rows.iloc[0].to_dict()
                
                try:
                    content = self._generate_report(media_row, event_description)
                    results.append({
                        "media_id": media_row.get("media_id"),
                        "media_name": media_row.get("media_name"),
                        "country": media_row.get("country"),
                        "behavior_tag": "媒体报道",
                        "report_type": "指定报道",
                        "publish_date": event_date,
                        "report_style": media_row.get("sci_report_style"),
                        "word_count": round((float(media_row.get("sci_word_count_range", "200-500").split("-")[0]) 
                                            + float(media_row.get("sci_word_count_range", "200-500").split("-")[-1])) / 2),
                        "content": content,
                        "has_error": False,
                    })
                    print(f"  ✓ 完成报告: {media_row.get('media_id')} ({media_row.get('media_name')})")
                except Exception as e:
                    print(f"  ✗ 报告生成失败: {media_id} - {type(e).__name__}: {str(e)[:50]}")
                    results.append({
                        "media_id": media_row.get("media_id"),
                        "media_name": media_row.get("media_name"),
                        "country": media_row.get("country"),
                        "behavior_tag": "媒体报道",
                        "report_type": "指定报道",
                        "content": f"报道生成失败：{str(e)[:100]}",
                        "has_error": True,
                    })
            
            print(f"  📤 返回 {len(results)} 份报道 (所有指定媒体)")
            return results
        
        # ========== 原有逻辑：自动选择媒体 ==========
        candidates: List[ReportCandidate] = []
        
        for _, row in self.df.iterrows():
            media_row = row.to_dict()
            activity = _safe_float(media_row.get("sci_activity_level"), 0.0)

            country_main = _parse_country_main(media_row.get("country"))
            related_score = 0.0
            if country_main:
                if country_main.lower() in event_lower:
                    related_score = 1.0
                elif str(media_row.get("region", "")).strip() and str(media_row.get("region")).lower() in event_lower:
                    related_score = 0.6

            should_report = (activity >= self.activity_high_threshold) or (
                activity < self.activity_high_threshold and related_score >= self.low_related_threshold
            )
            if not should_report:
                continue

            delay_seconds = int((1.0 - min(max(activity, 0.0), 1.0)) * 120) + random.randint(0, 20)

            candidates.append(
                ReportCandidate(
                    media_row=media_row,
                    related_score=related_score,
                    activity=activity,
                    delay_seconds=delay_seconds,
                )
            )

        print(f"  - 自动筛选：{len(candidates)} 个候选媒体")

        if not candidates:
            print(f"  ⚠️  无符合条件的候选，从前3个高活跃媒体中选择")
            top_df = self.df.sort_values("sci_activity_level", ascending=False).head(3)
            for _, row in top_df.iterrows():
                media_row = row.to_dict()
                activity = _safe_float(media_row.get("sci_activity_level"), 0.0)
                delay_seconds = int((1.0 - min(max(activity, 0.0), 1.0)) * 120) + random.randint(0, 20)
                candidates.append(
                    ReportCandidate(
                        media_row=media_row,
                        related_score=0.0,
                        activity=activity,
                        delay_seconds=delay_seconds,
                    )
                )
            print(f"  ✓ 备选筛选：{len(candidates)} 个候选")

        candidates.sort(key=lambda c: c.delay_seconds)
        results: List[Dict[str, Any]] = []

        for idx, c in enumerate(candidates):
            report_type = "首发" if idx == 0 else "转载"
            try:
                content = self._generate_report(c.media_row, event_description)
                results.append({
                    "media_id": c.media_row.get("media_id"),
                    "media_name": c.media_row.get("media_name"),
                    "country": c.media_row.get("country"),
                    "behavior_tag": "媒体报道",
                    "report_type": report_type,
                    "delay_seconds": c.delay_seconds,
                    "publish_date": event_date,
                    "report_style": c.media_row.get("sci_report_style"),
                    "word_count": round((float(c.media_row.get("sci_word_count_range", "200-500").split("-")[0]) 
                                        + float(c.media_row.get("sci_word_count_range", "200-500").split("-")[-1])) / 2),
                    "content": content,
                    "has_error": False,
                })
                print(f"  ✓ 完成报告 #{idx+1}/{len(candidates)}: {c.media_row.get('media_id')}")
            except Exception as e:
                results.append({
                    "media_id": c.media_row.get("media_id"),
                    "media_name": c.media_row.get("media_name"),
                    "country": c.media_row.get("country"),
                    "behavior_tag": "媒体报道",
                    "report_type": report_type,
                    "content": f"报道生成失败：{str(e)[:100]}",
                    "has_error": True,
                })
                print(f"  ✗ 报告失败 #{idx+1}/{len(candidates)}: {c.media_row.get('media_id')} - {type(e).__name__}")
        
        print(f"  📤 返回 {len(results)} 份报道")
        return results

    def _generate_report(self, media_row: Dict[str, Any], event_description: str) -> str:
        ownership_type = str(media_row.get("ownership_type", "")).strip() or "未知"
        region = str(media_row.get("region", "")).strip() or "未知"
        primary_lang = str(media_row.get("primary_report_lang", "")).strip() or "中文"

        activity = _safe_float(media_row.get("sci_activity_level"), 0.0)
        style = str(media_row.get("sci_report_style", "")).strip() or "Grand_Official"
        word_range = str(media_row.get("sci_word_count_range", "")).strip()
        word_min, word_max = _parse_word_count_range(word_range)

        weights = {
            "frontier": _safe_float(media_row.get("sci_weight_frontier"), 0.0),
            "security": _safe_float(media_row.get("sci_weight_security"), 0.0),
            "infrastructure": _safe_float(media_row.get("sci_weight_infrastructure"), 0.0),
            "collab": _safe_float(media_row.get("sci_weight_collab"), 0.0),
        }

        kw = _build_narrative_keywords(weights)

        security_hard = kw["security"].get("hard", False)
        security_hard_line = (
            "硬性要求：由于安全权重较高，你的报道必须包含对风险、成本或安全的描述，并给出（可选）应对/缓解视角。\n"
            if security_hard
            else ""
        )

        max_tokens = max(256, min(1024, int(word_max * 1.2)))

        system_prompt = (
            f"你是一家来自{media_row.get('country')}的{ownership_type}媒体记者。\n"
            f"你的报道区域/传播背景是：{region}。\n"
            f"请使用语言：{primary_lang} 输出。\n\n"
            f"{_map_report_style(style)}\n\n"
            "写作目标：围绕给定科技事件生成媒体新闻报道，要求专业、具体、可读，并避免编造具体未给出的事实细节。\n"
            f"长度要求：控制在约 {word_min}-{word_max} 词/字的范围内（不要明显超出）。\n"
            f"输出中不要包含任何 JSON、标题前缀或多余解释；只输出正文。\n"
        )

        user_prompt = (
            f"科技/国际事件：{event_description}\n\n"
            "请按“叙事权重”分配报道重点，并保证覆盖以下关键词（可用多段或要点展开）：\n"
            f"- 前沿探索（weight={weights['frontier']:.3f}）：{kw['frontier']['keywords']}\n"
            f"- 安全与风险（weight={weights['security']:.3f}）：{kw['security']['keywords']}\n"
            f"- 基础设施与工程（weight={weights['infrastructure']:.3f}）：{kw['infrastructure']['keywords']}\n"
            f"- 国际协作与合规（weight={weights['collab']:.3f}）：{kw['collab']['keywords']}\n\n"
            f"{security_hard_line}"
            f"并在文中自然体现：该媒体的所有制与区域背景（{ownership_type}、{region}）如何影响其关注点与措辞。\n\n"
            "段落建议：\n"
            "1) 事件概述（1段）\n"
            "2) 叙事重心展开（2段以内，覆盖权重最高的2-3个方向）\n"
            "3) 风险/成本/合作或工程落地的补充（如对应权重较高则更深入）\n"
            "4) 结尾总结（1段，保持新闻口吻）\n"
        )

        user_prompt += f"\n附：媒体科学活动度约 {activity:.2f}（更高代表更快响应与更强首发倾向）。"

        # 打印媒体信息
        media_id = media_row.get("media_id", "未知")
        media_name = media_row.get("media_name", "未知")
        print(f"\n{'='*80}")
        print(f"📰 生成报道：{media_name} ({media_id})")
        print(f"{'='*80}")
        
        # 打印系统提示词
        print(f"\n🔧 系统提示词：")
        print(f"{'-'*80}")
        print(system_prompt)
        print(f"{'-'*80}")
        
        # 打印用户提示词
        print(f"\n👤 用户提示词：")
        print(f"{'-'*80}")
        print(user_prompt)
        print(f"{'-'*80}")
        
        # 调用 LLM
        print(f"\n⏳ 调用 LLM（max_tokens={max_tokens}）...")
        content = llm_client.ask(system_prompt, user_prompt, max_tokens=max_tokens)
        
        # 打印返回的内容
        print(f"\n✅ LLM 返回内容：")
        print(f"{'-'*80}")
        print(content)
        print(f"{'-'*80}\n")
        
        return content
    
    
    
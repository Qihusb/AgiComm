import pandas as pd


_INTENT_COLUMNS = (
    ("intent_agenda_setting", "agenda_setting"),
    ("intent_fact_checking", "fact_checking"),
    ("intent_diplomacy_collab", "diplomacy"),
    ("intent_social_impact", "social_impact"),
    ("intent_causal_logic", "causal_logic"),
    ("intent_risk_assessment", "risk_assessment"),
)

_INTENT_LABELS = {
    "agenda_setting": "议程设置",
    "fact_checking": "事实核查",
    "diplomacy": "外交与协作",
    "social_impact": "社会影响",
    "causal_logic": "因果与背景",
    "risk_assessment": "风险与安全",
}


def _is_na(value):
    if value is None:
        return True
    try:
        return bool(pd.isna(value))
    except (TypeError, ValueError):
        return False


def _safe_str(value, default="未知"):
    if _is_na(value):
        return default
    if isinstance(value, str) and not value.strip():
        return default
    return str(value).strip()


def _safe_float(value, default=0.0):
    if _is_na(value):
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _parse_bool(value):
    if isinstance(value, bool):
        return value
    if _is_na(value):
        return False
    s = str(value).strip().lower()
    if s in ("true", "1", "yes", "y", "是"):
        return True
    if s in ("false", "0", "no", "n", "否"):
        return False
    return False


def _build_intent_weights(profile_row):
    raw = {}
    for col, key in _INTENT_COLUMNS:
        v = profile_row.get(col) if hasattr(profile_row, "get") else profile_row[col]
        if _is_na(v) or (isinstance(v, str) and not str(v).strip()):
            raw[key] = None
        else:
            try:
                raw[key] = float(v)
            except (TypeError, ValueError):
                raw[key] = None

    missing = [k for k, w in raw.items() if w is None]
    n = len(_INTENT_COLUMNS)
    fill = 1.0 / n
    for k in missing:
        raw[k] = fill

    total = sum(raw.values())
    if total <= 0:
        for k in raw:
            raw[k] = 1.0 / n
    return raw


class MediaAgent:
    def __init__(self, profile_row):
        """
        基于 GSS 范式的媒体智能体：字段对齐 `media_science_inquiring_generalized.csv`。
        :param profile_row: pd.Series
        """
        row = profile_row
        self.id = _safe_str(row.get("media_id"), "unknown")
        self.name = _safe_str(row.get("media_name"), "未知媒体")
        self.country = _safe_str(row.get("country"), "未知")
        self.ownership = _safe_str(row.get("ownership_type"), "未知")
        self.region = _safe_str(row.get("region"), "未知")
        self.primary_language = _safe_str(row.get("primary_language"), "未知")
        self.media_type = _safe_str(row.get("media_type"), "未知")
        self.coverage_areas = _safe_str(row.get("coverage_areas"), "综合")
        self.is_press_conference_regular = _parse_bool(row.get("is_press_conference_regular"))

        breadth = _safe_float(row.get("sci_interest_breadth"), 0.0)
        self.persona = {
            "breadth": breadth,
            "dominant_tag": _safe_str(row.get("sci_dominant_tag"), "Universal_Reporter"),
            "specialization": _safe_float(row.get("sci_specialization"), 0.0),
        }

        self.intents = _build_intent_weights(row)

    def intent_label_zh(self, intent_key: str) -> str:
        return _INTENT_LABELS.get(intent_key, intent_key)

    def get_persona_description(self) -> str:
        """结构化人设描述，供 LLM system prompt 使用。"""
        pc = "是外交部/科技发布会等场合的常客记者" if self.is_press_conference_regular else "较少以发布会例行身份出现，但仍需专业提问能力"
        lines = [
            f"【身份与所有制】{self.name}，来自{self.country}的{self.ownership}媒体；机构类型：{self.media_type}。",
            f"【地区与语言】主要地区/区域：{self.region}；语言：{self.primary_language}。",
            f"【报道覆盖】关注领域：{self.coverage_areas}。",
            f"【发布会参与】{pc}。",
            "【科学报道画像】"
            f"科学关注广度约 {self.persona['breadth']:.2f}；"
            f"科学特化度约 {self.persona['specialization']:.3f}（越高越集中在少数议题）；"
            f"主导科学标签：{self.persona['dominant_tag']}。",
            "【提问意图倾向（相对权重，供单次抽样）】"
            + "；".join(
                f"{self.intent_label_zh(k)}={self.intents.get(k, 0):.3f}"
                for _, k in _INTENT_COLUMNS
            )
            + "。",
        ]
        return "\n".join(lines)

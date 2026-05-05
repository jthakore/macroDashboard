from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Literal


Bucket = Literal[
    "Growth",
    "Inflation",
    "Labor",
    "Financial conditions",
    "Liquidity",
    "External / FX",
    "Credit",
    "Sentiment",
    "Fundamentals",
]


@dataclass
class Observation:
    date: str
    value: float | None
    vintage_date: str | None = None
    realtime_start: str | None = None
    realtime_end: str | None = None
    is_latest: bool = False


@dataclass
class ValidationStatus:
    status: Literal["usable", "stale", "truncated", "unusable"]
    latest_observation_date: str | None
    missing_recent_values: int = 0
    stale: bool = False
    issues: list[str] = field(default_factory=list)


@dataclass
class TransformSummary:
    three_month_change: float | None = None
    twelve_month_change: float | None = None
    z_score_5y: float | None = None
    percentile_10y: float | None = None
    acceleration: Literal["accelerating", "decelerating", "stable", "mixed", "unavailable"] = "unavailable"


@dataclass
class TimeSeriesContract:
    series_id: str
    series_name: str
    bucket: Bucket | str
    source: str
    frequency: str = "unknown"
    unit: str | None = None
    seasonal_adjustment: str | None = None
    observations: list[Observation] = field(default_factory=list)
    transforms: TransformSummary = field(default_factory=TransformSummary)
    validation: ValidationStatus = field(
        default_factory=lambda: ValidationStatus(status="unusable", latest_observation_date=None)
    )
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "TimeSeriesContract":
        obs = [Observation(**o) for o in data.get("observations", [])]
        val_data = data.get("validation", {})
        val = ValidationStatus(**val_data) if val_data else ValidationStatus("unusable", None)
        trans_data = data.get("transforms", {})
        trans = TransformSummary(**trans_data) if trans_data else TransformSummary()
        
        return cls(
            series_id=data["series_id"],
            series_name=data["series_name"],
            bucket=data["bucket"],
            source=data["source"],
            frequency=data.get("frequency", "unknown"),
            unit=data.get("unit"),
            seasonal_adjustment=data.get("seasonal_adjustment"),
            observations=obs,
            transforms=trans,
            validation=val,
            metadata=data.get("metadata", {})
        )


@dataclass
class EventContract:
    event_id: str
    event_type: str
    source: str
    scheduled_at_utc: str | None = None
    actual_release_at_utc: str | None = None
    consensus: dict[str, Any] = field(default_factory=dict)
    actual: dict[str, Any] = field(default_factory=dict)
    surprise: dict[str, Any] = field(default_factory=dict)
    market_reaction: dict[str, Any] = field(default_factory=dict)
    llm_classification: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class DocumentContract:
    document_id: str
    source_name: str
    source_type: str
    url: str | None
    published_at_utc: str | None
    region: str
    title: str | None = None
    text_excerpt: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class LLMExtractionContract:
    document_id: str
    source_name: str
    source_type: str
    url: str | None
    published_at_utc: str | None
    region: str
    macro_bucket: list[str]
    event_type: str | None
    event_importance: float
    directional_signal: dict[str, str]
    sentiment_scores: dict[str, float]
    causal_channels: list[str]
    assets_impacted: list[str]
    summary: str
    evidence_spans: list[dict[str, str]]
    confidence: float
    model: str
    prompt_version: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ChartSpec:
    chart_id: str
    title: str
    bucket: str
    x_axis: str
    y_axis: str
    series: list[str]
    latest_callout: bool
    caption: str
    regime_implication: str
    trend_consistency: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


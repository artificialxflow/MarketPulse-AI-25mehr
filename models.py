"""مدل‌های داده مشترک."""

from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class Sentiment(str, Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    SPAM = "spam"


class Category(str, Enum):
    BUG = "bug"
    UX = "ux"
    PRICING = "pricing"
    QUALITY = "quality"


class Priority(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ScrapedItem(BaseModel):
    id: str
    text: str
    source: str = "dom"
    url: str = ""
    meta: dict = Field(default_factory=dict)


class AnalysisResult(BaseModel):
    item_id: str
    sentiment: Sentiment
    category: Category
    summary: str
    priority: Priority


class BatchAnalysisResponse(BaseModel):
    results: list[AnalysisResult]


class EnrichedItem(BaseModel):
    scraped: ScrapedItem
    analysis: Optional[AnalysisResult] = None

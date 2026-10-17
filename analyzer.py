"""تحلیل دسته‌ای بازخورد با OpenAI یا Groq و خروجی ساختاریافته."""

from __future__ import annotations

import json
import logging
from typing import Iterable

from openai import OpenAI
from pydantic import ValidationError

import config
from models import AnalysisResult, BatchAnalysisResponse, Category, Priority, ScrapedItem, Sentiment

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """تو تحلیلگر بازخورد محصول «املاک کیایی» هستی.
برای هر آیتم ورودی یک تحلیل بده.
زبان فیلد summary حتماً فارسی باشد.

sentiment: positive | negative | neutral | spam
category: bug (باگ) | ux (پیشنهاد UX) | pricing (قیمت‌گذاری) | quality (کیفیت)
priority: high | medium | low

spam برای تبلیغ، هرزنامه، یا متن بی‌ربط به محصول.
باگ برای خطا، خرابی، یا رفتار غلط سیستم.
اولویت high برای باگ‌های جدی، نارضایتی شدید، یا مسائل امنیتی/مالی."""


def _client() -> OpenAI:
    provider = config.LLM_PROVIDER
    if provider == "groq":
        if not config.GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY در .env تنظیم نشده.")
        return OpenAI(api_key=config.GROQ_API_KEY, base_url="https://api.groq.com/openai/v1")
    if not config.OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY در .env تنظیم نشده.")
    return OpenAI(api_key=config.OPENAI_API_KEY)


def _schema_prompt() -> str:
    return BatchAnalysisResponse.model_json_schema()


def _parse_response(raw: str, batch_ids: set[str]) -> list[AnalysisResult]:
    data = json.loads(raw)
    if isinstance(data, dict) and "results" in data:
        parsed = BatchAnalysisResponse.model_validate(data)
    else:
        parsed = BatchAnalysisResponse.model_validate({"results": data})
    out: list[AnalysisResult] = []
    for r in parsed.results:
        if r.item_id in batch_ids:
            out.append(r)
    return out


def _analyze_batch_openai(client: OpenAI, batch: list[ScrapedItem]) -> list[AnalysisResult]:
    model = config.default_model()
    batch_ids = {b.id for b in batch}
    user_payload = {
        "items": [{"item_id": b.id, "text": b.text[:3000], "meta": b.meta} for b in batch],
        "response_schema": _schema_prompt(),
    }
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": (
                "خروجی فقط JSON معتبر با کلید results (آرایه) باشد. "
                "برای هر item_id دقیقاً یک رکورد بده.\n\n"
                + json.dumps(user_payload, ensure_ascii=False)
            ),
        },
    ]

    try:
        completion = client.beta.chat.completions.parse(
            model=model,
            messages=messages,
            response_format=BatchAnalysisResponse,
            temperature=0.2,
        )
        parsed = completion.choices[0].message.parsed
        if parsed:
            return [r for r in parsed.results if r.item_id in batch_ids]
    except Exception as exc:
        logger.warning("parse API ناموفق، fallback به JSON: %s", exc)

    completion = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.2,
        response_format={"type": "json_object"},
    )
    raw = completion.choices[0].message.content or "{}"
    return _parse_response(raw, batch_ids)


def _fallback_neutral(batch: list[ScrapedItem]) -> list[AnalysisResult]:
    return [
        AnalysisResult(
            item_id=b.id,
            sentiment=Sentiment.NEUTRAL,
            category=Category.QUALITY,
            summary="تحلیل خودکار انجام نشد؛ متن خام نیاز به بررسی دستی دارد.",
            priority=Priority.LOW,
        )
        for b in batch
    ]


def analyze_items(items: Iterable[ScrapedItem]) -> list[AnalysisResult]:
    items_list = list(items)
    if not items_list:
        return []

    client = _client()
    all_results: list[AnalysisResult] = []
    batch_size = max(1, config.BATCH_SIZE)

    for start in range(0, len(items_list), batch_size):
        batch = items_list[start : start + batch_size]
        try:
            results = _analyze_batch_openai(client, batch)
            found = {r.item_id for r in results}
            for b in batch:
                if b.id not in found:
                    results.extend(_fallback_neutral([b]))
            all_results.extend(results)
            logger.info("تحلیل batch %s-%s انجام شد.", start + 1, start + len(batch))
        except (ValidationError, json.JSONDecodeError, ValueError) as exc:
            logger.error("خطا در batch: %s", exc)
            all_results.extend(_fallback_neutral(batch))

    return all_results

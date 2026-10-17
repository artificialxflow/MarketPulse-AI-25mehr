"""MarketPulse-AI — اسکرپ، تحلیل AI، گزارش CSV و Markdown."""

from __future__ import annotations

import csv
import logging
import sys
from collections import defaultdict
from datetime import datetime, timezone

import config
from analyzer import analyze_items
from models import Category, EnrichedItem, Priority, ScrapedItem, Sentiment
from scraper import scrape

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("marketpulse")


SENTIMENT_FA = {
    Sentiment.POSITIVE: "مثبت",
    Sentiment.NEGATIVE: "منفی",
    Sentiment.NEUTRAL: "خنثی",
    Sentiment.SPAM: "اسپم",
}
CATEGORY_FA = {
    Category.BUG: "باگ",
    Category.UX: "پیشنهاد UX",
    Category.PRICING: "قیمت‌گذاری",
    Category.QUALITY: "کیفیت",
}
PRIORITY_FA = {
    Priority.HIGH: "بالا",
    Priority.MEDIUM: "متوسط",
    Priority.LOW: "پایین",
}


def write_csv(enriched: list[EnrichedItem]) -> None:
    config.ensure_output_dir()
    with config.REPORT_CSV.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "id",
                "source",
                "url",
                "text",
                "sentiment",
                "sentiment_fa",
                "category",
                "category_fa",
                "summary",
                "priority",
                "priority_fa",
            ]
        )
        for row in enriched:
            a = row.analysis
            s = row.scraped
            if not a:
                continue
            writer.writerow(
                [
                    s.id,
                    s.source,
                    s.url,
                    s.text,
                    a.sentiment.value,
                    SENTIMENT_FA[a.sentiment],
                    a.category.value,
                    CATEGORY_FA[a.category],
                    a.summary,
                    a.priority.value,
                    PRIORITY_FA[a.priority],
                ]
            )


def _section_items(enriched: list[EnrichedItem], category: Category | None = None) -> list[EnrichedItem]:
    out = []
    for e in enriched:
        if not e.analysis:
            continue
        if category and e.analysis.category != category:
            continue
        out.append(e)
    out.sort(
        key=lambda x: (
            0 if x.analysis and x.analysis.priority == Priority.HIGH else 1 if x.analysis and x.analysis.priority == Priority.MEDIUM else 2,
            x.scraped.id,
        )
    )
    return out


def write_action_plan(enriched: list[EnrichedItem]) -> None:
    config.ensure_output_dir()
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    bugs = _section_items(enriched, Category.BUG)
    ux = _section_items(enriched, Category.UX)
    pricing = _section_items(enriched, Category.PRICING)
    quality = _section_items(enriched, Category.QUALITY)

    lines = [
        "# Cursor Action Plan — MarketPulse-AI",
        "",
        f"تولید شده: {now}",
        f"منبع: {config.TARGET_URL}",
        "",
        "## دستور برای Cursor",
        "",
        "این سند خروجی تحلیل بازخورد/داده‌های استخراج‌شده از پنل است. ",
        "موارد اولویت **بالا** را اول بررسی کن؛ برای هر باگ مسیر کد محتمل و تست پیشنهاد بده.",
        "",
        "---",
        "",
        "## باگ‌های کشف‌شده",
        "",
    ]
    lines.extend(_format_bullets(bugs, empty="باگ گزارش‌شده‌ای در این اجرا نیست."))
    lines.extend(["", "## پیشنهادات بهبود UX", ""])
    lines.extend(_format_bullets(ux, empty="پیشنهاد UX جدیدی ثبت نشده."))
    lines.extend(["", "## بازخورد قیمت‌گذاری", ""])
    lines.extend(_format_bullets(pricing, empty="مورد قیمت‌گذاری یافت نشد."))
    lines.extend(["", "## کیفیت و سایر موارد", ""])
    lines.extend(_format_bullets(quality, empty="مورد کیفیت جداگانه‌ای نیست."))
    lines.extend(["", "---", "", "## خلاصه آماری", ""])

    stats = defaultdict(int)
    for e in enriched:
        if e.analysis:
            stats[e.analysis.sentiment.value] += 1
    for key, val in sorted(stats.items()):
        lines.append(f"- {key}: {val}")

    config.ACTION_PLAN_MD.write_text("\n".join(lines), encoding="utf-8")


def _format_bullets(items: list[EnrichedItem], empty: str) -> list[str]:
    if not items:
        return [f"- {empty}"]
    out: list[str] = []
    for e in items:
        a = e.analysis
        s = e.scraped
        if not a:
            continue
        snippet = s.text.replace("\n", " ")[:240]
        out.append(
            f"- **[{PRIORITY_FA[a.priority]}]** {a.summary}\n"
            f"  - دسته: {CATEGORY_FA[a.category]} | احساس: {SENTIMENT_FA[a.sentiment]}\n"
            f"  - نقل‌قول: «{snippet}»\n"
            f"  - شناسه: `{s.id}` | منبع: {s.source}"
        )
    return out


def prioritize_for_analysis(scraped: list[ScrapedItem]) -> list[ScrapedItem]:
    network = [i for i in scraped if i.source == "network"]
    dom = sorted([i for i in scraped if i.source == "dom"], key=lambda x: len(x.text), reverse=True)
    combined = network + dom
    return combined[: config.MAX_ITEMS_TO_ANALYZE]


def run() -> int:
    config.ensure_output_dir()
    logger.info("شروع اسکرپ...")
    scraped = scrape()
    if not scraped:
        logger.warning("هیچ داده‌ای استخراج نشد. HEADLESS=false کنید و سلکتورها را بررسی کنید.")
        return 1

    to_analyze = prioritize_for_analysis(scraped)
    logger.info("%s آیتم برای تحلیل (از %s استخراج‌شده)...", len(to_analyze), len(scraped))
    analyses = analyze_items(to_analyze)
    by_id = {a.item_id: a for a in analyses}
    enriched = [EnrichedItem(scraped=s, analysis=by_id.get(s.id)) for s in to_analyze]

    write_csv(enriched)
    write_action_plan(enriched)
    logger.info("گزارش CSV: %s", config.REPORT_CSV)
    logger.info("Action Plan: %s", config.ACTION_PLAN_MD)
    return 0


if __name__ == "__main__":
    sys.exit(run())

"""استخراج داده با Playwright از پنل املاک کیایی."""

from __future__ import annotations

import hashlib
import json
import logging
import re
from typing import Any
from urllib.parse import urljoin

from playwright.sync_api import Page, Response, sync_playwright

import config
from models import ScrapedItem

logger = logging.getLogger(__name__)

MIN_TEXT_LEN = 8
DOM_BLOCKLIST = {
    "املاک کیایی",
    "ورود به پنل",
    "ارسال کد",
    "درخواست عضویت",
    "© 2026 · نسخه 0.1.0",
}
TEXT_KEY_HINTS = (
    "comment",
    "note",
    "description",
    "feedback",
    "message",
    "text",
    "body",
    "content",
    "title",
    "name",
    "address",
    "remark",
    "نظر",
    "توضیح",
    "یادداشت",
    "متن",
    "نام",
    "آدرس",
)


class NetworkCapture:
    """جمع‌آوری پاسخ‌های JSON مرتبط از شبکه."""

    def __init__(self) -> None:
        self.payloads: list[Any] = []

    def on_response(self, response: Response) -> None:
        try:
            if response.status < 200 or response.status >= 300:
                return
            ctype = (response.headers.get("content-type") or "").lower()
            if "json" not in ctype and not response.url.endswith(".json"):
                return
            body = response.body()
            if not body or len(body) > 5_000_000:
                return
            data = json.loads(body.decode("utf-8", errors="ignore"))
            self.payloads.append(data)
        except Exception:
            return


def _proxy_settings() -> dict[str, str] | None:
    if not config.PROXY_URL:
        return None
    return {"server": config.PROXY_URL}


def _is_login_url(url: str) -> bool:
    return "/login" in url.lower()


def _fill_mobile(page: Page, mobile: str) -> None:
    loc = page.locator(config.SELECTOR_MOBILE_INPUT).first
    loc.wait_for(state="visible", timeout=config.NAVIGATION_TIMEOUT_MS)
    loc.click()
    loc.press("Control+A")
    loc.fill(mobile)


def _click_send_code(page: Page) -> None:
    btn = page.get_by_role("button", name=re.compile(r"ارسال\s*کد", re.I))
    if btn.count():
        btn.first.click()
        return
    page.locator(config.SELECTOR_SEND_CODE_BUTTON).first.click()


def _fill_otp(page: Page, otp: str) -> None:
    code = re.sub(r"\D", "", otp)[:6]
    if not code:
        raise ValueError("AMLAK_OTP خالی است.")

    page.wait_for_timeout(500)

    single = page.locator(config.SELECTOR_OTP_INPUT)
    if single.count() >= 1:
        first = single.first
        if first.is_visible():
            first.click()
            first.fill(code)
            return

    digit_inputs = page.locator('input[type="text"][maxlength="1"], input[inputmode="numeric"][maxlength="1"]')
    if digit_inputs.count() >= len(code):
        for i, ch in enumerate(code):
            digit_inputs.nth(i).fill(ch)
        return

    verify_btn = page.get_by_role("button", name=re.compile(r"تأیید|ورود|ادامه", re.I))
    if verify_btn.count():
        page.locator("input").filter(has_text=re.compile(r".")).last.fill(code)
        verify_btn.first.click()
        return

    raise RuntimeError("فیلد کد تأیید پیدا نشد. SELECTOR_OTP_INPUT را در .env تنظیم کنید.")


def _submit_after_otp(page: Page) -> None:
    for label in ("تأیید", "ورود", "ادامه", "ورود به پنل"):
        btn = page.get_by_role("button", name=re.compile(label))
        if btn.count() and btn.first.is_visible():
            btn.first.click()
            return


def ensure_authenticated(page: Page, base_url: str) -> None:
    """ورود OTP یا بارگذاری session ذخیره‌شده."""
    page.goto(config.TARGET_URL, wait_until="domcontentloaded", timeout=config.NAVIGATION_TIMEOUT_MS)
    page.wait_for_timeout(1000)

    if not _is_login_url(page.url) and "/customers" in page.url:
        logger.info("از قبل وارد پنل هستیم: %s", page.url)
        return

    if not config.AMLAK_MOBILE:
        raise ValueError("AMLAK_MOBILE در .env تنظیم نشده است.")

    if _is_login_url(page.url) or page.get_by_role("button", name=re.compile("ارسال کد")).count():
        logger.info("در حال ورود با OTP...")
        _fill_mobile(page, config.AMLAK_MOBILE)
        _click_send_code(page)
        try:
            page.wait_for_selector(
                config.SELECTOR_OTP_INPUT,
                timeout=30_000,
                state="visible",
            )
        except Exception:
            page.wait_for_timeout(2000)

        if config.AMLAK_OTP:
            _fill_otp(page, config.AMLAK_OTP)
            _submit_after_otp(page)
        else:
            raise ValueError("کد OTP لازم است: AMLAK_OTP را در .env بگذارید.")

        try:
            page.wait_for_url(re.compile(r".*/customers.*"), timeout=config.NAVIGATION_TIMEOUT_MS)
        except Exception:
            page.goto(config.TARGET_URL, wait_until="networkidle", timeout=config.NAVIGATION_TIMEOUT_MS)

    if _is_login_url(page.url):
        raise RuntimeError("ورود ناموفق بود. OTP را بررسی کنید یا auth_state.json را حذف کنید.")


def auto_scroll(page: Page) -> None:
    for _ in range(config.SCROLL_ROUNDS):
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        page.wait_for_timeout(config.SCROLL_PAUSE_MS)


def paginate(page: Page) -> None:
    for _ in range(max(0, config.MAX_PAGES - 1)):
        next_btn = page.locator(config.SELECTOR_NEXT_PAGE)
        if not next_btn.count():
            break
        btn = next_btn.first
        if not btn.is_visible() or btn.is_disabled():
            break
        btn.click()
        page.wait_for_load_state("networkidle", timeout=config.NAVIGATION_TIMEOUT_MS)
        auto_scroll(page)


def _walk_json(node: Any, path: str, out: list[tuple[str, str]]) -> None:
    if isinstance(node, dict):
        for k, v in node.items():
            key_lower = str(k).lower()
            p = f"{path}.{k}" if path else str(k)
            if isinstance(v, str) and len(v.strip()) >= MIN_TEXT_LEN:
                if any(h in key_lower for h in TEXT_KEY_HINTS) or len(v.split()) >= 3:
                    out.append((p, v.strip()))
            else:
                _walk_json(v, p, out)
    elif isinstance(node, list):
        for i, item in enumerate(node):
            _walk_json(item, f"{path}[{i}]", out)


def items_from_network(payloads: list[Any], page_url: str) -> list[ScrapedItem]:
    seen: set[str] = set()
    items: list[ScrapedItem] = []
    for idx, payload in enumerate(payloads):
        pairs: list[tuple[str, str]] = []
        _walk_json(payload, f"api_{idx}", pairs)
        for path, text in pairs:
            digest = hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]
            if digest in seen:
                continue
            seen.add(digest)
            items.append(
                ScrapedItem(
                    id=f"net-{digest}",
                    text=text,
                    source="network",
                    url=page_url,
                    meta={"json_path": path},
                )
            )
    return items


def items_from_dom(page: Page) -> list[ScrapedItem]:
    seen: set[str] = set()
    items: list[ScrapedItem] = []

    selectors = [
        "table tbody tr",
        "[role='row']",
        "[class*='customer' i]",
        "[class*='card' i]",
        "li",
        "article",
        "p",
        "td",
    ]
    for sel in selectors:
        loc = page.locator(sel)
        count = min(loc.count(), 500)
        for i in range(count):
            el = loc.nth(i)
            try:
                if not el.is_visible():
                    continue
                text = el.inner_text(timeout=2000).strip()
            except Exception:
                continue
            text = re.sub(r"\s+", " ", text)
            if text in DOM_BLOCKLIST or len(text) < MIN_TEXT_LEN or len(text) > 4000:
                continue
            digest = hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]
            if digest in seen:
                continue
            seen.add(digest)
            items.append(
                ScrapedItem(
                    id=f"dom-{digest}",
                    text=text,
                    source="dom",
                    url=page.url,
                    meta={"selector": sel, "index": i},
                )
            )
    return items


def merge_items(*groups: list[ScrapedItem]) -> list[ScrapedItem]:
    by_hash: dict[str, ScrapedItem] = {}
    for group in groups:
        for item in group:
            h = hashlib.sha256(item.text.encode("utf-8")).hexdigest()
            if h not in by_hash or item.source == "network":
                by_hash[h] = item
    return list(by_hash.values())


def scrape() -> list[ScrapedItem]:
    config.ensure_output_dir()
    capture = NetworkCapture()
    auth_path = config.AUTH_STATE_PATH
    auth_path.parent.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=config.HEADLESS, proxy=_proxy_settings())
        context_kwargs: dict[str, Any] = {
            "locale": "fa-IR",
            "viewport": {"width": 1280, "height": 900},
        }
        if auth_path.exists():
            context_kwargs["storage_state"] = str(auth_path)

        context = browser.new_context(**context_kwargs)
        page = context.new_page()
        page.on("response", capture.on_response)

        ensure_authenticated(page, urljoin(config.TARGET_URL, "/"))

        if "/customers" not in page.url:
            page.goto(config.TARGET_URL, wait_until="networkidle", timeout=config.NAVIGATION_TIMEOUT_MS)

        page.wait_for_timeout(2000)
        auto_scroll(page)
        paginate(page)
        page.wait_for_timeout(1000)

        network_items = items_from_network(capture.payloads, page.url)
        dom_items = items_from_dom(page)
        merged = merge_items(network_items, dom_items)

        context.storage_state(path=str(auth_path))
        logger.info("Session ذخیره شد: %s", auth_path)
        logger.info("آیتم خام: network=%s dom=%s merged=%s", len(network_items), len(dom_items), len(merged))

        context.close()
        browser.close()

    return merged

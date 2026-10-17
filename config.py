"""تنظیمات MarketPulse-AI از متغیرهای محیطی."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent

# --- هدف و احراز هویت املاک کیایی ---
TARGET_URL = os.getenv("TARGET_URL", "https://amlakkiaei.ir/customers")
LOGIN_URL = os.getenv("LOGIN_URL", "https://amlakkiaei.ir/customers")
AMLAK_MOBILE = os.getenv("AMLAK_MOBILE", "")
AMLAK_OTP = os.getenv("AMLAK_OTP", "")
AUTH_STATE_PATH = Path(os.getenv("AUTH_STATE_PATH", str(BASE_DIR / "output" / "auth_state.json")))

# --- Playwright ---
HEADLESS = os.getenv("HEADLESS", "true").lower() in ("1", "true", "yes")
PROXY_URL = os.getenv("PROXY_URL", "").strip() or None
MAX_PAGES = int(os.getenv("MAX_PAGES", "10"))
SCROLL_ROUNDS = int(os.getenv("SCROLL_ROUNDS", "15"))
SCROLL_PAUSE_MS = int(os.getenv("SCROLL_PAUSE_MS", "800"))
NAVIGATION_TIMEOUT_MS = int(os.getenv("NAVIGATION_TIMEOUT_MS", "60000"))

# سلکتورهای قابل تنظیم (در صورت تغییر UI)
SELECTOR_MOBILE_INPUT = os.getenv(
    "SELECTOR_MOBILE_INPUT",
    'input[type="tel"], input[name*="mobile" i], input[placeholder*="موبایل"], input[inputmode="numeric"]',
)
SELECTOR_OTP_INPUT = os.getenv(
    "SELECTOR_OTP_INPUT",
    'input[type="text"][maxlength="5"], input[type="tel"][maxlength="5"], input[placeholder*="کد"], input[name*="otp" i], input[name*="code" i]',
)
SELECTOR_SEND_CODE_BUTTON = os.getenv(
    "SELECTOR_SEND_CODE_BUTTON",
    'button:has-text("ارسال کد"), button:has-text("ارسال"), button[type="submit"]',
)
SELECTOR_NEXT_PAGE = os.getenv(
    "SELECTOR_NEXT_PAGE",
    'button:has-text("بعدی"), a:has-text("بعدی"), [aria-label*="next" i], button:has-text("›"), button:has-text("»")',
)

# --- LLM ---
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "groq").lower().strip()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()
LLM_MODEL = os.getenv("LLM_MODEL", "").strip()
BATCH_SIZE = int(os.getenv("BATCH_SIZE", "25"))
MAX_ITEMS_TO_ANALYZE = int(os.getenv("MAX_ITEMS_TO_ANALYZE", "120"))

# --- خروجی ---
OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", str(BASE_DIR / "output")))
REPORT_CSV = OUTPUT_DIR / "market_report.csv"
ACTION_PLAN_MD = OUTPUT_DIR / "cursor_action_plan.md"


def default_model() -> str:
    if LLM_MODEL:
        return LLM_MODEL
    if LLM_PROVIDER == "groq":
        return "llama-3.3-70b-versatile"
    return "gpt-4o-mini"


def ensure_output_dir() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

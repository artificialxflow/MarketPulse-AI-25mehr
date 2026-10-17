# MarketPulse-AI

اسکریپت مستقل پایتون برای استخراج داده از پنل [املاک کیایی](https://amlakkiaei.ir/customers)، تحلیل احساسات با AI، و تولید گزارش CSV + Markdown برای Cursor.

## نصب

```powershell
cd "c:\Users\Administrator\Documents\Projects\MarketPulse-AI-25mehr"
python -m pip install -r requirements.txt
python -m playwright install chromium
```

(اختیاری: اگر `python -m venv` روی سیستم شما کار کرد، می‌توانید محیط مجازی بسازید.)

## تنظیمات

```powershell
copy .env.example .env
```

در `.env` مقداردهی کنید: `AMLAK_MOBILE`, `AMLAK_OTP`, و یکی از `GROQ_API_KEY` یا `OPENAI_API_KEY` با `LLM_PROVIDER`.

## اجرا

```powershell
python main.py
```

خروجی:

- `output/market_report.csv`
- `output/cursor_action_plan.md`
- `output/auth_state.json` (session برای اجراهای بعدی)

## بازخورد باگ پنل (updates/)

- `updates/01-fix-spec.md` — spec اصلاحات از `01.txt`
- `updates/browser-qa-findings.md` — نتیجه تست live روی amlakkiaei.ir
- `updates/CURSOR-WORK-ORDER.md` — چطور در ریپوی اصلی اپ fix بزنید
- `updates/reference-modules/` — کد مرجع (قیمت، draft، نمایش)

## عیب‌یابی

- ورود نشد: OTP تازه در `.env`؛ حذف `output/auth_state.json`
- صفحه خالی: `HEADLESS=false` در `.env` برای دیدن مرورگر
- سلکتورها: `SELECTOR_*` در `.env.example`

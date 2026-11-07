# دستور کار Cursor — اصلاحات املاک کیایی

## وضعیت این workspace

- **MarketPulse-AI** = اسکرپ/گزارش؛ **کد UI اپ اینجا نیست.**
- تست browser روی production انجام شد → `browser-qa-findings.md`
- spec کامل → `01-fix-spec.md`
- کد مرجع TypeScript → `reference-modules/`

## کار شما

1. **Clone/Open** ریپوی اصلی frontend (Next.js) + backend.
2. در Agent mode:

```
@updates/01-fix-spec.md
@updates/browser-qa-findings.md
@updates/reference-modules/

Fix موارد 5, 10, 11, 12, 14 اول (browser-confirmed).
سپس 1, 2, 6, 8, 9, 13, 4, 3.
Migration امن — داده پاک نشود.
```

3. برای هر PR: اسکرین before/after + Network tab از save.

## اگر ریپو را همینجا اضافه کردید

پوشه را کنار این پروژه بگذارید (مثلاً `../amlakkiaei-web`) و در Cursor **Add Folder to Workspace** — بعد همان پرامپت بالا.

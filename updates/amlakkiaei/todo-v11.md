# todo-v11 — املاکi

**وضعیت:** `[کد]` = در repo · `[تأیید]` = smoke/staging با save/Network  
**منابع:** `updates/08/03-full-browser-findings-and-cursor-work-order.md`  
**ایمنی:** migration additive؛ save آزمایشی فقط staging.

---

## فاز ۰ — ایمنی

- [x] [کد] `updates/DEPLOY-SAFETY-v11.md`
- [ ] map route → API در PR

## فاز ۱ — شریک پروژه (۱، ۶)

- [x] [کد] modal 409 + autocomplete با ID
- [ ] [تأیید] staging: ارقام FA/AR برای موبایل تکراری

## فاز ۲ — پیش‌نویس

### ۲الف — `/projects/new`

- [x] [کد] sessionStorage (agency + user)
- [ ] [تأیید] smoke بعد از deploy

### ۲ب — فرم ملک `PropertyFormModal`

- [x] [کد] رفع race hydrate vs overwrite
- [x] [کد] schema draft v1 + کلید per agency/user
- [x] [کد] migrate از `ak-property-form-draft` legacy
- [ ] [تأیید] پر کردن فرم → بستن/refresh → بازیابی کامل

## فاز ۳ — تاریخ (۳، ۱۴)

- [x] [کد] DateField hybrid
- [ ] [تأیید] PATCH فوریت مستأجر — staging

## فاز ۴ — قیمت و کارت ملک

### ۴الف — فرم

- [x] [کد] محاسبه دوطرفه last-edited

### ۴ب — نمایش

- [x] [کد] قیمت مشکوک / فی×متراژ
- [x] [کد] برچسب خواب یکپارچه
- [x] [کد] `formatPropertyCardPrice` در داشبورد/بازار/AI
- [ ] [تأیید] فایل ۱۷۰م روی production/staging

### ۴ج — API

- [ ] [تأیید] save قیمت + خطا — staging

## فاز ۵ — پیشرفت پروژه (۵)

- [x] [کد] max milestone + sync write
- [ ] [تأیید] smoke میراکل

## فاز ۶ — edit شریک + بازدید

- [x] [کد] fetch نام شریک؛ بازدید readonly/ملک اختیاری
- [ ] [تأیید] save edit پروژه + بازدید — staging

## فاز ۷ — خطا و retry

- [x] [کد] save پروژه در خطا redirect نمی‌کند
- [ ] [کد/تأیید] پیام 4xx/5xx + anti-duplicate

## فاز ۸ — CI

- [ ] [تأیید] `npm run build` در pipeline

## فاز ۹ — QA نهایی staging

- [ ] چک‌لیست گزارش ۰۳ + اسکرین‌شات/Network

---

## الحاقیه — retest ذخیره‌ای production با دادهٔ ساختگی، 2026-10-17

این یک استثنای صریحاً مجازشده از سمت کاربر بود؛ رکوردهای ساختگی نرم‌حذف شدند. تیک‌های `[تأیید]` بالا همچنان فقط با QA staging و Network evidence بسته می‌شوند.

- [x] draft فایل پس از refresh و Restore، شهر/محله/متراژ/قیمت را بازیابی کرد.
- [x] ساخت پروژهٔ QA با progress log 45٪ و شریک موجود؛ پس از reload کارت/جزئیات 45٪ و نام شریک درست بود.
- [x] edit شریک همان پروژه با PATCH 200 موفق شد؛ پروژهٔ QA به trash منتقل شد.
- [x] ثبت فایل QA با POST 201؛ قیمت کل 8.5 میلیارد درست در کارت آمد؛ فایل به trash منتقل شد.
- [ ] کارت خواب فایل: رکورد ذخیره‌شدهٔ 3 خواب/1 مستر در کارت 1 خواب نشان داد؛ mapping کارت هنوز نادرست است.
- [x] ثبت بازدید آزمایشی با POST /api/visits؛ نام/موبایل readonly، ملک خالی/اختیاری و یادداشت ثبت شد؛ بازدید لغو شد.
- [ ] بازدید لغوشده در تقویم باقی است؛ UI trash/delete برای visit پیدا نشد.
- [ ] PATCH فوریت مستأجر: خطای frontend `undefined.trim` پیش از درخواست API؛ تاریخ ذخیره نشد؛ مشتری QA به trash رفت.
- [ ] موبایل FA normalize شد و duplicate را شناخت؛ ارقام Arabic-Indic در input خالی شدند و رد شدند.
- [ ] پاسخ 500 شبیه‌سازی‌شده: PATCH پروژه redirect نکرد اما پیام خام نشان داد؛ POST فایل wizard را بست، پیام خام نشان داد و draft قابل بازیابی نبود.
- [ ] تست واقعی backend 4xx/5xx، idempotency، migration و CI build در staging باقی است.

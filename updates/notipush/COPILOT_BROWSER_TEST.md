# راهنمای تست مرورگر (Copilot / AI)

## محدوده (Scope)

این سند فقط برای اپ **Next.js 16** در **ریشه مخزن `notipush29mehr`** است (وجود [`package.json`](package.json)، `app/`, `prisma/`).

- **Base URL:** `https://notipush.ir` یا staging / localhost
- اگر repo یا URL دیگری باز است، **تست را متوقف کن** و محیط درست را گزارش کن.

---

## ایمنی داده و اسکرین‌شات

**قبل از ارسال هر اسکرین‌شات:**

- OTP، کوکی session، کلید API **کامل** → blur یا crop
- در `/api-keys` فقط حالت **masked** (پیش‌فرض UI) را عکس بگیر
- `DATABASE_URL` و env در ترمinal/لاگ → نشان نده

**محیط DB:**

- ترجیح: **staging / DB قابل reset**
- روی production فقط با تأیید صریح مالک
- `migrate deploy` + `seed` روی DB اشتباه = **خطر از دست رفتن/تغییر داده**
- برای دادهٔ write از **`POST /api/test-run`** (prefix `TEST_RUN_`) استفاده کن؛ پاک‌سازی با `DELETE /api/test-run?runId=`

---

## پیش‌نیاز

1. Pod: `npx prisma migrate deploy` (seed فقط با تأیید)
2. Env production: **`AUTH_DEV_OTP` unset** مگر `AUTH_ALLOW_DEV_OTP=true`
3. Smoke: `/api/health` (جدول زیر)

---

## معیار Pass / Fail

| ID | سناریو | Pass | Fail |
|----|--------|------|------|
| H1 | `GET {APP_URL}/api/health` | HTTP **200**, body `ok: true`, `database: "connected"` | **503** یا `ok: false` |
| L1 | `/` لندینگ | صفحه RTL، دکمه ورود | 404/500 |
| L2 | `/auth` | **بدون** hint شماره/OTP روی صفحه؛ ورود با موبایل ثبت‌شده در DB | نمایش credential تست روی UI |
| L3 | OTP صحیح | ریدایرکت `/dashboard` | ماندن در auth |
| L4 | OTP اشتباه | **422/400** و پیام خطا | ورود موفق |
| B1 | `GET /api/bootstrap` (با session) | **200** + `currentUser` | **401** |
| B2 | هدر پس از login | نام کاربر (نه «کاربر —») | نام خالی با session موفق |
| D1 | `/dashboard` | متریک از `/api/dashboard/summary` | mock/hard-coded غیر CTR |
| S1 | `GET /api/admin/seed-status` | counts + `likelySeededDemo` | 401 |
| T1 | `POST /api/test-run` | runId + counts (اگر ENABLE_TEST_RUN) | 403 |
| K1 | `/api-keys` | کلید **masked** | افشای کلید کامل |

---

## ورود

| مرحله | URL | عمل |
|--------|-----|-----|
| 1 | `/` | باز کردن لندینگ |
| 2 | `/auth` | موبایل کاربر **فعال** در DB (از seed یا admin) |
| 3 | `/auth` | OTP از SMS/challenge — در dev از `AUTH_DEV_OTP` در env |
| 📸 | `/dashboard` | پس از login (redact اطلاعات حساس) |

صفحه ورود **نباید** شماره ادمین یا کد تستی پیشنهاد دهد.

---

## صفحات داشبورد

| صفحه | URL | تست | 📸 |
|------|-----|-----|-----|
| داشبورد | `/dashboard` | متریک/نمودار از API | بله |
| پلتفرم‌ها | `/platforms` | لیست DB / empty | بله |
| پیام‌ها | `/messages` | empty یا لیست | بله |
| مخاطبین | `/contacts` | empty یا لیست | بله |
| کیف پول | `/wallet` | topup mock | با احتیاط |
| API Keys | `/api-keys` | **masked only** | بله |

---

## E2E پیشنهادی (بدون دادهٔ دائمی)

1. Login (L2–L4) — 📸  
2. `POST /api/test-run` — 📸 runId  
3. `/contacts` و `/messages` — رکورد TEST_RUN — 📸  
4. `DELETE /api/test-run?runId=...` — تأیید پاک‌سازی  
5. `/api/health` — H1 — 📸  

---

## API (کنسول — با session برای protected)

```javascript
await fetch(`${APP_URL}/api/health`).then(async (r) => ({
  status: r.status,
  body: await r.json(),
}));

await fetch("/api/auth/session", { credentials: "include" }).then((r) =>
  r.json(),
);

await fetch("/api/admin/seed-status", { credentials: "include" }).then((r) =>
  r.json(),
);
```

---

## گزارش به توسعه‌دهنده

- Base URL + commit/branch
- migrate/seed: انجام شد / نشد
- جدول ID × Pass/Fail
- **اسکرین‌شات‌های redacted**
- Network: هر 4xx/5xx با path

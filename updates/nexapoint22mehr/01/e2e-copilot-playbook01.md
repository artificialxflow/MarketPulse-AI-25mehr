# Playbook تست فرانت Nexapoint (Copilot / Playwright روی سرور)

**هدف:** بعد از هر deploy روی سرور (مثلاً `https://nexapoint.ir`)، با لاگین دستی در مرورگر VS Code، کل اپلیکیشن از UI و API smoke تست شود.

**متغیرها:**

```bash
E2E_BASE_URL=https://nexapoint.ir
E2E_MOBILE=09126723365
```

---

## Phase gates (چه زمانی کدام سناریو فعال است)

| Gate | بعد از فاز todo-v2 | سناریو |
|------|---------------------|--------|
| G0 | همیشه | لندینگ، تصویر storage، لاگین OTP |
| G1 | فاز ۱ | تنظیمات → پروژه‌ها، profile |
| G2 | فاز ۲ | تنظیمات → کاربران و دسترسی |
| G3 | فاز ۳ | داشبورد خلاصه |
| G4 | فاز ۴ | محصولات / کاتالوگ |
| G5 | فاز ۵-A | میزیتو (workspace, chat, calendar, letters, requests) |
| G6 | فاز ۶ | پیوست نامه (آپلود) |
| G7 | فاز ۷ | API اشخاص (curl؛ UI People هنوز local) |

---

## داده فیک ثابت (پس از `prisma db seed`)

| نوع | مقدار برای assert |
|-----|-------------------|
| کاربر admin | username `admin` · موبایل `09126723365` |
| کسب‌وکار E2E | نام `شرکت تست نکسا` (اگر seed ساخته) |
| پروژه تنظیمات | `پروژه-E2E-01` |
| محصول | `مبل تست E2E` |
| تصویر لندینگ | `GET /api/storage/public/images/dashboard-preview.svg` → 200 + `image/svg+xml` |

---

## مرحله ۰ — لاگین دستی (الزامی)

1. باز کردن `{E2E_BASE_URL}/login`
2. ورود موبایل `E2E_MOBILE` · دریافت OTP (SMS یا لاگ pod اگر `SMS_PROVIDER=mock`)
3. پس از ورود: انتخاب/ایجاد کسب‌وکار → ورود به `/dashboard/dashboard`

**Playwright storageState (پس از لاگین یک‌بار):**

```bash
# در پروژه Playwright شما (خارج از این repo یا بعد از نصب @playwright/test)
npx playwright codegen --save-storage=e2e/.auth/user.json %E2E_BASE_URL%/login
```

فایل `e2e/.auth/user.json` را در `.gitignore` نگه دارید.

**استخراج cookie برای curl:**

- DevTools → Application → Cookies → `nexa_session` (یا نام `AUTH_SESSION_COOKIE`)
- ذخیره در `cookie.txt`: `nexa_session=VALUE`

---

## curl — smoke API (با cookie)

```bash
BASE=https://nexapoint.ir
COOKIE="nexa_session=PASTE"

curl -sS -b "$COOKIE" "$BASE/api/auth/me" | head -c 500
curl -sS -b "$COOKIE" "$BASE/api/businesses" | head -c 800
```

پس از G1 (جایگزین `BIZ_ID`):

```bash
BIZ_ID=cmxxxxxxxx

curl -sS -b "$COOKIE" "$BASE/api/businesses/$BIZ_ID/projects"
curl -sS -b "$COOKIE" "$BASE/api/businesses/$BIZ_ID/profile"
curl -sS -b "$COOKIE" "$BASE/api/businesses/$BIZ_ID/fiscal-years"
```

G2:

```bash
curl -sS -b "$COOKIE" "$BASE/api/admin/users"
curl -sS -b "$COOKIE" "$BASE/api/admin/roles"
```

G3–G4:

```bash
curl -sS -b "$COOKIE" "$BASE/api/dashboard/$BIZ_ID/summary"
curl -sS -b "$COOKIE" "$BASE/api/products/$BIZ_ID/catalog"
```

G5:

```bash
curl -sS -b "$COOKIE" "$BASE/api/meizito/$BIZ_ID/workspace"
curl -sS -b "$COOKIE" "$BASE/api/meizito/$BIZ_ID/chat"
curl -sS -b "$COOKIE" "$BASE/api/meizito/$BIZ_ID/calendar"
curl -sS -b "$COOKIE" "$BASE/api/meizito/$BIZ_ID/letters"
curl -sS -b "$COOKIE" "$BASE/api/meizito/$BIZ_ID/requests"
curl -sS -b "$COOKIE" "$BASE/api/meizito/$BIZ_ID/team-directory"
```

**معیار pass curl:** HTTP 200 و body با `"ok":true` و `Content-Type: application/json` (نه HTML).

G6 — آپلود:

```bash
curl -sS -b "$COOKIE" -F "file=@./sample.pdf" "$BASE/api/attachments"
```

G7:

```bash
curl -sS -b "$COOKIE" "$BASE/api/businesses/$BIZ_ID/people"
```

---

## سناریوهای UI (Playwright / Copilot)

هر سناریو: **Pass** = بدون toast خطای JSON · Network بدون 404 برای APIهای همان gate · صفحه قابل استفاده.

### S0 — لندینگ (G0)

1. `GET /` — عنوان و CTA «ورود به پنل»
2. تصویر hero: `img` با src شامل `dashboard-preview` یا storage API · `naturalWidth > 0`

### S1 — Auth (G0)

1. `/login` — فیلد موبایل · ارسال OTP · verify
2. Redirect به `/businesses` یا dashboard

### S2 — کسب‌وکار (G0)

1. لیست کسب‌وکارها · انتخاب یکی · `/dashboard/dashboard`

### S3 — تنظیمات پروژه (G1)

1. `/dashboard/settings` · تب «پروژه‌ها»
2. ایجاد پروژه با نام `تست-موقت-{timestamp}`
3. لیست شامل `پروژه-E2E-01` (اگر seed)

### S4 — کاربران (G2)

1. تنظیمات → کاربران و دسترسی
2. لیست کاربران بدون crash · حداقل admin

### S5 — داشبورد (G3)

1. `/dashboard/dashboard` — کارت‌های آماری بدون خطای console مربوط به summary

### S6 — محصولات (G4)

1. `/dashboard/products` — لیست · وجود `مبل تست E2E` در صورت seed

### S7 — میزیتو (G5)

1. `/dashboard/tasks` یا تب‌های میزیتو — workspace بارگذاری · کارت «کار نمونه»
2. `/dashboard/chats` — thread نمایشی
3. نامه / درخواست / تقویم — لیست نمایشی بدون 404

### S8 — پیوست (G6)

1. میزیتو → نامه → پیوست فایل کوچک · بدون متن «Nextcloud»

---

## قالب گزارش Copilot (پس از هر اجرا)

```markdown
## E2E Report — {date} — {E2E_BASE_URL}

### Environment
- Gate tested: G0–G?
- Business ID: ...
- Logged in: yes/no

### API smoke
| Endpoint | Status | ok field |
|----------|--------|----------|

### UI scenarios
| ID | Pass/Fail | Notes |

### Console / Network
- 404 URLs: (list)
- JSON parse errors: (list)

### Screenshots
- (paths)

### Recommended fixes
- (file/module + priority)
```

---

## نکات OTP روی production

- ورود خودکار بدون SMS دشوار است؛ **همیشه یک بار لاگین دستی** سپس `storageState` یا cookie.
- کاربر جدید فقط اگر در DB با `mobilePhone` و `status=active` باشد ([src/lib/otp/service.ts](src/lib/otp/service.ts)).

---

## نصب Playwright (اختیاری در repo)

```bash
npm init -y @playwright/test
npx playwright install chromium
```

Spec نمونه: استفاده از `storageState: 'e2e/.auth/user.json'` و `baseURL: process.env.E2E_BASE_URL`.

Copilot می‌تواند همین playbook را به‌عنوان spec دستی اجرا کند بدون فایل spec در repo.

# Playbook Copilot — todo-v3 (Browser + curl)

**Base:** `E2E_BASE_URL=https://nexapoint.ir` · **Admin mobile:** `09126723365`  
**مرجع قبلی:** [e2e-copilot-playbook.md](../01/e2e-copilot-playbook.md) · [test01](../01/test01-retest-copilot.md) · [test02](../01/test02-access-invite-copilot.md)

پس از login: `cookie.txt` با `nexa_session=...` · `BIZ_ID` از `GET /api/businesses`

---

## قالب گزارش Copilot

```markdown
| فاز | Browser | curl | یادداشت |
|-----|---------|------|---------|
| 0 | Pass/Fail | Pass/Fail | deploy + migrate روی Runflare |
| 1 | Pass/Fail | Pass/Fail | test01 + test02 + G0–G7 |
| 2 | — | — | `npm run lint` (محلی: خطاهای legacy meizito/settings؛ build سبز) |
| 3 | Pass/Fail | — | پاکسازی کاربران تست prod |
| 4–8 | Pass/Fail | Pass/Fail | پس از deploy migration `20261019150000_v3_admin_warehouse` |
```

**تأیید dev (بدون prod):** `npm run build` موفق · migration v3 در ریپو · `prisma migrate deploy` روی prod پس از اتصال DB.

---

## Phase 0 — Gate پروداکشن

**پیش‌نیاز:** deploy + migrate

### Browser

1. `/` — تصویر لندینگ، favicon نکسا
2. `/login` — OTP با `09126723365`
3. `/businesses` — انتخاب «شرکت تست نکسا»
4. `/dashboard/dashboard` — بدون خطای JSON در UI

### curl

```bash
BASE=https://nexapoint.ir
COOKIE="nexa_session=PASTE"

curl -sS -b "$COOKIE" "$BASE/api/auth/me" | head -c 400
curl -sS -b "$COOKIE" "$BASE/api/businesses" | head -c 600
curl -sS -o /dev/null -w "%{http_code}" "$BASE/api/storage/public/images/dashboard-preview.svg"
```

**Pass:** همه 200 و `ok:true` برای APIهای احراز‌شده.

---

## Phase 1 — Copilot retest

اجرای کامل test01 + test02 + G0–G7 از playbook v1. این فاز فقط جمع‌بندی Pass/Fail در جدول بالا.

**curl اضافی v3:**

```bash
curl -sS -b "$COOKIE" "$BASE/api/admin/access-requests?status=pending"
```

---

## Phase 2 — Lint (dev)

```bash
npm run lint   # انتظار: exit 0 روی prod CI؛ فعلاً خطاهای legacy در meizito/settings
npm run build  # باید exit 0 پس از merge v3
```

**Pass:** lint و build هر دو exit 0.

---

## Phase 3 — پاکسازی legacy

### Browser

تنظیمات → سیستم → **تنظیمات** → **کاربران و دسترسی** — بدون کاربر تست با نقش «مدیر کل» ناخواسته.

**Pass:** فقط کاربران مورد انتظار فعال/pending.

---

## Phase 4 — پیوست

### Browser

1. میز کار → **نامه‌ها** (`/dashboard/tasks?tab=letters`)
2. نامه جدید → **پیوست** → فایل کوچک txt
3. ذخیره → باز کردن پیوست (تب جدید یا دانلود)

### curl

```bash
curl -sS -b "$COOKIE" -F "file=@small.txt" "$BASE/api/attachments"
# url از پاسخ → GET با cookie
curl -sS -b "$COOKIE" -o /dev/null -w "%{http_code}" "$BASE/api/attachments/YYYY-MM-DD/UUID-small.txt"
```

**Pass:** آپلود 201 · دانلود 200.

---

## Phase 5 — اشخاص

### Browser

فروش → **اشخاص** (`/dashboard/people`) · افزودن شخص با نام یکتا · F5 · همان شخص در لیست

### curl

```bash
curl -sS -b "$COOKIE" "$BASE/api/businesses/$BIZ_ID/people"
curl -sS -b "$COOKIE" -X POST "$BASE/api/businesses/$BIZ_ID/people" \
  -H "Content-Type: application/json" \
  -d '{"person":{"id":"e2e-person-1","displayName":"شخص E2E","roles":["customer"],"phones":[],"categoryIds":[],"groupMemberships":[]}}'
curl -sS -b "$COOKIE" -X PATCH "$BASE/api/businesses/$BIZ_ID/people/e2e-person-1" \
  -H "Content-Type: application/json" -d '{"person":{"displayName":"شخص E2E ویرایش"}}'
curl -sS -b "$COOKIE" -X DELETE "$BASE/api/businesses/$BIZ_ID/people/e2e-person-1"
```

**Pass:** CRUD همه `ok:true`.

---

## Phase 6 — محدودیت‌ها و بانک

### Browser

تنظیمات → کاربران → تب **محدودیت‌ها** / **دسترسی بانک** · تغییر · رفرش · مقدار بماند

### curl

```bash
USER_ID=paste
curl -sS -b "$COOKIE" "$BASE/api/admin/users/$USER_ID/restrictions"
curl -sS -b "$COOKIE" -X PATCH "$BASE/api/admin/users/$USER_ID/restrictions" \
  -H "Content-Type: application/json" -d '{"ownSalesOnly":true}'
curl -sS -b "$COOKIE" "$BASE/api/admin/users/$USER_ID/bank-access"
curl -sS -b "$COOKIE" -X PATCH "$BASE/api/admin/users/$USER_ID/bank-access" \
  -H "Content-Type: application/json" -d '{"MELLAT":false,"MELLI":true}'
```

**Pass:** PATCH بعد GET همان مقادیر.

---

## Phase 7 — Permissions

### Browser

ورود با کاربر نقش فروش (اگر وجود دارد) — تنظیمات access نباید داده حساس بدهد.

### curl

```bash
# cookie کاربر non-super-admin
curl -sS -b "$COOKIE_LOW" "$BASE/api/admin/users"
```

**Pass:** `403` و `FORBIDDEN`.

---

## Phase 8 — انبار

### Browser

تولید → **مدیریت انبار** · افزودن/ویرایش ردیف · رفرش

### curl

```bash
curl -sS -b "$COOKIE" "$BASE/api/businesses/$BIZ_ID/warehouse/items"
curl -sS -b "$COOKIE" -X POST "$BASE/api/businesses/$BIZ_ID/warehouse/items" \
  -H "Content-Type: application/json" \
  -d '{"item":{"id":"wh-e2e-1","name":"کالای تست","sku":"SKU-1","quantity":10}}'
```

**Pass:** POST 201 · GET شامل item.

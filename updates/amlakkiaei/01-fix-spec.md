# مشخصات اصلاح — بازخورد `01.txt` (املاک کیایی)

**قانون طلایی (#0):** هیچ migration یا deploy نباید دادهٔ ثبت‌شده را پاک، truncate یا overwrite کند. فقط فیلدهای nullable جدید، backfill اختیاری، و draft جدا از DB.

---

## 0. حفظ داده‌های موجود

- **مشکل:** نگرانی تیم از دست رفتن داده بعد از تغییرات.
- **راه‌حل:** migrationهای additive؛ backup قبل از deploy؛ feature flag برای فرم draft.
- **تست:** رکورد نمونه قبل/بعد deploy — همان id و همان فیلدهای قبلی.

---

## 1. ثبت شریک در «پروژه جدید» — پرش به مشتریان / اسم wrong

- **مسیر UI:** `/projects/new` → «سازندگان و شرکا» → «افزودن»
- **گزارش:** با «ثبت شرکا» از فرم خارج می‌شود و به مشتریان می‌رود؛ اسم اشتباه ثبت می‌شود.
- **فرض root cause:**
  - `<Link href="/customers">` یا دکمه header «ثبت مشتری» داخل form submit bubbling
  - autocomplete مشتری: انتخاب اشتباه label/value
- **راه‌حل:**
  - دکمه «افزودن» شریک: `type="button"`؛ جلوگیری از submit فرم پروژه
  - modal/local state برای شریک؛ navigation فقط بعد از «ذخیره پروژه»
  - autocomplete: `onSelect` با `customerId` صریح؛ debounce و UTF-8 normalize
- **جستجو در repo:** `ProjectNew`, `partners`, `co_builder`, `projects/new`
- **تست:** پروژه جدید → افزودن شریک با نام جدید → بدون leave صفحه → ذخیره → نام در لیست شرکا درست.

---

## 2. پاک شدن داده فرم بعد از خطا / خروج

- **مسیر:** همه فرم‌های بلند (`/projects/new`, `/properties/new`, modal مشتری)
- **راه‌حل:** `sessionStorage` با کلید `draft:{formId}:{userId}:{branchId}`؛ restore on mount؛ clear فقط پس از save موفق.
- **جستجو:** `useFormDraft`, `ProjectForm`, `PropertyWizard`
- **تست:** پر کردن نصف فرم → قطع شبکه → refresh → داده برگردد.

---

## 3. تاریخ — picker + تایپ دستی

- **مسیر:** تاریخ پروژه، بازدید، «تا تاریخ» مشتری
- **گزارش:** picker سخت؛ تایپ دستی لازم.
- **راه‌حل:** `HybridJalaliInput` — input text + picker؛ parse `1403/08/01`؛ پیام خطای فارسی
- **تست:** انتخاب از picker + تایپ دستی → submit → همان تاریخ در DB/API.

---

## 4. افزودن شریک به پروژه **بعد از** ثبت

- **مسیر:** `/projects/[id]` یا «ویرایش مشخصات»
- **راه‌حل:** API `POST /projects/:id/partners`؛ UI «افزودن شریک» در edit فعال
- **تست:** پروژه موجود → شریک جدید → 200 و لیست به‌روز.

---

## 5. پیشرفت پروژه ۰٪ در داشبورد/لیست — **تأیید browser**

- **مسیر:** `/projects` — کارت «میراکل» → 0٪
- **فرض:** نمایش از `progress_logs[0].percent` که 0 است؛ یا `current_progress` update نمی‌شود هنگام «افزودن به سوابق پیشرفت»
- **راه‌حل:**
  - on add progress log → update `projects.current_progress = max(logs)`
  - card/dashboard: `current_progress ?? latest_log.percent`
  - backfill یک‌بار: `UPDATE` از آخرین log (بدون delete)
- **جستجو:** `progress`, `ProjectCard`, `progress_logs`
- **تست:** ثبت ۴۵٪ → لیست و dashboard هر دو ۴۵٪.

---

## 6. موبایل تکراری + نام‌های به‌هم‌ریخته در autocomplete

- **مسیر:** `/projects/new` — شرکا
- **راه‌حل:** on 409 duplicate — clear نام پیشنهادی؛ toast فارسی؛ عدم setState نام از response خراب
- **تست:** موبایل duplicate → خطا + فیلد نام خالی/قبلی کاربر.

---

## 7. ثبت‌نشدن عمومی / خطای سرور

- **مسیر:** چند ماژول
- **راه‌حل:** لاگ server؛ نمایش `message` فارسی از API؛ Idempotency-Key برای retry
- **تست:** Network 4xx/5xx → پیام واضح؛ داده draft حفظ (#2).

---

## 8. ثبت بازدید از مشتری — فیلدهای تکراری

- **مسیر:** `/customers` → پرونده → «ثبت بازدید» (احتمالاً `/customers/[id]` یا `/appointments`)
- **گزارش:** نام/موبایل متقاضی دوباره؛ از روی مشتری باز شده.
- **راه‌حل:** `customerId` در query → prefill + readonly/hidden برای name/phone
- **جستجو:** `VisitForm`, `appointment`, `بازدید`
- **تست:** از کارت مشتری → بازدید → بدون پر مجدد نام/موبایل → save OK.

---

## 9. بازدید — انتخاب ملک / یادداشت سریع

- **راه‌حل:** فیلد «یادداشت بازدید» (required-soft) + optional multi-select property؛ کاهش requiredهای «نتیجه/علاقه» برای flow سریع
- **تست:** فقط تاریخ + «۲ ملک نشان داده شد» → save.

---

## 10–11. یکدست‌سازی عدد + محاسبه دوطرفه قیمت — **تأیید UI**

- **مسیر:** `/properties/new` مرحله ۳
- **مشاهده:** قیمت کل required؛ فی از کل محاسبه می‌شود (برعکس UX مورد انتظار)
- **راه‌حل:**
  - `normalizeDigits` (فارسی→انگلیسی) + `formatToman` نمایشی
  - `useBidirectionalPrice(area, total, perMeter, lastEditedField)`
  - on save: همیشه هر دو `total_price` و `price_per_meter` persist
- **فایل مرجع:** `updates/reference-modules/useBidirectionalPrice.ts`
- **تست:** فقط فی + متراژ → کل پر شود → save → `/properties` قیمت نمایشی ≠ «رایگان».

---

## 12. نمایش فایل برای مشتری — رایگان / master-bed wrong — **تأیید browser**

- **مسیر:** `/properties`
- **راه‌حل:** card از `display_price = total_price ?? area * price_per_meter`؛ mapping bedrooms/master از فیلدهای step 2 نه placeholder
- **جستجو:** `PropertyCard`, `formatPrice`, `master_bedroom`
- **تست:** فایل با فی ثبت‌شده → کارت و view مشتری همان مبلغ.

---

## 13. خطای سرور هنگام ذخیره (مثلاً اصلاح قیمت)

- **راه‌حل:** fix validation backend (null, bigint, decimal)؛ frontend نمایش detail
- **تست:** edit قیمت → 200؛ refresh مقدار جدید.

---

## 14. ویرایش مستاجر — تاریخ فوریت save نمی‌شود — **تست browser مشکوک**

- **مسیر:** `/customers` → ویرایش مستاجر → «تا تاریخ (اختیاری)»
- **فرض:** فیلد date فقط picker؛ PATCH بدون `urgency_deadline` / parse fail
- **راه‌حل:** همان HybridJalali (#3)؛ map به ISO در API؛ fix edit handler
- **تست:** set تاریخ → save → modal بسته → reopen → تاریخ همان.

---

## اولویت پیاده‌سازی

1. #13 (server errors) + #10–11–12 (قیمت)  
2. #1 #2 #6 (پروژه/شریک)  
3. #5 (progress)  
4. #8 #9 (بازدید)  
5. #14 #3 (تاریخ)  
6. #4  

---

## پرامپت آماده برای Cursor (ریپوی اصلی اپ)

```
@updates/01-fix-spec.md @updates/browser-qa-findings.md

طبق spec موارد 0–14 را fix کن. قانون: داده production پاک نشود.
اول #10–#13 و #5 و #14 — با reference-modules در updates/reference-modules.
بعد از هر fix تست دستی طبق بخش «تست» همان مورد.
```

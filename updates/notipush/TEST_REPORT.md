# گزارش پیاده‌سازی بک‌اند Notipush

تاریخ: 2026-10-22

## خلاصه

- Auth مبتنی بر OTP + session (JWT در کوکی httpOnly)
- ادمین seed: **09126723365** / OTP **0000** (`AUTH_DEV_OTP`)
- UI بدون `mockData` — بارگذاری از `GET /api/bootstrap`
- SMS و درگاه: stub (لاگ / تراکنش COMPLETED)

## Migration

- `20251022120000_init` — schema اصلی
- `20251022140000_auth_sessions` — `otp_challenges`, `sessions`

**لوکال:** `prisma migrate deploy` به DB remote در این محیط **ناموفق** (P1001). روی سرور deploy کن.

## API Endpoints

| Method | Path |
|--------|------|
| GET | `/api/health` |
| POST | `/api/auth/otp/request`, `/api/auth/otp/verify`, `/api/auth/logout` |
| GET | `/api/auth/session`, `/api/bootstrap`, `/api/me` |
| PATCH | `/api/me` |
| GET/POST | `/api/platforms`, `/api/platforms/[id]`, `/api/platforms/[id]/channels` |
| GET/POST | `/api/contacts`, `/api/contacts/[id]`, `/api/contacts/blocked`, `/api/contacts/blocked/[id]` |
| GET/POST | `/api/messages`, `/api/messages/test` |
| GET/POST | `/api/content-library`, `/api/tickets`, `/api/api-keys`, `/api/api-keys/[id]` |
| GET/POST | `/api/files`, `/api/wallet`, `/api/wallet/topup`, `/api/wallet/transactions` |
| GET | `/api/calls`, `/api/activity-logs`, `/api/dashboard/summary`, `/api/campaigns`, `/api/admin/seed-status` |
| POST/DELETE | `/api/test-run` (با `ENABLE_TEST_RUN` در production) |
| DELETE | `/api/campaigns/[id]`, `/api/platforms/[id]` |

## فایل‌های کلیدی

- [`middleware.ts`](middleware.ts)
- [`lib/auth/`](lib/auth/)
- [`lib/services/bootstrap.ts`](lib/services/bootstrap.ts)
- [`components/providers/NotipushProvider.tsx`](components/providers/NotipushProvider.tsx)
- [`prisma/seed.ts`](prisma/seed.ts)

## صفحات UI

`/`, `/auth`, `/dashboard`, `/platforms`, `/messages`, `/content-library`, `/contacts`, `/calls`, `/tickets`, `/wallet`, `/api-keys`, `/activity-logs`, `/files`, `/settings`, `/mobile`

## آمادگی تست / production (2026-10-22)

| مورد | وضعیت |
|------|--------|
| حذف hint ورود (09126723365 / 1234) | انجام شد |
| Bootstrap: hydrate session + `bootstrapError` | انجام شد |
| OTP bypass gated (`AUTH_ALLOW_DEV_OTP`) | انجام شد |
| `GET /api/admin/seed-status` | انجام شد |
| `POST/DELETE /api/test-run` | انجام شد |
| Empty state contacts/messages | انجام شد |

**دادهٔ «فیک»:** رکوردهای [`prisma/seed.ts`](prisma/seed.ts) در DB (پس از seed)، نه mock UI. CTR داشبورد هنوز placeholder (`—`).

**تأیید دستی production:** `/api/bootstrap`، env Runflare، migrate/seed — [`todo.md`](todo.md).

- مخزن هدف: root Next app (نه prototype `notipush30mehr-main`)
- UI بدون `data/mockData.ts`
- راهنمای Copilot: [`COPILOT_BROWSER_TEST.md`](COPILOT_BROWSER_TEST.md)

### قرارداد `/api/health`

| HTTP | Body |
|------|------|
| 200 | `{ "ok": true, "database": "connected" }` |
| 503 | `{ "ok": false, "database": "unavailable" }` |

بدون auth (public در middleware).

## تست

[`COPILOT_BROWSER_TEST.md`](COPILOT_BROWSER_TEST.md) — Pass/Fail، redaction، scope.

## وابستگی

- `jose` (JWT)

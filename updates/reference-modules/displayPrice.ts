/** قیمت نمایشی کارت فایل — رفع «رایگان» وقتی فقط فی ثبت شده (#12) */

import { formatTomanDisplay } from "./normalizeDigits";

export function displayPropertyPrice(p: {
  total_price?: number | null;
  price_per_meter?: number | null;
  area_sqm?: number | null;
}): string {
  const total =
    p.total_price ??
    (p.price_per_meter != null && p.area_sqm != null && p.area_sqm > 0
      ? Math.round(p.price_per_meter * p.area_sqm)
      : null);

  if (total == null || total <= 0) return "رایگان";
  return formatTomanDisplay(total);
}

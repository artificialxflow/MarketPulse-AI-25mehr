/** تبدیل ارقام فارسی/عربی به لاتین — برای ورودی قیمت و متراژ */

const PERSIAN = "۰۱۲۳۴۵۶۷۸۹";
const ARABIC = "٠١٢٣٤٥٦٧٨٩";

export function normalizeDigits(input: string): string {
  return input
    .split("")
    .map((ch) => {
      const pi = PERSIAN.indexOf(ch);
      if (pi >= 0) return String(pi);
      const ai = ARABIC.indexOf(ch);
      if (ai >= 0) return String(ai);
      return ch;
    })
    .join("");
}

export function parseTomanInput(raw: string): number | null {
  const n = normalizeDigits(raw).replace(/[^\d.]/g, "");
  if (!n) return null;
  const v = Number(n);
  return Number.isFinite(v) ? Math.round(v) : null;
}

export function formatTomanDisplay(value: number | null | undefined): string {
  if (value == null || value <= 0) return "—";
  return new Intl.NumberFormat("fa-IR").format(value) + " تومان";
}

/**
 * محاسبه دوطرفه قیمت کل و فی — برای مرحله «قیمت و شرایط» ثبت فایل.
 * در repo اصلی داخل React hook کپی/ادapt کنید.
 */

import { useCallback, useState } from "react";

export type PriceField = "total" | "per_meter";

export function useBidirectionalPrice(initialArea = 0) {
  const [area, setArea] = useState(initialArea);
  const [totalPrice, setTotalPrice] = useState<number | null>(null);
  const [pricePerMeter, setPricePerMeter] = useState<number | null>(null);
  const [lastEdited, setLastEdited] = useState<PriceField>("total");

  const recompute = useCallback(
    (field: PriceField, total: number | null, perMeter: number | null, sqm: number) => {
      if (sqm <= 0) return { total, perMeter };
      if (field === "per_meter" && perMeter != null) {
        return { total: Math.round(perMeter * sqm), perMeter };
      }
      if (field === "total" && total != null) {
        return { total, perMeter: Math.round(total / sqm) };
      }
      return { total, perMeter };
    },
    [],
  );

  const setTotal = (v: number | null) => {
    setLastEdited("total");
    const next = recompute("total", v, pricePerMeter, area);
    setTotalPrice(next.total);
    setPricePerMeter(next.perMeter);
  };

  const setPerMeter = (v: number | null) => {
    setLastEdited("per_meter");
    const next = recompute("per_meter", totalPrice, v, area);
    setTotalPrice(next.total);
    setPricePerMeter(next.perMeter);
  };

  const setAreaSqm = (sqm: number) => {
    setArea(sqm);
    const next = recompute(lastEdited, totalPrice, pricePerMeter, sqm);
    setTotalPrice(next.total);
    setPricePerMeter(next.perMeter);
  };

  /** برای API — هر دو مقدار را بفرستید تا لیست «رایگان» نشود */
  const toPayload = () => ({
    total_price: totalPrice,
    price_per_meter: pricePerMeter,
    area_sqm: area,
  });

  return {
    area,
    totalPrice,
    pricePerMeter,
    setTotal,
    setPerMeter,
    setAreaSqm,
    toPayload,
  };
}

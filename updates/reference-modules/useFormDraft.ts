/**
 * نگه‌داری draft فرم در sessionStorage — برای #2 در spec.
 */

import { useEffect, useRef } from "react";

export function useFormDraft<T extends object>(
  key: string,
  values: T,
  setValues: (v: T) => void,
  enabled = true,
) {
  const hydrated = useRef(false);

  useEffect(() => {
    if (!enabled || hydrated.current) return;
    try {
      const raw = sessionStorage.getItem(key);
      if (raw) setValues(JSON.parse(raw) as T);
    } catch {
      /* ignore */
    }
    hydrated.current = true;
  }, [key, enabled, setValues]);

  useEffect(() => {
    if (!enabled || !hydrated.current) return;
    try {
      sessionStorage.setItem(key, JSON.stringify(values));
    } catch {
      /* quota */
    }
  }, [key, values, enabled]);

  const clearDraft = () => {
    sessionStorage.removeItem(key);
  };

  return { clearDraft };
}

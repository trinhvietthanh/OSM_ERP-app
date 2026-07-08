"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";

import {
  DEFAULT_LOCALE,
  LOCALE_COOKIE,
  LOCALE_COOKIE_MAX_AGE,
  LOCALE_STORAGE_KEY,
  LOCALES,
  isLocale,
  setActiveLocale,
  type Locale,
} from "@/lib/i18n/config";
import {
  dictionaries,
  interpolate,
  lookup,
  type TranslationKey,
} from "@/lib/i18n/dictionaries";

type I18nContextValue = {
  locale: Locale;
  /** Switch locale; persists to localStorage + cookie and updates `<html lang>`. */
  setLocale: (locale: Locale) => void;
  /** Translate a dot-path key, filling `{placeholder}` params. */
  t: (key: TranslationKey, params?: Record<string, string | number>) => string;
};

const I18nContext = createContext<I18nContextValue | null>(null);

function persist(locale: Locale) {
  // localStorage: instant client read on next load.
  window.localStorage.setItem(LOCALE_STORAGE_KEY, locale);
  // Cookie: lets server-side `generateMetadata` localize titles.
  document.cookie = `${LOCALE_COOKIE}=${locale}; path=/; max-age=${LOCALE_COOKIE_MAX_AGE}; samesite=lax`;
  // Keep `<html lang>` and the non-React formatter singleton in sync.
  document.documentElement.lang = locale;
  setActiveLocale(locale);
}

/**
 * Provides the active locale + `t()` to the whole app.
 *
 * State initializes to `DEFAULT_LOCALE` so SSR and the first client paint match
 * (no hydration mismatch); on mount we read the stored preference and switch if
 * needed. Because every protected route is gated behind a client guard that
 * renders a loader first, the locale settles before any content paints.
 */
export function I18nProvider({ children }: { children: ReactNode }) {
  const [locale, setLocaleState] = useState<Locale>(DEFAULT_LOCALE);

  // Read the stored preference once on mount, then apply the effective locale.
  useEffect(() => {
    const stored = window.localStorage.getItem(LOCALE_STORAGE_KEY);
    const initial = isLocale(stored) ? stored : locale;
    // The stored locale is browser-only; it can only be read after mount, so
    // syncing it into state here is unavoidable (same pattern as the theme/token).
    // eslint-disable-next-line react-hooks/set-state-in-effect
    if (initial !== locale) setLocaleState(initial);
    persist(initial);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const setLocale = useCallback((next: Locale) => {
    setLocaleState(next);
    persist(next);
  }, []);

  // Keep the formatter singleton + `<html lang>` in sync with state changes.
  useEffect(() => {
    setActiveLocale(locale);
    if (typeof document !== "undefined") document.documentElement.lang = locale;
  }, [locale]);

  const t = useCallback(
    (key: TranslationKey, params?: Record<string, string | number>) =>
      interpolate(lookup(dictionaries[locale], key), params),
    [locale],
  );

  const value = useMemo<I18nContextValue>(
    () => ({ locale, setLocale, t }),
    [locale, setLocale, t],
  );

  return <I18nContext.Provider value={value}>{children}</I18nContext.Provider>;
}

/** Access the active locale, `setLocale`, and the `t()` translator. */
export function useI18n(): I18nContextValue {
  const ctx = useContext(I18nContext);
  if (!ctx) throw new Error("useI18n must be used within an I18nProvider");
  return ctx;
}

export { LOCALES };

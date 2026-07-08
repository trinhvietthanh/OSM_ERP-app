/**
 * Internationalization config.
 *
 * Vietnamese is the default; English is a user-selectable alternative. The
 * chosen locale is persisted to `localStorage` (instant client read) and to a
 * cookie (so server-side `generateMetadata` can localize document titles).
 *
 * A module-level `activeLocale` singleton lets non-React helpers
 * (`formatMoney` / `formatDate` in `lib/orders.ts`) read the current locale
 * without being turned into hooks. The provider keeps it in sync.
 */

export const LOCALES = ["vi", "en"] as const;
export type Locale = (typeof LOCALES)[number];

export const DEFAULT_LOCALE: Locale = "vi";

export const LOCALE_STORAGE_KEY = "app_erp.locale";
export const LOCALE_COOKIE = "app_erp.locale";
/** Cookie lifetime — ~1 year. */
export const LOCALE_COOKIE_MAX_AGE = 60 * 60 * 24 * 365;

/** Human-readable name for each locale, shown in the switcher. */
export const LOCALE_LABELS: Record<Locale, string> = {
  vi: "Tiếng Việt",
  en: "English",
};

/** BCP-47 tag for locale-aware formatting (dates, numbers). */
export const LOCALE_BCP47: Record<Locale, string> = {
  vi: "vi-VN",
  en: "en-US",
};

export function isLocale(value: unknown): value is Locale {
  return value === "vi" || value === "en";
}

/* --------------------------- active-locale singleton --------------------------- */

let activeLocale: Locale = DEFAULT_LOCALE;

export const getActiveLocale = (): Locale => activeLocale;

export function setActiveLocale(locale: Locale): void {
  activeLocale = locale;
}

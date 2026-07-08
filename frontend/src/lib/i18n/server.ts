/**
 * Server-only i18n helpers. Imported by Server Components / `generateMetadata`
 * to localize document metadata. Must NOT be imported from client code —
 * `next/headers` is server-only.
 */
import { cookies } from "next/headers";

import {
  DEFAULT_LOCALE,
  LOCALE_COOKIE,
  isLocale,
  type Locale,
} from "./config";
import { dictionaries, lookup, type TranslationKey } from "./dictionaries";

/** Read the locale from the cookie set by `I18nProvider`. Falls back to vi. */
export async function getLocale(): Promise<Locale> {
  const store = await cookies();
  const value = store.get(LOCALE_COOKIE)?.value;
  return isLocale(value) ? value : DEFAULT_LOCALE;
}

/** Server-side translator bound to the cookie locale. */
export async function getT() {
  const locale = await getLocale();
  return (key: TranslationKey, params?: Record<string, string | number>) => {
    const template = lookup(dictionaries[locale], key);
    if (!params) return template;
    return template.replace(/\{(\w+)\}/g, (match, name: string) =>
      name in params ? String(params[name]) : match,
    );
  };
}

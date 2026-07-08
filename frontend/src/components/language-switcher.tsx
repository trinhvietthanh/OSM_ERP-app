"use client";

import { useEffect, useRef, useState } from "react";
import { Check, ChevronDown, Globe } from "lucide-react";

import { cn } from "@/lib/utils";
import { useI18n } from "@/components/i18n-provider";
import { LOCALES, LOCALE_LABELS, type Locale } from "@/lib/i18n/config";

/**
 * Settings row that picks the UI language. Shows the current language and opens
 * a small dropdown of the available locales.
 */
export function LanguageSwitcher() {
  const { locale, setLocale, t } = useI18n();
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  // Close on outside click / Escape.
  useEffect(() => {
    if (!open) return;
    function onPointer(event: MouseEvent) {
      if (ref.current && !ref.current.contains(event.target as Node)) {
        setOpen(false);
      }
    }
    function onKey(event: KeyboardEvent) {
      if (event.key === "Escape") setOpen(false);
    }
    document.addEventListener("mousedown", onPointer);
    document.addEventListener("keydown", onKey);
    return () => {
      document.removeEventListener("mousedown", onPointer);
      document.removeEventListener("keydown", onKey);
    };
  }, [open]);

  function choose(next: Locale) {
    setLocale(next);
    setOpen(false);
  }

  return (
    <div ref={ref} className="relative">
      <button
        type="button"
        onClick={() => setOpen((value) => !value)}
        aria-haspopup="listbox"
        aria-expanded={open}
        className="flex w-full items-center gap-3 px-4 py-3 text-left transition-colors hover:bg-muted/50"
      >
        <Globe className="size-5 text-muted-foreground" aria-hidden />
        <span className="flex-1 text-sm font-medium">{t("profile.language")}</span>
        <span className="text-sm text-muted-foreground">
          {LOCALE_LABELS[locale]}
        </span>
        <ChevronDown
          className={cn(
            "size-4 text-muted-foreground transition-transform",
            open && "rotate-180",
          )}
          aria-hidden
        />
      </button>

      {open && (
        <ul
          role="listbox"
          className="absolute left-2 right-2 top-full z-10 mt-1 overflow-hidden rounded-xl border border-border bg-popover p-1 shadow-lg"
        >
          {LOCALES.map((value) => (
            <li key={value} role="option" aria-selected={value === locale}>
              <button
                type="button"
                onClick={() => choose(value)}
                className="flex w-full items-center justify-between rounded-lg px-3 py-2 text-sm transition-colors hover:bg-muted"
              >
                {LOCALE_LABELS[value]}
                {value === locale && (
                  <Check className="size-4 text-primary" aria-hidden />
                )}
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

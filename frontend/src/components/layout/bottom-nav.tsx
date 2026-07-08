"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

import { cn } from "@/lib/utils";
import { MOBILE_NAV_ITEMS, isNavActive } from "@/lib/nav";
import { useI18n } from "@/components/i18n-provider";

export function BottomNav() {
  const pathname = usePathname();
  const { t } = useI18n();

  return (
    <nav
      aria-label={t("nav.ariaPrimary")}
      className="sticky bottom-0 z-40 border-t border-border bg-background/95 pb-safe backdrop-blur supports-[backdrop-filter]:bg-background/80 lg:hidden"
    >
      <ul className="mx-auto grid max-w-md grid-cols-4">
        {MOBILE_NAV_ITEMS.map(({ href, label, icon: Icon }) => {
          const active = isNavActive(pathname, href);
          return (
            <li key={href}>
              <Link
                href={href}
                aria-current={active ? "page" : undefined}
                className={cn(
                  "flex h-16 flex-col items-center justify-center gap-1 text-xs font-medium transition-colors",
                  active
                    ? "text-primary"
                    : "text-muted-foreground hover:text-foreground",
                )}
              >
                <Icon
                  className={cn("size-5", active && "fill-primary/10")}
                  strokeWidth={active ? 2.4 : 2}
                  aria-hidden
                />
                <span>{t(label)}</span>
              </Link>
            </li>
          );
        })}
      </ul>
    </nav>
  );
}

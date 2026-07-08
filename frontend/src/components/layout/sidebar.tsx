"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { LayoutGrid, Plus } from "lucide-react";

import { cn } from "@/lib/utils";
import { NAV_ITEMS, isNavActive } from "@/lib/nav";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Button } from "@/components/ui/button";
import { useI18n } from "@/components/i18n-provider";

/** Desktop-only left navigation rail. Hidden below the `lg` breakpoint. */
export function Sidebar() {
  const pathname = usePathname();
  const { t } = useI18n();

  return (
    <aside className="sticky top-0 hidden h-dvh w-64 shrink-0 flex-col border-r border-border bg-background lg:flex">
      <div className="flex h-14 items-center gap-2.5 border-b border-border px-5">
        <span className="flex size-8 items-center justify-center rounded-lg bg-primary text-primary-foreground">
          <LayoutGrid className="size-4.5" aria-hidden />
        </span>
        <span className="text-base font-semibold tracking-tight">
          {t("nav.appName")}
        </span>
      </div>

      <nav aria-label={t("nav.ariaPrimary")} className="flex-1 space-y-1 p-3">
        <Button asChild className="mb-2 w-full gap-1.5">
          <Link href="/orders?tab=create">
            <Plus aria-hidden />
            {t("nav.newOrder")}
          </Link>
        </Button>
        {NAV_ITEMS.map(({ href, label, icon: Icon }) => {
          const active = isNavActive(pathname, href);
          return (
            <Link
              key={href}
              href={href}
              aria-current={active ? "page" : undefined}
              className={cn(
                "flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors",
                active
                  ? "bg-muted text-foreground"
                  : "text-muted-foreground hover:bg-muted/50 hover:text-foreground",
              )}
            >
              <Icon className="size-4.5" aria-hidden />
              {t(label)}
            </Link>
          );
        })}
      </nav>

      <div className="border-t border-border p-3">
        <div className="flex items-center gap-3 px-2 py-1.5">
          <Avatar className="size-9">
            <AvatarFallback className="bg-primary/10 text-sm font-semibold text-primary">
              AL
            </AvatarFallback>
          </Avatar>
          <div className="min-w-0">
            <p className="truncate text-sm font-medium">Ada Lovelace</p>
            <p className="truncate text-xs text-muted-foreground">
              ada@example.com
            </p>
          </div>
        </div>
      </div>
    </aside>
  );
}

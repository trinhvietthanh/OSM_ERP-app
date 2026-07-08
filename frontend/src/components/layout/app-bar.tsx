"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter, usePathname } from "next/navigation";
import { Bell, Plus, Search } from "lucide-react";

import { navTitleKey } from "@/lib/nav";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { useI18n } from "@/components/i18n-provider";

/**
 * Adaptive top bar.
 *
 * - Mobile (< lg): a sticky title row with the brand pill.
 * - Desktop (>= lg): the title plus a global search field (routes to the orders
 *   quick-find via `?q=`) and a quick-actions group (notifications, New, avatar).
 */
export function AppBar() {
  const pathname = usePathname();
  const router = useRouter();
  const { t } = useI18n();
  const [query, setQuery] = useState("");

  function onSubmit(event: React.SyntheticEvent) {
    event.preventDefault();
    const q = query.trim();
    router.push(q ? `/orders?q=${encodeURIComponent(q)}` : "/orders");
  }

  return (
    <header className="sticky top-0 z-40 border-b border-border bg-background/95 pt-safe backdrop-blur supports-[backdrop-filter]:bg-background/80">
      <div className="flex h-14 items-center gap-3 px-4 lg:gap-6 lg:px-8">
        <h1 className="text-lg font-semibold tracking-tight lg:shrink-0">
          {t(navTitleKey(pathname))}
        </h1>

        {/* Mobile brand pill */}
        <span className="ml-auto rounded-full bg-primary/10 px-2.5 py-1 text-xs font-medium text-primary lg:hidden">
          {t("nav.brandPill")}
        </span>

        {/* Desktop global search */}
        <form
          onSubmit={onSubmit}
          role="search"
          className="relative hidden flex-1 lg:flex"
        >
          <Search
            className="pointer-events-none absolute top-1/2 left-3 size-4 -translate-y-1/2 text-muted-foreground"
            aria-hidden
          />
          <Input
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder={t("nav.searchPlaceholder")}
            className="pl-9"
            inputMode="search"
            aria-label={t("nav.searchAria")}
          />
        </form>

        {/* Desktop quick actions */}
        <div className="hidden items-center gap-1.5 lg:flex">
          <Button size="icon-sm" variant="ghost" aria-label={t("nav.notifications")}>
            <Bell aria-hidden />
          </Button>
          <Button asChild size="sm" className="gap-1.5">
            <Link href="/orders?tab=create">
              <Plus aria-hidden />
              {t("nav.new")}
            </Link>
          </Button>
          <Avatar className="size-8">
            <AvatarFallback className="bg-primary/10 text-xs font-semibold text-primary">
              AL
            </AvatarFallback>
          </Avatar>
        </div>
      </div>
    </header>
  );
}

"use client";

import { useMemo } from "react";
import { useQuery } from "@tanstack/react-query";
import {
  Bell,
  ChevronRight,
  CreditCard,
  LogOut,
  Settings,
  ShieldCheck,
} from "lucide-react";

import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Card, CardContent } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import InstallPrompt from "@/components/InstallPrompt";
import { LanguageSwitcher } from "@/components/language-switcher";
import { useI18n } from "@/components/i18n-provider";
import type { TranslationKey } from "@/lib/i18n/dictionaries";
import { fetchCurrentUser } from "@/lib/api";

type Setting = { labelKey: TranslationKey; icon: typeof Settings };

/** Up to two uppercase initials from a username (e.g. "ada_lovelace" → "AL"). */
function initialsFrom(username: string): string {
  const parts = username.split(/[^a-zA-Z0-9]+/).filter(Boolean);
  const letters = parts.slice(0, 2).map((p) => p[0]?.toUpperCase() ?? "");
  return letters.join("") || username.slice(0, 2).toUpperCase() || "—";
}

export default function ProfilePage() {
  const { t } = useI18n();
  const { data: user, isLoading } = useQuery({
    queryKey: ["me"],
    queryFn: fetchCurrentUser,
  });

  const initials = useMemo(
    () => initialsFrom(user?.username ?? ""),
    [user?.username],
  );

  const SETTINGS: Setting[] = [
    { labelKey: "profile.settings.account", icon: Settings },
    { labelKey: "profile.settings.notifications", icon: Bell },
    { labelKey: "profile.settings.billing", icon: CreditCard },
    { labelKey: "profile.settings.security", icon: ShieldCheck },
  ];

  return (
    <div className="space-y-6 lg:grid lg:grid-cols-[280px_minmax(0,1fr)] lg:items-start lg:gap-6 lg:space-y-0">
      {/* Left rail: identity + sign out */}
      <div className="space-y-6">
        <Card>
          <CardContent className="flex items-center gap-4 px-4">
            <Avatar className="size-14">
              <AvatarFallback className="bg-primary/10 text-lg font-semibold text-primary">
                {isLoading ? <Skeleton className="size-7 rounded-full" /> : initials}
              </AvatarFallback>
            </Avatar>
            <div className="min-w-0">
              {isLoading ? (
                <div className="space-y-2">
                  <Skeleton className="h-5 w-32" />
                  <Skeleton className="h-4 w-44" />
                </div>
              ) : (
                <>
                  <p className="truncate text-lg font-semibold">
                    {user?.username ?? "—"}
                  </p>
                  <p className="truncate text-sm text-muted-foreground">
                    {user?.email ?? ""}
                  </p>
                </>
              )}
            </div>
          </CardContent>
        </Card>

        <button className="flex w-full items-center justify-center gap-2 rounded-xl border border-border py-3 text-sm font-medium text-destructive transition-colors hover:bg-destructive/5">
          <LogOut className="size-4" aria-hidden />
          {t("profile.signOut")}
        </button>
      </div>

      {/* Right column: settings + install */}
      <div className="space-y-6">
        <Card className="py-2">
          <CardContent className="divide-y divide-border px-0">
            <LanguageSwitcher />
            {SETTINGS.map(({ labelKey, icon: Icon }) => (
              <button
                key={labelKey}
                className="flex w-full items-center gap-3 px-4 py-3 text-left transition-colors hover:bg-muted/50"
              >
                <Icon className="size-5 text-muted-foreground" aria-hidden />
                <span className="flex-1 text-sm font-medium">{t(labelKey)}</span>
                <ChevronRight
                  className="size-4 text-muted-foreground"
                  aria-hidden
                />
              </button>
            ))}
          </CardContent>
        </Card>

        <InstallPrompt />
      </div>
    </div>
  );
}

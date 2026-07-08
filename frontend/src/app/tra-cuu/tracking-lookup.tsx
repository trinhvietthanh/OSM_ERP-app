"use client";

import { useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { Check, PackageSearch, Search } from "lucide-react";

import { cn } from "@/lib/utils";
import { ApiError } from "@/lib/api";
import {
  formatDate,
  formatMoney,
  orderStatusLabel,
  toNumber,
  trackOrder,
  type OrderStatus,
} from "@/lib/orders";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Separator } from "@/components/ui/separator";
import { Card, CardContent } from "@/components/ui/card";
import { useI18n } from "@/components/i18n-provider";

/** Milestones shown on the public timeline (cancelled handled separately). */
const TIMELINE: OrderStatus[] = [
  "pending",
  "confirmed",
  "purchasing",
  "purchased",
  "arrived",
  "delivered",
];

/**
 * Public order lookup (customers, no account needed). The code can be passed as
 * `?code=` so the shop can send a direct link.
 */
export function TrackingLookup() {
  const { t } = useI18n();
  const router = useRouter();
  const searchParams = useSearchParams();
  const urlCode = (searchParams.get("code") ?? "").trim().toUpperCase();

  const [input, setInput] = useState(urlCode);

  const { data, isFetching, isError, error } = useQuery({
    queryKey: ["tracking", urlCode],
    queryFn: () => trackOrder(urlCode),
    enabled: urlCode.length > 0,
    retry: false,
    staleTime: 30_000,
  });

  function submit(event: React.FormEvent) {
    event.preventDefault();
    const code = input.trim().toUpperCase();
    if (code) router.push(`/tra-cuu?code=${encodeURIComponent(code)}`);
  }

  const notFound =
    isError && error instanceof ApiError && error.status === 404;

  return (
    <main className="mx-auto flex min-h-dvh w-full max-w-md flex-col gap-6 px-4 py-10">
      <div className="text-center">
        <p className="text-sm font-semibold tracking-wide text-muted-foreground">
          {t("nav.appName")}
        </p>
        <h1 className="mt-1 text-2xl font-semibold">{t("tracking.title")}</h1>
        <p className="mt-1 text-sm text-muted-foreground">
          {t("tracking.subtitle")}
        </p>
      </div>

      <form onSubmit={submit} className="flex gap-2">
        <div className="relative flex-1">
          <Search
            className="pointer-events-none absolute top-1/2 left-3 size-4 -translate-y-1/2 text-muted-foreground"
            aria-hidden
          />
          <Input
            value={input}
            onChange={(event) => setInput(event.target.value.toUpperCase())}
            placeholder={t("tracking.placeholder")}
            aria-label={t("tracking.codeAria")}
            className="pl-9 font-mono uppercase tracking-widest"
            maxLength={8}
            autoFocus
          />
        </div>
        <Button type="submit" disabled={!input.trim() || isFetching}>
          {isFetching ? t("tracking.searching") : t("tracking.search")}
        </Button>
      </form>

      {notFound && (
        <Card>
          <CardContent className="flex flex-col items-center gap-2 py-8 text-center">
            <PackageSearch className="size-8 text-muted-foreground" aria-hidden />
            <p className="font-medium">{t("tracking.notFound", { code: urlCode })}</p>
            <p className="text-sm text-muted-foreground">
              {t("tracking.notFoundHint")}
            </p>
          </CardContent>
        </Card>
      )}
      {isError && !notFound && (
        <p className="text-center text-sm text-destructive">{t("tracking.error")}</p>
      )}

      {data && (
        <Card>
          <CardContent className="space-y-4 py-5">
            <div className="flex items-center justify-between">
              <div>
                <p className="font-mono text-lg font-semibold tracking-widest">
                  {data.tracking_code}
                </p>
                <p className="text-xs text-muted-foreground">
                  {t("tracking.createdOn", { date: formatDate(data.created_at) })}{" "}
                  · {t("tracking.updated", { date: formatDate(data.updated_at) })}
                </p>
              </div>
            </div>

            {/* Status timeline */}
            {data.status === "cancelled" ? (
              <p className="rounded-lg bg-destructive/10 px-3 py-2 text-sm font-medium text-destructive">
                {t("tracking.cancelledNotice")}
              </p>
            ) : (
              <ol className="space-y-0">
                {TIMELINE.map((step, index) => {
                  const currentIndex = TIMELINE.indexOf(data.status);
                  const done = index < currentIndex;
                  const current = index === currentIndex;
                  return (
                    <li key={step} className="flex gap-3">
                      <div className="flex flex-col items-center">
                        <span
                          className={cn(
                            "flex size-5 items-center justify-center rounded-full border text-[10px]",
                            done || current
                              ? "border-primary bg-primary text-primary-foreground"
                              : "border-border bg-background text-muted-foreground",
                          )}
                        >
                          {done ? <Check className="size-3" aria-hidden /> : index + 1}
                        </span>
                        {index < TIMELINE.length - 1 && (
                          <span
                            className={cn(
                              "w-px flex-1 min-h-4",
                              done ? "bg-primary" : "bg-border",
                            )}
                            aria-hidden
                          />
                        )}
                      </div>
                      <p
                        className={cn(
                          "pb-3 text-sm",
                          current
                            ? "font-semibold"
                            : done
                              ? "text-foreground"
                              : "text-muted-foreground",
                        )}
                      >
                        {orderStatusLabel(step)}
                        {current && (
                          <span className="ml-2 rounded-full bg-primary/10 px-2 py-0.5 text-xs font-medium text-primary">
                            {t("tracking.current")}
                          </span>
                        )}
                      </p>
                    </li>
                  );
                })}
              </ol>
            )}

            <Separator />

            {/* Items */}
            <ul className="space-y-1.5 text-sm">
              {data.lines.map((line, index) => (
                <li key={index} className="flex items-center justify-between gap-2">
                  <span className="truncate">{line.product_name}</span>
                  <span className="shrink-0 tabular-nums text-muted-foreground">
                    × {line.quantity}
                  </span>
                </li>
              ))}
            </ul>

            <Separator />

            {/* Money */}
            <div className="space-y-1 text-sm">
              <div className="flex justify-between">
                <span className="text-muted-foreground">{t("tracking.total")}</span>
                <span className="font-semibold tabular-nums">
                  {formatMoney(data.total_amount)}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">{t("tracking.paid")}</span>
                <span className="tabular-nums">
                  {formatMoney(data.total_collected)}
                </span>
              </div>
              <div className="flex justify-between font-medium">
                <span>{t("tracking.dueOnDelivery")}</span>
                <span
                  className={cn(
                    "tabular-nums",
                    toNumber(data.remaining) > 0 && "text-destructive",
                  )}
                >
                  {formatMoney(data.remaining)}
                </span>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </main>
  );
}

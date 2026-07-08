"use client";

import { useMemo } from "react";
import { useQuery } from "@tanstack/react-query";
import {
  AlertTriangle,
  DollarSign,
  HandCoins,
  Receipt,
  ShoppingCart,
  TrendingDown,
  TrendingUp,
} from "lucide-react";

import { cn } from "@/lib/utils";
import { Card, CardContent } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { StatusBadge } from "@/components/ui/status-badge";
import { useI18n } from "@/components/i18n-provider";
import {
  getDailySummaryReport,
  getOverviewReport,
  getPeriodComparison,
} from "@/lib/reports";
import { STATUS_STYLE, formatMoney, toNumber } from "@/lib/orders";
import { LOCALE_BCP47, getActiveLocale } from "@/lib/i18n/config";

type Icon = typeof DollarSign;

/** % change current vs previous; null when the previous period is empty. */
function pctDelta(current: number, previous: number): number | null {
  if (previous === 0) return null;
  return ((current - previous) / previous) * 100;
}

/** `YYYY-MM-DD` for a Date (local time, for the daily-summary date params). */
function isoDate(d: Date) {
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(
    d.getDate(),
  ).padStart(2, "0")}`;
}

export default function DashboardPage() {
  const { t } = useI18n();

  // Last 7 days (including today) for the revenue chart.
  const range = useMemo(() => {
    const today = new Date();
    const start = new Date(today);
    start.setDate(today.getDate() - 6);
    return { date_from: isoDate(start), date_to: isoDate(today) };
  }, []);

  const overview = useQuery({
    queryKey: ["reports", "overview"],
    queryFn: getOverviewReport,
  });
  const daily = useQuery({
    queryKey: ["reports", "daily-summary", range],
    queryFn: () => getDailySummaryReport(range),
  });
  const comparison = useQuery({
    queryKey: ["reports", "period-comparison"],
    queryFn: () => getPeriodComparison(),
  });

  const deltas = comparison.data
    ? {
        revenue: pctDelta(
          toNumber(comparison.data.current.revenue),
          toNumber(comparison.data.previous.revenue),
        ),
        orders: pctDelta(
          comparison.data.current.orders_count,
          comparison.data.previous.orders_count,
        ),
        collected: pctDelta(
          toNumber(comparison.data.current.collected),
          toNumber(comparison.data.previous.collected),
        ),
      }
    : { revenue: null, orders: null, collected: null };

  const shortDate = (iso: string) =>
    new Date(iso).toLocaleDateString(LOCALE_BCP47[getActiveLocale()], {
      day: "2-digit",
      month: "2-digit",
    });

  const kpis: {
    label: string;
    value: string;
    icon: Icon;
    delta?: number | null;
  }[] = overview.data
    ? [
        {
          label: t("dashboard.kpiRevenue"),
          value: formatMoney(overview.data.total_revenue),
          icon: DollarSign,
          delta: deltas.revenue,
        },
        {
          label: t("dashboard.kpiOrders"),
          value: String(overview.data.orders_count),
          icon: ShoppingCart,
          delta: deltas.orders,
        },
        {
          label: t("dashboard.kpiCollected"),
          value: formatMoney(overview.data.total_collected),
          icon: HandCoins,
          delta: deltas.collected,
        },
        {
          label: t("dashboard.kpiOutstanding"),
          value: formatMoney(overview.data.total_outstanding),
          icon: Receipt,
        },
      ]
    : [];

  const days = daily.data?.days ?? [];
  const maxRevenue = Math.max(1, ...days.map((d) => toNumber(d.revenue)));
  const statusBreakdown = overview.data?.status_breakdown ?? [];
  const maxStatus = Math.max(1, ...statusBreakdown.map((s) => s.count));

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold tracking-tight">{t("dashboard.title")}</h2>

      {/* KPI cards */}
      <section className="grid grid-cols-2 gap-3 lg:grid-cols-4">
        {overview.isLoading
          ? Array.from({ length: 4 }).map((_, i) => (
              <Card key={i} className="py-4">
                <CardContent className="px-4">
                  <Skeleton className="size-9 rounded-lg" />
                  <Skeleton className="mt-3 h-7 w-24" />
                  <Skeleton className="mt-2 h-4 w-16" />
                </CardContent>
              </Card>
            ))
          : kpis.map(({ label, value, icon: Icon, delta }) => (
              <Card key={label} className="gap-0 py-4">
                <CardContent className="px-4">
                  <span className="flex size-9 items-center justify-center rounded-lg bg-primary/10 text-primary">
                    <Icon className="size-4.5" aria-hidden />
                  </span>
                  <p className="mt-3 text-2xl font-semibold tabular-nums">{value}</p>
                  <p className="text-sm text-muted-foreground">{label}</p>
                  {delta != null && (
                    <p
                      className={cn(
                        "mt-1 flex items-center gap-1 text-xs tabular-nums",
                        delta >= 0 ? "text-green-600" : "text-destructive",
                      )}
                      title={t("dashboard.vsLastMonth")}
                    >
                      {delta >= 0 ? (
                        <TrendingUp className="size-3.5" aria-hidden />
                      ) : (
                        <TrendingDown className="size-3.5" aria-hidden />
                      )}
                      {`${delta >= 0 ? "+" : ""}${delta.toFixed(0)}% `}
                      <span className="text-muted-foreground">
                        {t("dashboard.vsLastMonth")}
                      </span>
                    </p>
                  )}
                </CardContent>
              </Card>
            ))}
      </section>

      {/* Orders waiting to be consolidated */}
      {overview.data && overview.data.unassigned_count > 0 && (
        <p className="flex items-center gap-2 rounded-lg bg-amber-500/10 px-3 py-2 text-sm text-amber-700">
          <AlertTriangle className="size-4 shrink-0" aria-hidden />
          {t("reports.overview.unassignedWarn", {
            count: overview.data.unassigned_count,
          })}
        </p>
      )}

      <div className="lg:grid lg:grid-cols-[minmax(0,1fr)_320px] lg:items-start lg:gap-6">
        {/* Revenue (last 7 days) */}
        <section className="space-y-3">
          <div className="flex items-center justify-between">
            <h3 className="font-semibold">{t("dashboard.revenueTitle")}</h3>
            <span className="text-sm text-muted-foreground">
              {t("dashboard.last7days")}
            </span>
          </div>
          <Card>
            <CardContent className="px-4 py-4">
              {daily.isLoading ? (
                <Skeleton className="h-32 w-full" />
              ) : days.length === 0 ? (
                <p className="py-10 text-center text-sm text-muted-foreground">
                  {t("dashboard.noData")}
                </p>
              ) : (
                <div className="flex items-end gap-2">
                  {days.map((d) => {
                    const pct = Math.round((toNumber(d.revenue) / maxRevenue) * 100);
                    return (
                      <div
                        key={d.date}
                        className="flex flex-1 flex-col items-center gap-2"
                      >
                        <div className="flex h-32 w-full items-end">
                          <div
                            className="w-full rounded-md bg-primary/80 transition-colors hover:bg-primary"
                            style={{ height: `${Math.max(4, pct)}%` }}
                            title={formatMoney(d.revenue)}
                          />
                        </div>
                        <span className="text-xs text-muted-foreground">
                          {shortDate(d.date)}
                        </span>
                      </div>
                    );
                  })}
                </div>
              )}
            </CardContent>
          </Card>
        </section>

        {/* Orders by status */}
        <aside className="mt-6 space-y-3 lg:mt-0">
          <Card>
            <CardContent className="space-y-3 px-4 py-4">
              <h3 className="font-semibold">{t("dashboard.ordersByStatus")}</h3>
              {overview.isLoading ? (
                <div className="space-y-3">
                  {Array.from({ length: 4 }).map((_, i) => (
                    <Skeleton key={i} className="h-6 w-full" />
                  ))}
                </div>
              ) : statusBreakdown.length > 0 ? (
                <ul className="space-y-2.5">
                  {statusBreakdown.map((s) => (
                    <li key={s.status}>
                      <div className="flex items-center justify-between gap-2 text-sm">
                        <StatusBadge status={s.status} size="sm" />
                        <span className="text-xs text-muted-foreground tabular-nums">
                          {s.count} · {formatMoney(s.total_amount)}
                        </span>
                      </div>
                      <div className="mt-1.5 h-1.5 w-full overflow-hidden rounded-full bg-muted">
                        <div
                          className={cn(
                            "h-full rounded-full",
                            STATUS_STYLE[s.status].dot,
                          )}
                          style={{
                            width: `${Math.round((s.count / maxStatus) * 100)}%`,
                          }}
                        />
                      </div>
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="text-sm text-muted-foreground">{t("dashboard.noData")}</p>
              )}
            </CardContent>
          </Card>
        </aside>
      </div>
    </div>
  );
}

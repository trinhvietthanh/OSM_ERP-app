"use client";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { AlertTriangle } from "lucide-react";

import Link from "next/link";

import { cn } from "@/lib/utils";
import {
  orderStatusLabel,
  STATUS_STYLE,
  STATUS_VARIANT,
  formatDate,
  formatMoney,
  toNumber,
} from "@/lib/orders";
import { TRIP_STATUS_VARIANT, tripStatusLabel } from "@/lib/trips";
import { LOCALE_BCP47, getActiveLocale } from "@/lib/i18n/config";
import {
  getCashFlowReport,
  getCustomerReport,
  getDailySummaryReport,
  getOperationsReport,
  getOverviewReport,
  getProductReport,
  getProfitReport,
  getReceivablesReport,
  getTripReport,
  type AgingBucketId,
} from "@/lib/reports";
import { useI18n } from "@/components/i18n-provider";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Skeleton } from "@/components/ui/skeleton";
import { Card, CardContent } from "@/components/ui/card";
import { StatusBadge } from "@/components/ui/status-badge";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

const TABS = [
  { id: "overview", labelKey: "reports.tabs.overview" as const },
  { id: "daily", labelKey: "reports.tabs.daily" as const },
  { id: "cashflow", labelKey: "reports.tabs.cashflow" as const },
  { id: "profit", labelKey: "reports.tabs.profit" as const },
  { id: "receivables", labelKey: "reports.tabs.receivables" as const },
  { id: "trips", labelKey: "reports.tabs.trips" as const },
  { id: "products", labelKey: "reports.tabs.products" as const },
  { id: "customers", labelKey: "reports.tabs.customers" as const },
  { id: "operations", labelKey: "reports.tabs.operations" as const },
];

type TabId = (typeof TABS)[number]["id"];

/** Reports screen: overview dashboard, daily pulse, cash flow, profit, debt. */
export function ReportsView() {
  const { t } = useI18n();
  const [tab, setTab] = useState<TabId>("overview");

  return (
    <div className="space-y-4">
      <div className="-mx-4 flex gap-1.5 overflow-x-auto px-4 pb-1 [scrollbar-width:none] [&::-webkit-scrollbar]:hidden">
        {TABS.map((tabItem) => {
          const active = tab === tabItem.id;
          return (
            <Button
              key={tabItem.id}
              size="sm"
              variant={active ? "default" : "secondary"}
              aria-pressed={active}
              onClick={() => setTab(tabItem.id)}
              className="shrink-0"
            >
              {t(tabItem.labelKey)}
            </Button>
          );
        })}
      </div>

      {tab === "overview" && <OverviewPanel />}
      {tab === "daily" && <DailyPanel />}
      {tab === "cashflow" && <CashFlowPanel />}
      {tab === "profit" && <ProfitPanel />}
      {tab === "receivables" && <ReceivablesPanel />}
      {tab === "trips" && <TripsPanel />}
      {tab === "products" && <ProductsPanel />}
      {tab === "customers" && <CustomersPanel />}
      {tab === "operations" && <OperationsPanel />}
    </div>
  );
}

/** Reusable [from / to] date filter for the date-scoped panels. */
function DateRangeFilter({
  dateFrom,
  dateTo,
  setDateFrom,
  setDateTo,
}: {
  dateFrom: string;
  dateTo: string;
  setDateFrom: (v: string) => void;
  setDateTo: (v: string) => void;
}) {
  const { t } = useI18n();
  return (
    <div className="flex flex-wrap items-end gap-2">
      <div className="space-y-1">
        <Label htmlFor="date-from" className="text-xs">
          {t("common.dateFrom")}
        </Label>
        <Input
          id="date-from"
          type="date"
          value={dateFrom}
          onChange={(event) => setDateFrom(event.target.value)}
          className="h-9 w-40"
        />
      </div>
      <div className="space-y-1">
        <Label htmlFor="date-to" className="text-xs">
          {t("common.dateTo")}
        </Label>
        <Input
          id="date-to"
          type="date"
          value={dateTo}
          onChange={(event) => setDateTo(event.target.value)}
          className="h-9 w-40"
        />
      </div>
      {(dateFrom || dateTo) && (
        <Button
          size="sm"
          variant="ghost"
          onClick={() => {
            setDateFrom("");
            setDateTo("");
          }}
        >
          {t("common.clearFilter")}
        </Button>
      )}
    </div>
  );
}

function SummaryCard({
  label,
  value,
  tone,
}: {
  label: string;
  value: string;
  tone?: "positive" | "negative";
}) {
  return (
    <Card className="py-0">
      <CardContent className="px-4 py-3">
        <p className="text-xs text-muted-foreground">{label}</p>
        <p
          className={cn(
            "mt-0.5 text-lg font-semibold tabular-nums",
            tone === "positive" && "text-green-600",
            tone === "negative" && "text-destructive",
          )}
        >
          {value}
        </p>
      </CardContent>
    </Card>
  );
}

const shortDate = (iso: string) =>
  new Date(iso).toLocaleDateString(LOCALE_BCP47[getActiveLocale()], {
    day: "2-digit",
    month: "2-digit",
  });

function OverviewPanel() {
  const { t } = useI18n();
  const { data, isLoading } = useQuery({
    queryKey: ["reports", "overview"],
    queryFn: getOverviewReport,
  });

  if (isLoading || !data) return <Skeleton className="h-60 w-full" />;

  const profit = toNumber(data.total_profit);
  const maxCount = Math.max(1, ...data.status_breakdown.map((s) => s.count));

  return (
    <div className="space-y-4">
      <div className="grid grid-cols-2 gap-3 lg:grid-cols-3">
        <SummaryCard
          label={t("reports.overview.revenue")}
          value={formatMoney(data.total_revenue)}
        />
        <SummaryCard
          label={t("reports.overview.collected")}
          value={formatMoney(data.total_collected)}
          tone="positive"
        />
        <SummaryCard
          label={t("reports.overview.outstanding")}
          value={formatMoney(data.total_outstanding)}
          tone="negative"
        />
        <SummaryCard
          label={t("reports.overview.depositDue")}
          value={formatMoney(data.total_deposit_due)}
        />
        <SummaryCard
          label={t("reports.overview.cost")}
          value={formatMoney(data.total_cost)}
        />
        <SummaryCard
          label={t("reports.overview.profit")}
          value={formatMoney(data.total_profit)}
          tone={profit >= 0 ? "positive" : "negative"}
        />
      </div>

      {data.unassigned_count > 0 && (
        <p className="flex items-center gap-2 rounded-lg bg-amber-500/10 px-3 py-2 text-sm text-amber-700">
          <AlertTriangle className="size-4 shrink-0" aria-hidden />
          {t("reports.overview.unassignedWarn", { count: data.unassigned_count })}
        </p>
      )}

      <Card className="py-0">
        <CardContent className="space-y-3 px-4 py-4">
          <div className="flex items-center justify-between">
            <p className="text-sm font-medium">{t("reports.overview.pipeline")}</p>
            <span className="text-xs text-muted-foreground">
              {t("reports.overview.ordersCount", { count: data.orders_count })}
            </span>
          </div>
          {data.status_breakdown.map((s) => {
            const pct = (s.count / maxCount) * 100;
            return (
              <div key={s.status} className="space-y-1.5">
                <div className="flex items-center justify-between gap-2">
                  <StatusBadge status={s.status} size="sm" />
                  <span className="text-xs tabular-nums text-muted-foreground">
                    {t("reports.overview.barCaption", {
                      count: s.count,
                      money: formatMoney(s.total_amount),
                    })}
                  </span>
                </div>
                <div className="h-2 w-full overflow-hidden rounded-full bg-muted">
                  <div
                    className={cn(
                      "h-full rounded-full",
                      STATUS_STYLE[s.status].dot,
                    )}
                    style={{ width: `${pct}%` }}
                  />
                </div>
              </div>
            );
          })}
        </CardContent>
      </Card>
    </div>
  );
}

function DailyPanel() {
  const { t } = useI18n();
  const [dateFrom, setDateFrom] = useState("");
  const [dateTo, setDateTo] = useState("");

  const { data, isLoading } = useQuery({
    queryKey: ["reports", "daily", { dateFrom, dateTo }],
    queryFn: () =>
      getDailySummaryReport({
        date_from: dateFrom || undefined,
        date_to: dateTo || undefined,
      }),
  });

  if (isLoading || !data) return <Skeleton className="h-60 w-full" />;

  const max = Math.max(1, ...data.days.map((d) => d.orders_count));

  return (
    <div className="space-y-4">
      <DateRangeFilter
        dateFrom={dateFrom}
        dateTo={dateTo}
        setDateFrom={setDateFrom}
        setDateTo={setDateTo}
      />

      <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
        <SummaryCard label={t("reports.daily.orders")} value={String(data.orders_count)} />
        <SummaryCard label={t("reports.daily.confirmed")} value={String(data.confirmed_count)} />
        <SummaryCard label={t("reports.daily.revenue")} value={formatMoney(data.revenue)} />
        <SummaryCard
          label={t("reports.daily.collected")}
          value={formatMoney(data.collected)}
          tone="positive"
        />
      </div>

      {data.days.length === 0 ? (
        <p className="py-10 text-center text-sm text-muted-foreground">
          {t("reports.daily.empty")}
        </p>
      ) : (
        <Card className="py-0">
          <CardContent className="space-y-3 px-4 py-4">
            <div className="flex items-center justify-between">
              <p className="text-sm font-medium">{t("reports.daily.chartTitle")}</p>
              <div className="flex items-center gap-3 text-xs text-muted-foreground">
                <span className="flex items-center gap-1">
                  <span className="size-2 rounded-full bg-primary" />{" "}
                  {t("reports.daily.legendConfirmed")}
                </span>
                <span className="flex items-center gap-1">
                  <span className="size-2 rounded-full bg-primary/25" />{" "}
                  {t("reports.daily.legendPending")}
                </span>
              </div>
            </div>
            <div className="overflow-x-auto pb-1 [scrollbar-width:none] [&::-webkit-scrollbar]:hidden">
              <div className="flex h-40 items-end gap-1.5">
                {data.days.map((d) => {
                  const total = (d.orders_count / max) * 100;
                  const conf = d.orders_count
                    ? (d.confirmed_count / d.orders_count) * total
                    : 0;
                  const rest = total - conf;
                  return (
                    <div
                      key={d.date}
                      className="flex w-6 shrink-0 flex-col items-center gap-1"
                      title={t("reports.daily.tooltip", {
                        date: formatDate(d.date),
                        count: d.orders_count,
                        confirmed: d.confirmed_count,
                        money: formatMoney(d.revenue),
                      })}
                    >
                      <div className="flex h-32 w-full flex-col justify-end">
                        <div
                          className="w-full bg-primary/25"
                          style={{ height: `${rest}%` }}
                        />
                        <div
                          className="w-full rounded-b-sm bg-primary"
                          style={{ height: `${conf}%` }}
                        />
                      </div>
                      <span className="text-[0.6rem] tabular-nums text-muted-foreground">
                        {shortDate(d.date)}
                      </span>
                    </div>
                  );
                })}
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}

function CashFlowPanel() {
  const { t } = useI18n();
  const [dateFrom, setDateFrom] = useState("");
  const [dateTo, setDateTo] = useState("");

  const { data, isLoading } = useQuery({
    queryKey: ["reports", "cashflow", { dateFrom, dateTo }],
    queryFn: () =>
      getCashFlowReport({
        date_from: dateFrom || undefined,
        date_to: dateTo || undefined,
      }),
  });

  if (isLoading || !data) return <Skeleton className="h-60 w-full" />;

  const net = toNumber(data.net);

  return (
    <div className="space-y-4">
      <DateRangeFilter
        dateFrom={dateFrom}
        dateTo={dateTo}
        setDateFrom={setDateFrom}
        setDateTo={setDateTo}
      />

      <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
        <SummaryCard
          label={t("reports.cashflow.in")}
          value={formatMoney(data.cash_in)}
          tone="positive"
        />
        <SummaryCard
          label={t("reports.cashflow.out")}
          value={formatMoney(data.cash_out)}
          tone="negative"
        />
        <SummaryCard
          label={t("reports.cashflow.refunded")}
          value={formatMoney(data.refunded)}
          tone="negative"
        />
        <SummaryCard
          label={t("reports.cashflow.net")}
          value={formatMoney(data.net)}
          tone={net >= 0 ? "positive" : "negative"}
        />
      </div>

      <Card className="py-0">
        <CardContent className="space-y-1 px-4 py-4">
          <p className="text-sm font-medium">{t("reports.cashflow.pendingTitle")}</p>
          <p className="text-2xl font-bold tabular-nums text-amber-600">
            {formatMoney(data.pending_purchase_cost)}
          </p>
          <p className="text-xs text-muted-foreground">
            {t("reports.cashflow.pendingDesc")}
          </p>
        </CardContent>
      </Card>
    </div>
  );
}

function ProfitPanel() {
  const { t } = useI18n();
  const [dateFrom, setDateFrom] = useState("");
  const [dateTo, setDateTo] = useState("");

  const { data, isLoading } = useQuery({
    queryKey: ["reports", "profit", { dateFrom, dateTo }],
    queryFn: () =>
      getProfitReport({
        date_from: dateFrom || undefined,
        date_to: dateTo || undefined,
      }),
  });

  if (isLoading || !data) return <Skeleton className="h-60 w-full" />;

  const profit = toNumber(data.total_profit);

  return (
    <div className="space-y-4">
      <DateRangeFilter
        dateFrom={dateFrom}
        dateTo={dateTo}
        setDateFrom={setDateFrom}
        setDateTo={setDateTo}
      />

      {/* Summary */}
      <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
        <SummaryCard label={t("reports.profit.revenue")} value={formatMoney(data.total_revenue)} />
        <SummaryCard label={t("reports.profit.cost")} value={formatMoney(data.total_cost)} />
        <SummaryCard
          label={t("reports.profit.profit")}
          value={formatMoney(data.total_profit)}
          tone={profit >= 0 ? "positive" : "negative"}
        />
        <SummaryCard label={t("reports.profit.orders")} value={String(data.orders_count)} />
      </div>

      {data.orders_with_incomplete_cost > 0 && (
        <p className="flex items-center gap-2 rounded-lg bg-amber-500/10 px-3 py-2 text-sm text-amber-700">
          <AlertTriangle className="size-4 shrink-0" aria-hidden />
          {t("reports.profit.incompleteWarn", {
            count: data.orders_with_incomplete_cost,
          })}
        </p>
      )}

      {/* Per-order table */}
      <Card className="py-0">
        <Table>
          <TableHeader>
            <TableRow className="hover:bg-transparent">
              <TableHead className="w-28">{t("orders.col.code")}</TableHead>
              <TableHead>{t("orders.col.customerShort")}</TableHead>
              <TableHead className="hidden w-28 lg:table-cell">
                {t("orders.col.date")}
              </TableHead>
              <TableHead className="w-28 text-right">
                {t("orders.col.revenue")}
              </TableHead>
              <TableHead className="hidden w-28 text-right lg:table-cell">
                {t("orders.col.cost")}
              </TableHead>
              <TableHead className="w-28 text-right">{t("orders.col.profit")}</TableHead>
              <TableHead className="hidden w-20 text-right lg:table-cell">
                {t("orders.col.margin")}
              </TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {data.orders.map((o) => (
              <TableRow key={o.order_id}>
                <TableCell className="font-medium tabular-nums">
                  {o.tracking_code}
                  {!o.cost_complete && (
                    <AlertTriangle
                      className="ml-1 inline size-3.5 text-amber-600"
                      aria-label={t("reports.profit.incompleteAria")}
                    />
                  )}
                </TableCell>
                <TableCell className="max-w-32 truncate">
                  {o.customer_name}
                </TableCell>
                <TableCell className="hidden text-muted-foreground lg:table-cell">
                  {formatDate(o.created_at)}
                </TableCell>
                <TableCell className="text-right tabular-nums">
                  {formatMoney(o.revenue)}
                </TableCell>
                <TableCell className="hidden text-right tabular-nums lg:table-cell">
                  {formatMoney(o.cost)}
                </TableCell>
                <TableCell
                  className={cn(
                    "text-right font-medium tabular-nums",
                    toNumber(o.profit) >= 0 ? "text-green-600" : "text-destructive",
                  )}
                >
                  {formatMoney(o.profit)}
                </TableCell>
                <TableCell className="hidden text-right tabular-nums text-muted-foreground lg:table-cell">
                  {o.margin_pct != null ? `${Number(o.margin_pct).toFixed(0)}%` : "—"}
                </TableCell>
              </TableRow>
            ))}
            {data.orders.length === 0 && (
              <TableRow className="hover:bg-transparent">
                <TableCell
                  colSpan={7}
                  className="py-10 text-center text-muted-foreground"
                >
                  {t("reports.profit.empty")}
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </Card>
    </div>
  );
}

const AGING_LABEL_KEY = {
  d0_7: "reports.receivables.agingD0_7",
  d8_30: "reports.receivables.agingD8_30",
  d31_60: "reports.receivables.agingD31_60",
  d61_plus: "reports.receivables.agingD61Plus",
} as const satisfies Record<AgingBucketId, string>;

function ReceivablesPanel() {
  const { t } = useI18n();
  const { data, isLoading } = useQuery({
    queryKey: ["reports", "receivables"],
    queryFn: getReceivablesReport,
  });

  if (isLoading || !data) return <Skeleton className="h-60 w-full" />;

  return (
    <div className="space-y-4">
      <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
        <SummaryCard
          label={t("reports.receivables.outstanding")}
          value={formatMoney(data.total_outstanding)}
          tone="negative"
        />
        <SummaryCard
          label={t("reports.receivables.ordersOwing")}
          value={String(data.orders_count)}
        />
        <SummaryCard
          label={t("reports.receivables.collectionRate")}
          value={`${Number(data.collection_rate_pct).toFixed(0)}%`}
        />
        <SummaryCard
          label={t("reports.receivables.depositShortfall")}
          value={formatMoney(data.deposit_shortfall)}
          tone={toNumber(data.deposit_shortfall) > 0 ? "negative" : undefined}
        />
      </div>

      {/* Aging buckets */}
      <Card className="py-0">
        <CardContent className="space-y-3 px-4 py-4">
          <p className="text-sm font-medium">
            {t("reports.receivables.agingTitle")}
          </p>
          <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
            {data.buckets.map((b) => (
              <div key={b.bucket} className="rounded-lg border border-border p-3">
                <p className="text-xs text-muted-foreground">
                  {t(AGING_LABEL_KEY[b.bucket])}
                </p>
                <p
                  className={cn(
                    "mt-0.5 text-base font-semibold tabular-nums",
                    b.bucket === "d61_plus" &&
                      b.orders_count > 0 &&
                      "text-destructive",
                  )}
                >
                  {formatMoney(b.outstanding)}
                </p>
                <p className="text-xs tabular-nums text-muted-foreground">
                  {t("reports.overview.ordersCount", { count: b.orders_count })}
                </p>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      <Card className="py-0">
        <Table>
          <TableHeader>
            <TableRow className="hover:bg-transparent">
              <TableHead className="w-28">{t("orders.col.code")}</TableHead>
              <TableHead>{t("orders.col.customerShort")}</TableHead>
              <TableHead className="hidden w-36 lg:table-cell">
                {t("orders.col.status")}
              </TableHead>
              <TableHead className="hidden w-24 text-right lg:table-cell">
                {t("reports.receivables.colAge")}
              </TableHead>
              <TableHead className="hidden w-28 text-right lg:table-cell">
                {t("orders.col.totalShort")}
              </TableHead>
              <TableHead className="hidden w-28 text-right lg:table-cell">
                {t("orders.col.collected")}
              </TableHead>
              <TableHead className="w-32 text-right">{t("orders.col.remaining")}</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {data.orders.map((o) => (
              <TableRow key={o.order_id}>
                <TableCell className="font-medium tabular-nums">
                  {o.tracking_code}
                  {!o.deposit_covered && (
                    <AlertTriangle
                      className="ml-1 inline size-3.5 text-amber-600"
                      aria-label={t("reports.receivables.depositUncoveredAria")}
                    />
                  )}
                </TableCell>
                <TableCell className="max-w-32 truncate">
                  {o.customer_name}
                </TableCell>
                <TableCell className="hidden lg:table-cell">
                  <Badge variant={STATUS_VARIANT[o.status]}>
                    {orderStatusLabel(o.status)}
                  </Badge>
                </TableCell>
                <TableCell
                  className={cn(
                    "hidden text-right tabular-nums lg:table-cell",
                    o.aging_bucket === "d61_plus"
                      ? "font-medium text-destructive"
                      : "text-muted-foreground",
                  )}
                >
                  {t("reports.receivables.ageDays", { days: o.age_days })}
                </TableCell>
                <TableCell className="hidden text-right tabular-nums lg:table-cell">
                  {formatMoney(o.total_amount)}
                </TableCell>
                <TableCell className="hidden text-right tabular-nums lg:table-cell">
                  {formatMoney(o.total_collected)}
                </TableCell>
                <TableCell className="text-right font-semibold tabular-nums text-destructive">
                  {formatMoney(o.remaining)}
                </TableCell>
              </TableRow>
            ))}
            {data.orders.length === 0 && (
              <TableRow className="hover:bg-transparent">
                <TableCell
                  colSpan={7}
                  className="py-10 text-center text-muted-foreground"
                >
                  {t("reports.receivables.empty")}
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </Card>
    </div>
  );
}

function TripsPanel() {
  const { t } = useI18n();
  const { data, isLoading } = useQuery({
    queryKey: ["reports", "trips"],
    queryFn: getTripReport,
  });

  if (isLoading || !data) return <Skeleton className="h-60 w-full" />;

  const profit = toNumber(data.total_profit);

  return (
    <div className="space-y-4">
      <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
        <SummaryCard
          label={t("reports.trips.tripsCount")}
          value={String(data.trips_count)}
        />
        <SummaryCard
          label={t("reports.trips.totalRevenue")}
          value={formatMoney(data.total_revenue)}
        />
        <SummaryCard
          label={t("reports.trips.totalCost")}
          value={formatMoney(data.total_cost)}
        />
        <SummaryCard
          label={t("reports.trips.totalProfit")}
          value={formatMoney(data.total_profit)}
          tone={profit >= 0 ? "positive" : "negative"}
        />
      </div>

      <Card className="py-0">
        <Table>
          <TableHeader>
            <TableRow className="hover:bg-transparent">
              <TableHead>{t("reports.trips.colTrip")}</TableHead>
              <TableHead className="hidden w-16 text-right lg:table-cell">
                {t("reports.trips.colOrders")}
              </TableHead>
              <TableHead className="w-28 text-right">
                {t("reports.trips.colRevenue")}
              </TableHead>
              <TableHead className="w-28 text-right">
                {t("reports.trips.colProfit")}
              </TableHead>
              <TableHead className="hidden w-36 lg:table-cell">
                {t("reports.trips.colProgress")}
              </TableHead>
              <TableHead className="hidden w-28 text-right lg:table-cell">
                {t("reports.trips.colOutstanding")}
              </TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {data.trips.map((trip) => {
              const progress = Number(trip.purchase_progress_pct);
              return (
                <TableRow key={trip.trip_id}>
                  <TableCell>
                    <Link
                      href={`/trips/${trip.trip_id}`}
                      className="font-medium underline-offset-4 hover:underline"
                    >
                      {trip.trip_name}
                      {!trip.cost_complete && (
                        <AlertTriangle
                          className="ml-1 inline size-3.5 text-amber-600"
                          aria-label={t("reports.trips.incompleteAria")}
                        />
                      )}
                    </Link>
                    <p className="text-xs text-muted-foreground">
                      {trip.trip_code}{" "}
                      <Badge
                        variant={TRIP_STATUS_VARIANT[trip.status]}
                        className="ml-1"
                      >
                        {tripStatusLabel(trip.status)}
                      </Badge>
                    </p>
                  </TableCell>
                  <TableCell className="hidden text-right tabular-nums lg:table-cell">
                    {trip.orders_count}
                  </TableCell>
                  <TableCell className="text-right tabular-nums">
                    {formatMoney(trip.revenue)}
                  </TableCell>
                  <TableCell
                    className={cn(
                      "text-right font-medium tabular-nums",
                      toNumber(trip.profit) >= 0
                        ? "text-green-600"
                        : "text-destructive",
                    )}
                  >
                    {formatMoney(trip.profit)}
                  </TableCell>
                  <TableCell className="hidden lg:table-cell">
                    <div className="flex items-center gap-2">
                      <div className="h-1.5 w-16 overflow-hidden rounded-full bg-muted">
                        <div
                          className="h-full rounded-full bg-primary"
                          style={{ width: `${Math.min(100, progress)}%` }}
                        />
                      </div>
                      <span className="text-xs tabular-nums text-muted-foreground">
                        {t("reports.trips.progressCaption", {
                          bought: trip.purchased_quantity,
                          qty: trip.total_quantity,
                        })}
                      </span>
                    </div>
                  </TableCell>
                  <TableCell className="hidden text-right tabular-nums text-destructive lg:table-cell">
                    {formatMoney(trip.outstanding)}
                  </TableCell>
                </TableRow>
              );
            })}
            {data.trips.length === 0 && (
              <TableRow className="hover:bg-transparent">
                <TableCell
                  colSpan={6}
                  className="py-10 text-center text-muted-foreground"
                >
                  {t("reports.trips.empty")}
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </Card>
    </div>
  );
}

function ProductsPanel() {
  const { t } = useI18n();
  const [dateFrom, setDateFrom] = useState("");
  const [dateTo, setDateTo] = useState("");

  const { data, isLoading } = useQuery({
    queryKey: ["reports", "products", { dateFrom, dateTo }],
    queryFn: () =>
      getProductReport({
        date_from: dateFrom || undefined,
        date_to: dateTo || undefined,
      }),
  });

  if (isLoading || !data) return <Skeleton className="h-60 w-full" />;

  const profit = toNumber(data.total_profit);

  return (
    <div className="space-y-4">
      <DateRangeFilter
        dateFrom={dateFrom}
        dateTo={dateTo}
        setDateFrom={setDateFrom}
        setDateTo={setDateTo}
      />

      <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
        <SummaryCard
          label={t("reports.products.productsCount")}
          value={String(data.products_count)}
        />
        <SummaryCard
          label={t("reports.products.totalQuantity")}
          value={String(data.total_quantity)}
        />
        <SummaryCard
          label={t("reports.products.totalRevenue")}
          value={formatMoney(data.total_revenue)}
        />
        <SummaryCard
          label={t("reports.products.totalProfit")}
          value={formatMoney(data.total_profit)}
          tone={profit >= 0 ? "positive" : "negative"}
        />
      </div>

      <Card className="py-0">
        <Table>
          <TableHeader>
            <TableRow className="hover:bg-transparent">
              <TableHead>{t("reports.products.colProduct")}</TableHead>
              <TableHead className="w-20 text-right">
                {t("reports.products.colQty")}
              </TableHead>
              <TableHead className="hidden w-16 text-right lg:table-cell">
                {t("reports.products.colOrders")}
              </TableHead>
              <TableHead className="w-28 text-right">
                {t("reports.products.colRevenue")}
              </TableHead>
              <TableHead className="hidden w-28 text-right lg:table-cell">
                {t("reports.products.colProfit")}
              </TableHead>
              <TableHead className="hidden w-20 text-right lg:table-cell">
                {t("reports.products.colMargin")}
              </TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {data.products.map((p) => (
              <TableRow key={p.product_code}>
                <TableCell>
                  <span className="font-medium">
                    {p.product_name}
                    {!p.cost_complete && (
                      <AlertTriangle
                        className="ml-1 inline size-3.5 text-amber-600"
                        aria-label={t("reports.products.incompleteAria")}
                      />
                    )}
                  </span>
                  <p className="text-xs tabular-nums text-muted-foreground">
                    {p.product_code}
                  </p>
                </TableCell>
                <TableCell className="text-right tabular-nums">
                  {p.quantity_sold}
                </TableCell>
                <TableCell className="hidden text-right tabular-nums lg:table-cell">
                  {p.orders_count}
                </TableCell>
                <TableCell className="text-right tabular-nums">
                  {formatMoney(p.revenue)}
                </TableCell>
                <TableCell
                  className={cn(
                    "hidden text-right font-medium tabular-nums lg:table-cell",
                    toNumber(p.profit) >= 0
                      ? "text-green-600"
                      : "text-destructive",
                  )}
                >
                  {formatMoney(p.profit)}
                </TableCell>
                <TableCell className="hidden text-right tabular-nums text-muted-foreground lg:table-cell">
                  {p.margin_pct != null
                    ? `${Number(p.margin_pct).toFixed(0)}%`
                    : "—"}
                </TableCell>
              </TableRow>
            ))}
            {data.products.length === 0 && (
              <TableRow className="hover:bg-transparent">
                <TableCell
                  colSpan={6}
                  className="py-10 text-center text-muted-foreground"
                >
                  {t("reports.products.empty")}
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </Card>
    </div>
  );
}

function CustomersPanel() {
  const { t } = useI18n();
  const [dateFrom, setDateFrom] = useState("");
  const [dateTo, setDateTo] = useState("");

  const { data, isLoading } = useQuery({
    queryKey: ["reports", "customers", { dateFrom, dateTo }],
    queryFn: () =>
      getCustomerReport({
        date_from: dateFrom || undefined,
        date_to: dateTo || undefined,
      }),
  });

  if (isLoading || !data) return <Skeleton className="h-60 w-full" />;

  const filtered = Boolean(dateFrom || dateTo);

  return (
    <div className="space-y-4">
      <DateRangeFilter
        dateFrom={dateFrom}
        dateTo={dateTo}
        setDateFrom={setDateFrom}
        setDateTo={setDateTo}
      />

      <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
        <SummaryCard
          label={t("reports.customers.customersCount")}
          value={String(data.customers_count)}
        />
        <SummaryCard
          label={t("reports.customers.totalRevenue")}
          value={formatMoney(data.total_revenue)}
        />
        {filtered && (
          <>
            <SummaryCard
              label={t("reports.customers.newCustomers")}
              value={String(data.new_customers_count)}
              tone="positive"
            />
            <SummaryCard
              label={t("reports.customers.returningCustomers")}
              value={String(data.returning_customers_count)}
            />
          </>
        )}
      </div>

      <Card className="py-0">
        <Table>
          <TableHeader>
            <TableRow className="hover:bg-transparent">
              <TableHead>{t("reports.customers.colCustomer")}</TableHead>
              <TableHead className="w-16 text-right">
                {t("reports.customers.colOrders")}
              </TableHead>
              <TableHead className="w-28 text-right">
                {t("reports.customers.colRevenue")}
              </TableHead>
              <TableHead className="hidden w-28 text-right lg:table-cell">
                {t("reports.customers.colOutstanding")}
              </TableHead>
              <TableHead className="hidden w-28 text-right lg:table-cell">
                {t("reports.customers.colAov")}
              </TableHead>
              <TableHead className="hidden w-28 lg:table-cell">
                {t("reports.customers.colLastOrder")}
              </TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {data.customers.map((c) => (
              <TableRow key={c.customer_id}>
                <TableCell>
                  <span className="font-medium">
                    {c.customer_name}
                    {filtered && c.is_new && (
                      <Badge variant="secondary" className="ml-1.5">
                        {t("reports.customers.newBadge")}
                      </Badge>
                    )}
                  </span>
                  {c.phone && (
                    <p className="text-xs tabular-nums text-muted-foreground">
                      {c.phone}
                    </p>
                  )}
                </TableCell>
                <TableCell className="text-right tabular-nums">
                  {c.orders_count}
                </TableCell>
                <TableCell className="text-right font-medium tabular-nums">
                  {formatMoney(c.revenue)}
                </TableCell>
                <TableCell
                  className={cn(
                    "hidden text-right tabular-nums lg:table-cell",
                    toNumber(c.outstanding) > 0
                      ? "text-destructive"
                      : "text-muted-foreground",
                  )}
                >
                  {formatMoney(c.outstanding)}
                </TableCell>
                <TableCell className="hidden text-right tabular-nums lg:table-cell">
                  {formatMoney(c.avg_order_value)}
                </TableCell>
                <TableCell className="hidden text-muted-foreground lg:table-cell">
                  {formatDate(c.last_order_at)}
                </TableCell>
              </TableRow>
            ))}
            {data.customers.length === 0 && (
              <TableRow className="hover:bg-transparent">
                <TableCell
                  colSpan={6}
                  className="py-10 text-center text-muted-foreground"
                >
                  {t("reports.customers.empty")}
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </Card>
    </div>
  );
}

function OperationsPanel() {
  const { t } = useI18n();
  const [dateFrom, setDateFrom] = useState("");
  const [dateTo, setDateTo] = useState("");

  const { data, isLoading } = useQuery({
    queryKey: ["reports", "operations", { dateFrom, dateTo }],
    queryFn: () =>
      getOperationsReport({
        date_from: dateFrom || undefined,
        date_to: dateTo || undefined,
      }),
  });

  if (isLoading || !data) return <Skeleton className="h-60 w-full" />;

  return (
    <div className="space-y-4">
      <DateRangeFilter
        dateFrom={dateFrom}
        dateTo={dateTo}
        setDateFrom={setDateFrom}
        setDateTo={setDateTo}
      />

      <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
        <SummaryCard
          label={t("reports.operations.ordersInPeriod")}
          value={String(data.orders_count)}
        />
        <SummaryCard
          label={t("reports.operations.cancellationRate")}
          value={`${Number(data.cancellation_rate_pct).toFixed(0)}%`}
          tone={Number(data.cancellation_rate_pct) > 0 ? "negative" : undefined}
        />
        <SummaryCard
          label={t("reports.operations.completionRate")}
          value={`${Number(data.purchase_completion_pct).toFixed(0)}%`}
          tone="positive"
        />
        <SummaryCard
          label={t("reports.operations.unassigned")}
          value={String(data.unassigned_count)}
          tone={data.unassigned_count > 0 ? "negative" : undefined}
        />
      </div>

      <Card className="py-0">
        <CardContent className="space-y-3 px-4 py-4">
          <p className="text-sm font-medium">
            {t("reports.operations.stuckTitle", { days: data.stale_days })}
          </p>
          {data.stuck.length === 0 ? (
            <p className="py-4 text-center text-sm text-muted-foreground">
              {t("reports.operations.stuckEmpty")}
            </p>
          ) : (
            <Table>
              <TableHeader>
                <TableRow className="hover:bg-transparent">
                  <TableHead>{t("reports.operations.colStatus")}</TableHead>
                  <TableHead className="w-20 text-right">
                    {t("reports.operations.colCount")}
                  </TableHead>
                  <TableHead className="w-24 text-right">
                    {t("reports.operations.colOldest")}
                  </TableHead>
                  <TableHead className="w-32 text-right">
                    {t("reports.operations.colAmount")}
                  </TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {data.stuck.map((s) => (
                  <TableRow key={s.status} className="bg-amber-500/5">
                    <TableCell>
                      <StatusBadge status={s.status} size="sm" />
                    </TableCell>
                    <TableCell className="text-right font-medium tabular-nums">
                      {s.count}
                    </TableCell>
                    <TableCell className="text-right tabular-nums text-amber-700">
                      {t("reports.operations.oldestDays", { days: s.oldest_days })}
                    </TableCell>
                    <TableCell className="text-right tabular-nums">
                      {formatMoney(s.total_amount)}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

"use client";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { AlertTriangle } from "lucide-react";

import { cn } from "@/lib/utils";
import {
  ORDER_STATUS_LABELS,
  STATUS_STYLE,
  STATUS_VARIANT,
  formatDate,
  formatMoney,
  toNumber,
} from "@/lib/orders";
import {
  getCashFlowReport,
  getDailySummaryReport,
  getOverviewReport,
  getProfitReport,
  getReceivablesReport,
} from "@/lib/reports";
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
  { id: "overview", label: "Tổng quan" },
  { id: "daily", label: "Theo ngày" },
  { id: "cashflow", label: "Dòng tiền" },
  { id: "profit", label: "Lãi / lỗ" },
  { id: "receivables", label: "Công nợ" },
] as const;

type TabId = (typeof TABS)[number]["id"];

/** Reports screen: overview dashboard, daily pulse, cash flow, profit, debt. */
export function ReportsView() {
  const [tab, setTab] = useState<TabId>("overview");

  return (
    <div className="space-y-4">
      <div className="-mx-4 flex gap-1.5 overflow-x-auto px-4 pb-1 [scrollbar-width:none] [&::-webkit-scrollbar]:hidden">
        {TABS.map((t) => {
          const active = tab === t.id;
          return (
            <Button
              key={t.id}
              size="sm"
              variant={active ? "default" : "secondary"}
              aria-pressed={active}
              onClick={() => setTab(t.id)}
              className="shrink-0"
            >
              {t.label}
            </Button>
          );
        })}
      </div>

      {tab === "overview" && <OverviewPanel />}
      {tab === "daily" && <DailyPanel />}
      {tab === "cashflow" && <CashFlowPanel />}
      {tab === "profit" && <ProfitPanel />}
      {tab === "receivables" && <ReceivablesPanel />}
    </div>
  );
}

/** Reusable [Từ ngày / Đến ngày] filter for the date-scoped panels. */
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
  return (
    <div className="flex flex-wrap items-end gap-2">
      <div className="space-y-1">
        <Label htmlFor="date-from" className="text-xs">
          Từ ngày
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
          Đến ngày
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
          Xóa lọc
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

function OverviewPanel() {
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
        <SummaryCard label="Doanh thu" value={formatMoney(data.total_revenue)} />
        <SummaryCard
          label="Đã thu"
          value={formatMoney(data.total_collected)}
          tone="positive"
        />
        <SummaryCard
          label="Công nợ"
          value={formatMoney(data.total_outstanding)}
          tone="negative"
        />
        <SummaryCard
          label="Cọc cần thu"
          value={formatMoney(data.total_deposit_due)}
        />
        <SummaryCard label="Chi phí" value={formatMoney(data.total_cost)} />
        <SummaryCard
          label="Lãi / lỗ"
          value={formatMoney(data.total_profit)}
          tone={profit >= 0 ? "positive" : "negative"}
        />
      </div>

      {data.unassigned_count > 0 && (
        <p className="flex items-center gap-2 rounded-lg bg-amber-500/10 px-3 py-2 text-sm text-amber-700">
          <AlertTriangle className="size-4 shrink-0" aria-hidden />
          {data.unassigned_count} đơn đã chốt / chờ xử lý chưa gom vào chuyến nào.
        </p>
      )}

      <Card className="py-0">
        <CardContent className="space-y-3 px-4 py-4">
          <div className="flex items-center justify-between">
            <p className="text-sm font-medium">Đường ống đơn hàng</p>
            <span className="text-xs text-muted-foreground">
              {data.orders_count} đơn
            </span>
          </div>
          {data.status_breakdown.map((s) => {
            const pct = (s.count / maxCount) * 100;
            return (
              <div key={s.status} className="space-y-1.5">
                <div className="flex items-center justify-between gap-2">
                  <StatusBadge status={s.status} size="sm" />
                  <span className="text-xs tabular-nums text-muted-foreground">
                    {s.count} đơn · {formatMoney(s.total_amount)}
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

const shortDate = (iso: string) =>
  new Date(iso).toLocaleDateString("vi-VN", {
    day: "2-digit",
    month: "2-digit",
  });

function DailyPanel() {
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
        <SummaryCard label="Số đơn" value={String(data.orders_count)} />
        <SummaryCard label="Đã chốt" value={String(data.confirmed_count)} />
        <SummaryCard label="Doanh thu" value={formatMoney(data.revenue)} />
        <SummaryCard
          label="Tiền thu"
          value={formatMoney(data.collected)}
          tone="positive"
        />
      </div>

      {data.days.length === 0 ? (
        <p className="py-10 text-center text-sm text-muted-foreground">
          Chưa có đơn nào trong khoảng thời gian này.
        </p>
      ) : (
        <Card className="py-0">
          <CardContent className="space-y-3 px-4 py-4">
            <div className="flex items-center justify-between">
              <p className="text-sm font-medium">Đơn theo ngày</p>
              <div className="flex items-center gap-3 text-xs text-muted-foreground">
                <span className="flex items-center gap-1">
                  <span className="size-2 rounded-full bg-primary" /> đã chốt
                </span>
                <span className="flex items-center gap-1">
                  <span className="size-2 rounded-full bg-primary/25" /> chưa
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
                      title={`${formatDate(d.date)}: ${d.orders_count} đơn (${d.confirmed_count} đã chốt) · ${formatMoney(d.revenue)}`}
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
          label="Tiền vào"
          value={formatMoney(data.cash_in)}
          tone="positive"
        />
        <SummaryCard
          label="Tiền ra (mua hàng)"
          value={formatMoney(data.cash_out)}
          tone="negative"
        />
        <SummaryCard
          label="Hoàn lại khách"
          value={formatMoney(data.refunded)}
          tone="negative"
        />
        <SummaryCard
          label="Net (vào − ra)"
          value={formatMoney(data.net)}
          tone={net >= 0 ? "positive" : "negative"}
        />
      </div>

      <Card className="py-0">
        <CardContent className="space-y-1 px-4 py-4">
          <p className="text-sm font-medium">Chi phí dự kiến còn lại</p>
          <p className="text-2xl font-bold tabular-nums text-amber-600">
            {formatMoney(data.pending_purchase_cost)}
          </p>
          <p className="text-xs text-muted-foreground">
            Số tiền ước tính sẽ cần chi để mua nốt hàng đã đặt (theo giá mua thực
            tế đã ghi).
          </p>
        </CardContent>
      </Card>
    </div>
  );
}

function ProfitPanel() {
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
      {/* Date filter */}
      <div className="flex flex-wrap items-end gap-2">
        <div className="space-y-1">
          <Label htmlFor="date-from" className="text-xs">
            Từ ngày
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
            Đến ngày
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
            Xóa lọc
          </Button>
        )}
      </div>

      {/* Summary */}
      <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
        <SummaryCard label="Doanh thu" value={formatMoney(data.total_revenue)} />
        <SummaryCard label="Giá vốn (đã ghi)" value={formatMoney(data.total_cost)} />
        <SummaryCard
          label="Lãi / lỗ"
          value={formatMoney(data.total_profit)}
          tone={profit >= 0 ? "positive" : "negative"}
        />
        <SummaryCard label="Số đơn" value={String(data.orders_count)} />
      </div>

      {data.orders_with_incomplete_cost > 0 && (
        <p className="flex items-center gap-2 rounded-lg bg-amber-500/10 px-3 py-2 text-sm text-amber-700">
          <AlertTriangle className="size-4 shrink-0" aria-hidden />
          {data.orders_with_incomplete_cost} đơn chưa nhập đủ giá mua thực tế —
          số lãi đang là ước tính thấp nhất của chi phí.
        </p>
      )}

      {/* Per-order table */}
      <Card className="py-0">
        <Table>
          <TableHeader>
            <TableRow className="hover:bg-transparent">
              <TableHead className="w-28">Mã Code</TableHead>
              <TableHead>Khách</TableHead>
              <TableHead className="hidden w-28 lg:table-cell">Ngày</TableHead>
              <TableHead className="w-28 text-right">Doanh thu</TableHead>
              <TableHead className="hidden w-28 text-right lg:table-cell">
                Giá vốn
              </TableHead>
              <TableHead className="w-28 text-right">Lãi</TableHead>
              <TableHead className="hidden w-20 text-right lg:table-cell">
                Biên %
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
                      aria-label="Chưa đủ giá vốn"
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
                  Chưa có đơn nào trong khoảng thời gian này.
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </Card>
    </div>
  );
}

function ReceivablesPanel() {
  const { data, isLoading } = useQuery({
    queryKey: ["reports", "receivables"],
    queryFn: getReceivablesReport,
  });

  if (isLoading || !data) return <Skeleton className="h-60 w-full" />;

  return (
    <div className="space-y-4">
      <div className="grid grid-cols-2 gap-3 lg:max-w-md">
        <SummaryCard
          label="Tổng phải thu"
          value={formatMoney(data.total_outstanding)}
          tone="negative"
        />
        <SummaryCard label="Số đơn còn nợ" value={String(data.orders_count)} />
      </div>

      <Card className="py-0">
        <Table>
          <TableHeader>
            <TableRow className="hover:bg-transparent">
              <TableHead className="w-28">Mã Code</TableHead>
              <TableHead>Khách</TableHead>
              <TableHead className="hidden w-36 lg:table-cell">Trạng thái</TableHead>
              <TableHead className="hidden w-28 text-right lg:table-cell">
                Tổng đơn
              </TableHead>
              <TableHead className="hidden w-28 text-right lg:table-cell">
                Đã thu
              </TableHead>
              <TableHead className="w-32 text-right">Còn nợ</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {data.orders.map((o) => (
              <TableRow key={o.order_id}>
                <TableCell className="font-medium tabular-nums">
                  {o.tracking_code}
                </TableCell>
                <TableCell className="max-w-32 truncate">
                  {o.customer_name}
                </TableCell>
                <TableCell className="hidden lg:table-cell">
                  <Badge variant={STATUS_VARIANT[o.status]}>
                    {ORDER_STATUS_LABELS[o.status]}
                  </Badge>
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
                  colSpan={6}
                  className="py-10 text-center text-muted-foreground"
                >
                  Không còn đơn nào nợ tiền 🎉
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </Card>
    </div>
  );
}

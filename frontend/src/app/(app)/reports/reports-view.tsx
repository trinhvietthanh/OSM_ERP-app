"use client";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { AlertTriangle } from "lucide-react";

import { cn } from "@/lib/utils";
import {
  ORDER_STATUS_LABELS,
  STATUS_VARIANT,
  formatDate,
  formatMoney,
  toNumber,
} from "@/lib/orders";
import { getProfitReport, getReceivablesReport } from "@/lib/reports";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Skeleton } from "@/components/ui/skeleton";
import { Card, CardContent } from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

const TABS = [
  { id: "profit", label: "Lãi / lỗ" },
  { id: "receivables", label: "Công nợ" },
] as const;

type TabId = (typeof TABS)[number]["id"];

/** Reports screen: per-order profit and outstanding balances. */
export function ReportsView() {
  const [tab, setTab] = useState<TabId>("profit");

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap gap-1.5">
        {TABS.map((t) => (
          <Button
            key={t.id}
            size="sm"
            variant={tab === t.id ? "secondary" : "ghost"}
            aria-pressed={tab === t.id}
            onClick={() => setTab(t.id)}
          >
            {t.label}
          </Button>
        ))}
      </div>

      {tab === "profit" ? <ProfitPanel /> : <ReceivablesPanel />}
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

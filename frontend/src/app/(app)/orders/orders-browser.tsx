"use client";

import { Fragment, useMemo, useState } from "react";
import { useSearchParams } from "next/navigation";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { ChevronDown, ChevronUp, Search } from "lucide-react";

import { cn } from "@/lib/utils";
import { ApiError } from "@/lib/api";
import { Input } from "@/components/ui/input";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  CANCELLABLE,
  NEXT_ORDER_STATUS,
  ORDER_STATUS_LABELS,
  STATUS_VARIANT,
  addReceipt,
  changeOrderStatus,
  formatDate,
  formatMoney,
  listOrders,
  toNumber,
  type Order,
  type OrderStatus,
  type ReceiptKind,
  type ReceiptMethod,
} from "@/lib/orders";

const FILTERS: ReadonlyArray<OrderStatus | "all"> = [
  "all",
  "pending",
  "confirmed",
  "purchasing",
  "purchased",
  "arrived",
  "delivered",
  "cancelled",
];

/** Orders list panel (tab "Danh sách"). Reads `?q=` from the URL. */
export function OrdersList() {
  const searchParams = useSearchParams();
  const urlQuery = searchParams.get("q") ?? "";

  const [query, setQuery] = useState(urlQuery);
  const [lastUrlQuery, setLastUrlQuery] = useState(urlQuery);
  if (urlQuery !== lastUrlQuery) {
    setLastUrlQuery(urlQuery);
    setQuery(urlQuery);
  }
  const [status, setStatus] = useState<OrderStatus | "all">("all");
  const [openId, setOpenId] = useState<string | null>(null);

  const {
    data: orders = [],
    isLoading,
    isError,
    error,
  } = useQuery({ queryKey: ["orders"], queryFn: () => listOrders() });

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    return orders.filter((o) => {
      const matchesQ =
        !q ||
        o.customer_name.toLowerCase().includes(q) ||
        o.tracking_code.toLowerCase().includes(q);
      const matchesStatus = status === "all" || o.status === status;
      return matchesQ && matchesStatus;
    });
  }, [orders, query, status]);

  const countFor = (value: OrderStatus | "all") =>
    value === "all"
      ? orders.length
      : orders.filter((o) => o.status === value).length;

  if (isLoading) {
    return (
      <div className="space-y-3">
        <Skeleton className="h-9 w-full" />
        <Skeleton className="h-40 w-full" />
      </div>
    );
  }
  if (isError) {
    return (
      <p className="py-10 text-center text-sm text-destructive">
        Không tải được danh sách đơn: {(error as Error).message}
      </p>
    );
  }

  return (
    <div className="space-y-4">
      {/* Status filter */}
      <div className="flex flex-wrap gap-1.5">
        {FILTERS.map((value) => {
          const active = status === value;
          return (
            <Button
              key={value}
              size="sm"
              variant={active ? "secondary" : "ghost"}
              aria-pressed={active}
              onClick={() => setStatus(value)}
              className="gap-1.5"
            >
              {value === "all" ? "Tất cả" : ORDER_STATUS_LABELS[value]}
              <span
                className={cn(
                  "rounded-full px-1.5 text-xs tabular-nums",
                  active
                    ? "bg-background/60 text-muted-foreground"
                    : "bg-muted text-muted-foreground",
                )}
              >
                {countFor(value)}
              </span>
            </Button>
          );
        })}
      </div>

      {/* Mobile-only quick search */}
      <div className="relative lg:hidden">
        <Search
          className="pointer-events-none absolute top-1/2 left-3 size-4 -translate-y-1/2 text-muted-foreground"
          aria-hidden
        />
        <Input
          value={query}
          onChange={(event) => setQuery(event.target.value)}
          placeholder="Tìm theo mã Code hoặc tên khách"
          className="pl-9"
          inputMode="search"
        />
      </div>

      {/* Desktop data table */}
      <Card className="hidden py-0 lg:block">
        <Table>
          <TableHeader>
            <TableRow className="hover:bg-transparent">
              <TableHead className="w-28">Mã Code</TableHead>
              <TableHead>Khách hàng</TableHead>
              <TableHead className="w-28">Ngày tạo</TableHead>
              <TableHead className="w-32 text-right">Tổng tiền</TableHead>
              <TableHead className="w-32 text-right">Còn lại</TableHead>
              <TableHead className="w-44">Trạng thái</TableHead>
              <TableHead className="w-10" />
            </TableRow>
          </TableHeader>
          <TableBody>
            {filtered.map((o) => (
              <Fragment key={o.id}>
                <TableRow
                  className="cursor-pointer"
                  onClick={() => setOpenId(openId === o.id ? null : o.id)}
                >
                  <TableCell className="font-medium tabular-nums">
                    {o.tracking_code}
                  </TableCell>
                  <TableCell>{o.customer_name}</TableCell>
                  <TableCell className="text-muted-foreground">
                    {formatDate(o.created_at)}
                  </TableCell>
                  <TableCell className="text-right font-semibold tabular-nums">
                    {formatMoney(o.total_amount)}
                  </TableCell>
                  <TableCell
                    className={cn(
                      "text-right tabular-nums",
                      toNumber(o.remaining) > 0
                        ? "text-destructive"
                        : "text-muted-foreground",
                    )}
                  >
                    {formatMoney(o.remaining)}
                  </TableCell>
                  <TableCell>
                    <div className="flex flex-wrap items-center gap-1">
                      <Badge variant={STATUS_VARIANT[o.status]}>
                        {ORDER_STATUS_LABELS[o.status]}
                      </Badge>
                      {o.trip_id && <Badge variant="secondary">Đã gom</Badge>}
                      {o.is_separate && <Badge variant="outline">Riêng</Badge>}
                    </div>
                  </TableCell>
                  <TableCell className="text-muted-foreground">
                    {openId === o.id ? (
                      <ChevronUp className="size-4" aria-hidden />
                    ) : (
                      <ChevronDown className="size-4" aria-hidden />
                    )}
                  </TableCell>
                </TableRow>
                {openId === o.id && (
                  <TableRow className="hover:bg-transparent">
                    <TableCell colSpan={7} className="bg-muted/30 p-4">
                      <OrderDetail order={o} />
                    </TableCell>
                  </TableRow>
                )}
              </Fragment>
            ))}
            {filtered.length === 0 && (
              <TableRow className="hover:bg-transparent">
                <TableCell
                  colSpan={7}
                  className="py-10 text-center text-muted-foreground"
                >
                  Không có đơn nào phù hợp.
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </Card>

      {/* Mobile cards */}
      <div className="grid gap-3 lg:hidden">
        {filtered.map((o) => (
          <Card key={o.id} className="py-0">
            <CardContent className="px-4 py-3">
              <button
                type="button"
                className="flex w-full items-center justify-between gap-3 text-left"
                onClick={() => setOpenId(openId === o.id ? null : o.id)}
              >
                <div className="min-w-0">
                  <p className="truncate font-medium">{o.customer_name}</p>
                  <p className="text-xs text-muted-foreground">
                    {o.tracking_code} · {formatDate(o.created_at)}
                  </p>
                  {(o.trip_id || o.is_separate) && (
                    <p className="mt-1 text-xs text-muted-foreground">
                      {o.trip_id ? "Đã gom chuyến" : "Giao riêng"}
                    </p>
                  )}
                </div>
                <div className="flex flex-col items-end gap-1">
                  <span className="font-semibold">
                    {formatMoney(o.total_amount)}
                  </span>
                  <Badge variant={STATUS_VARIANT[o.status]}>
                    {ORDER_STATUS_LABELS[o.status]}
                  </Badge>
                </div>
              </button>
              {openId === o.id && (
                <div className="mt-3 border-t border-border pt-3">
                  <OrderDetail order={o} />
                </div>
              )}
            </CardContent>
          </Card>
        ))}

        {filtered.length === 0 && (
          <p className="py-10 text-center text-sm text-muted-foreground">
            Không có đơn nào phù hợp.
          </p>
        )}
      </div>
    </div>
  );
}

const METHOD_LABELS: Record<ReceiptMethod, string> = {
  cash: "Tiền mặt",
  bank_transfer: "Chuyển khoản",
  other: "Khác",
};

/** Expanded order detail: lines, receipts, collect-money form, status actions. */
function OrderDetail({ order }: { order: Order }) {
  const queryClient = useQueryClient();
  const [amount, setAmount] = useState("");
  const [method, setMethod] = useState<ReceiptMethod>("cash");
  const [kind, setKind] = useState<ReceiptKind>(
    order.status === "cancelled" ? "refund" : "collection",
  );

  const invalidate = () =>
    queryClient.invalidateQueries({ queryKey: ["orders"] });

  const statusMutation = useMutation({
    mutationFn: (status: OrderStatus) => changeOrderStatus(order.id, status),
    onSuccess: (updated) => {
      toast.success(
        `Đơn ${updated.tracking_code}: ${ORDER_STATUS_LABELS[updated.status]}`,
      );
      invalidate();
    },
    onError: (err: Error) =>
      toast.error(err instanceof ApiError ? err.message : "Có lỗi xảy ra"),
  });

  const receiptMutation = useMutation({
    mutationFn: () => addReceipt(order.id, { amount, method, kind }),
    onSuccess: () => {
      toast.success(kind === "refund" ? "Đã ghi phiếu hoàn" : "Đã ghi phiếu thu");
      setAmount("");
      invalidate();
    },
    onError: (err: Error) =>
      toast.error(err instanceof ApiError ? err.message : "Có lỗi xảy ra"),
  });

  const next = NEXT_ORDER_STATUS[order.status];

  return (
    <div className="grid gap-4 lg:grid-cols-2">
      {/* Lines */}
      <div className="space-y-2">
        <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
          Dòng hàng
        </p>
        <ul className="space-y-1.5 text-sm">
          {order.lines.map((line) => (
            <li key={line.id} className="flex items-center justify-between gap-2">
              <span className="min-w-0 truncate">
                {line.product_name}
                <span className="text-muted-foreground"> × {line.quantity}</span>
              </span>
              <span className="shrink-0 tabular-nums">
                {formatMoney(line.line_total)}
              </span>
            </li>
          ))}
        </ul>
        <Separator />
        <div className="space-y-1 text-sm">
          <div className="flex justify-between">
            <span className="text-muted-foreground">Tổng tiền</span>
            <span className="font-semibold tabular-nums">
              {formatMoney(order.total_amount)}
            </span>
          </div>
          <div className="flex justify-between">
            <span className="text-muted-foreground">Cọc yêu cầu</span>
            <span className="tabular-nums">{formatMoney(order.deposit_due)}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-muted-foreground">Đã thu</span>
            <span className="tabular-nums">
              {formatMoney(order.total_collected)}
            </span>
          </div>
          <div className="flex justify-between font-medium">
            <span>Còn lại</span>
            <span
              className={cn(
                "tabular-nums",
                toNumber(order.remaining) > 0 && "text-destructive",
              )}
            >
              {formatMoney(order.remaining)}
            </span>
          </div>
        </div>
        {order.note && (
          <p className="rounded-lg bg-muted px-2.5 py-1.5 text-xs text-muted-foreground">
            {order.note}
          </p>
        )}
      </div>

      {/* Receipts + actions */}
      <div className="space-y-3">
        <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
          Phiếu thu
        </p>
        {order.receipts.length === 0 ? (
          <p className="text-sm text-muted-foreground">Chưa thu khoản nào.</p>
        ) : (
          <ul className="space-y-1.5 text-sm">
            {order.receipts.map((r) => (
              <li key={r.id} className="flex items-center justify-between gap-2">
                <span className="text-muted-foreground">
                  {formatDate(r.received_at)} · {METHOD_LABELS[r.method]}
                  {r.kind === "refund" ? " · Hoàn tiền" : ""}
                  {r.note ? ` · ${r.note}` : ""}
                </span>
                <span
                  className={cn(
                    "shrink-0 font-medium tabular-nums",
                    r.kind === "refund" && "text-destructive",
                  )}
                >
                  {r.kind === "refund" ? "−" : ""}
                  {formatMoney(r.amount)}
                </span>
              </li>
            ))}
          </ul>
        )}
        {toNumber(order.total_refunded) > 0 && (
          <p className="text-xs text-muted-foreground">
            Đã hoàn {formatMoney(order.total_refunded)} cho khách.
          </p>
        )}

        {/* Thu tiền khi đơn còn sống và còn thiếu; hoàn tiền khi còn giữ tiền
            của khách (kể cả đơn đã hủy — hoàn cọc). */}
        {((order.status !== "cancelled" && toNumber(order.remaining) > 0) ||
          toNumber(order.total_collected) > 0) && (
          <form
            className="flex flex-wrap items-center gap-2"
            onSubmit={(event) => {
              event.preventDefault();
              if (Number(amount) > 0) receiptMutation.mutate();
            }}
          >
            <select
              value={kind}
              onChange={(event) => setKind(event.target.value as ReceiptKind)}
              aria-label="Loại phiếu"
              className="h-9 rounded-md border border-input bg-transparent px-2 text-sm"
            >
              {order.status !== "cancelled" && (
                <option value="collection">Thu tiền</option>
              )}
              {toNumber(order.total_collected) > 0 && (
                <option value="refund">Hoàn tiền</option>
              )}
            </select>
            <Input
              type="number"
              min={0}
              step={1000}
              value={amount}
              onChange={(event) => setAmount(event.target.value)}
              placeholder="Số tiền"
              aria-label="Số tiền"
              className="w-32"
            />
            <select
              value={method}
              onChange={(event) =>
                setMethod(event.target.value as ReceiptMethod)
              }
              aria-label="Hình thức"
              className="h-9 rounded-md border border-input bg-transparent px-2 text-sm"
            >
              <option value="cash">Tiền mặt</option>
              <option value="bank_transfer">Chuyển khoản</option>
              <option value="other">Khác</option>
            </select>
            <Button
              type="submit"
              size="sm"
              variant={kind === "refund" ? "destructive" : "default"}
              disabled={receiptMutation.isPending || Number(amount) <= 0}
            >
              {receiptMutation.isPending
                ? "Đang lưu…"
                : kind === "refund"
                  ? "Hoàn tiền"
                  : "Thu tiền"}
            </Button>
          </form>
        )}

        <div className="flex flex-wrap gap-2 pt-1">
          {next && !(order.trip_id && ["confirmed", "purchasing"].includes(order.status)) && (
            <Button
              size="sm"
              variant="secondary"
              disabled={statusMutation.isPending}
              onClick={() => statusMutation.mutate(next)}
            >
              → {ORDER_STATUS_LABELS[next]}
            </Button>
          )}
          {CANCELLABLE.has(order.status) && !order.trip_id && (
            <Button
              size="sm"
              variant="destructive"
              disabled={statusMutation.isPending}
              onClick={() => statusMutation.mutate("cancelled")}
            >
              Hủy đơn
            </Button>
          )}
        </div>
        {order.trip_id && (
          <p className="text-xs text-muted-foreground">
            Đơn thuộc một chuyến hàng — trạng thái Đang mua/Đã về VN sẽ tự cập
            nhật theo chuyến.
          </p>
        )}
      </div>
    </div>
  );
}

"use client";

import { useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";

import { ApiError } from "@/lib/api";
import {
  combineLines,
  formatDate,
  formatMoney,
  listOrders,
  toNumber,
  updateOrder,
} from "@/lib/orders";
import {
  attachOrders,
  createTrip,
  listTrips,
  type Trip,
} from "@/lib/trips";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Separator } from "@/components/ui/separator";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

/**
 * Gom đơn: pick confirmed/pending orders (not giao riêng, not already in a
 * trip) and attach them to a buying trip — either an existing PLANNING trip
 * or a new one created inline.
 */
export function ConsolidateOrders() {
  const router = useRouter();
  const queryClient = useQueryClient();
  const [selected, setSelected] = useState<Set<string>>(new Set());

  // Existing PLANNING trip to attach to; "new" = create inline.
  const [tripChoice, setTripChoice] = useState<string>("new");
  const [code, setCode] = useState("");
  const [name, setName] = useState("");
  const [shopper, setShopper] = useState("");

  const { data: orders = [], isLoading } = useQuery({
    queryKey: ["orders", { unassigned: true }],
    queryFn: () => listOrders({ unassigned: true }),
  });
  const { data: planningTrips = [] } = useQuery({
    queryKey: ["trips", { status: "planning" }],
    queryFn: () => listTrips("planning"),
  });
  const { data: allOrders = [] } = useQuery({
    queryKey: ["orders"],
    queryFn: () => listOrders(),
  });

  // Attachable: pending/confirmed only (backend enforces the same rule).
  const eligible = useMemo(
    () =>
      orders.filter((o) => o.status === "pending" || o.status === "confirmed"),
    [orders],
  );
  const separateOrders = useMemo(
    () =>
      allOrders.filter(
        (o) =>
          o.is_separate &&
          !o.trip_id &&
          (o.status === "pending" || o.status === "confirmed"),
      ),
    [allOrders],
  );

  const selectedOrders = eligible.filter((o) => selected.has(o.id));
  const combined = combineLines(selectedOrders);
  const grandTotal = selectedOrders.reduce(
    (sum, o) => sum + toNumber(o.total_amount),
    0,
  );
  const customers = [...new Set(selectedOrders.map((o) => o.customer_name))];

  const invalidate = () => {
    queryClient.invalidateQueries({ queryKey: ["orders"] });
    queryClient.invalidateQueries({ queryKey: ["trips"] });
  };

  const consolidateMutation = useMutation({
    mutationFn: async () => {
      let trip: Trip;
      if (tripChoice === "new") {
        trip = await createTrip({
          code: code.trim(),
          name: name.trim() || code.trim(),
          shopper_name: shopper.trim(),
        });
      } else {
        const existing = planningTrips.find((t) => t.id === tripChoice);
        if (!existing) throw new Error("Chuyến không còn ở trạng thái lên kế hoạch.");
        trip = existing;
      }
      await attachOrders(
        trip.id,
        selectedOrders.map((o) => o.id),
      );
      return trip;
    },
    onSuccess: (trip) => {
      toast.success(
        `Đã gom ${selectedOrders.length} đơn vào chuyến ${trip.code}`,
      );
      setSelected(new Set());
      invalidate();
      router.push(`/trips/${trip.id}`);
    },
    onError: (err: Error) =>
      toast.error(err instanceof ApiError ? err.message : err.message),
  });

  const reincludeMutation = useMutation({
    mutationFn: (id: string) => updateOrder(id, { is_separate: false }),
    onSuccess: () => {
      toast.success("Đơn đã có thể gom chuyến");
      invalidate();
    },
    onError: (err: Error) =>
      toast.error(err instanceof ApiError ? err.message : "Có lỗi xảy ra"),
  });

  function toggle(id: string) {
    setSelected((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  }

  const canSubmit =
    selectedOrders.length > 0 &&
    (tripChoice !== "new" || code.trim().length > 0) &&
    !consolidateMutation.isPending;

  if (isLoading) {
    return <Skeleton className="h-60 w-full" />;
  }

  return (
    <div className="lg:grid lg:grid-cols-[minmax(0,1fr)_340px] lg:items-start lg:gap-6">
      {/* Selectable orders + separate section */}
      <div className="space-y-4">
        <Card>
          <CardHeader>
            <CardTitle>Đơn chờ gom</CardTitle>
            <CardDescription>
              Chọn nhiều đơn (khác khách) để gom vào một chuyến hàng.
            </CardDescription>
          </CardHeader>
          <CardContent className="divide-y divide-border">
            {eligible.length === 0 ? (
              <p className="py-6 text-center text-sm text-muted-foreground">
                Không có đơn phù hợp để gom.
              </p>
            ) : (
              eligible.map((o) => {
                const checked = selected.has(o.id);
                return (
                  <label
                    key={o.id}
                    className="flex cursor-pointer items-center gap-3 py-3 first:pt-0 last:pb-0 has-[:checked]:bg-muted/40 sm:px-1"
                  >
                    <input
                      type="checkbox"
                      checked={checked}
                      onChange={() => toggle(o.id)}
                      className="size-4 rounded border-input accent-primary"
                    />
                    <div className="min-w-0 flex-1">
                      <div className="flex items-center justify-between gap-2">
                        <p className="truncate font-medium">{o.customer_name}</p>
                        <span className="shrink-0 font-semibold tabular-nums">
                          {formatMoney(o.total_amount)}
                        </span>
                      </div>
                      <p className="truncate text-xs text-muted-foreground">
                        {o.tracking_code} · {o.lines.length} dòng ·{" "}
                        {formatDate(o.created_at)}
                      </p>
                    </div>
                  </label>
                );
              })
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Đơn giao riêng</CardTitle>
            <CardDescription>
              Khách yêu cầu không gom — tách khỏi chuyến gom chung.
            </CardDescription>
          </CardHeader>
          <CardContent className="divide-y divide-border">
            {separateOrders.length === 0 ? (
              <p className="py-2 text-sm text-muted-foreground">
                Không có đơn giao riêng.
              </p>
            ) : (
              separateOrders.map((o) => (
                <div
                  key={o.id}
                  className="flex items-center justify-between gap-3 py-3 first:pt-0 last:pb-0"
                >
                  <div className="min-w-0">
                    <p className="truncate font-medium">{o.customer_name}</p>
                    <p className="truncate text-xs text-muted-foreground">
                      {o.tracking_code} · {formatMoney(o.total_amount)}
                    </p>
                  </div>
                  <Button
                    size="sm"
                    variant="ghost"
                    disabled={reincludeMutation.isPending}
                    onClick={() => reincludeMutation.mutate(o.id)}
                  >
                    Cho gom lại
                  </Button>
                </div>
              ))
            )}
          </CardContent>
        </Card>
      </div>

      {/* Sticky trip panel */}
      <div className="mt-4 lg:sticky lg:top-20 lg:mt-0">
        <Card>
          <CardHeader>
            <CardTitle>Chuyến hàng</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="space-y-1.5">
              <Label htmlFor="trip-choice">Gom vào chuyến</Label>
              <select
                id="trip-choice"
                value={tripChoice}
                onChange={(event) => setTripChoice(event.target.value)}
                className="h-9 w-full rounded-md border border-input bg-transparent px-2 text-sm"
              >
                <option value="new">+ Tạo chuyến mới</option>
                {planningTrips.map((t) => (
                  <option key={t.id} value={t.id}>
                    {t.code} — {t.name}
                  </option>
                ))}
              </select>
            </div>

            {tripChoice === "new" && (
              <div className="space-y-2">
                <Input
                  value={code}
                  onChange={(event) => setCode(event.target.value)}
                  placeholder="Mã chuyến (vd JP-2026-07)"
                  aria-label="Mã chuyến"
                />
                <Input
                  value={name}
                  onChange={(event) => setName(event.target.value)}
                  placeholder="Tên chuyến (vd Chuyến Nhật tháng 7)"
                  aria-label="Tên chuyến"
                />
                <Input
                  value={shopper}
                  onChange={(event) => setShopper(event.target.value)}
                  placeholder="Người xách tay (tùy chọn)"
                  aria-label="Người xách tay"
                />
              </div>
            )}

            <Separator />

            {selectedOrders.length === 0 ? (
              <p className="text-sm text-muted-foreground">
                Chọn các đơn bên trái để xem danh sách cần mua gộp.
              </p>
            ) : (
              <>
                <div className="flex items-center justify-between text-sm">
                  <span className="text-muted-foreground">Số đơn</span>
                  <span className="font-medium tabular-nums">
                    {selectedOrders.length}
                  </span>
                </div>
                <div className="text-sm">
                  <span className="text-muted-foreground">Khách: </span>
                  <span className="font-medium">{customers.join(", ")}</span>
                </div>
                <Separator />
                <ul className="space-y-1.5 text-sm">
                  {combined.map((line) => (
                    <li
                      key={line.product_id}
                      className="flex items-center justify-between gap-2"
                    >
                      <span className="truncate">{line.product_name}</span>
                      <span className="shrink-0 tabular-nums text-muted-foreground">
                        × {line.quantity} · {formatMoney(line.total)}
                      </span>
                    </li>
                  ))}
                </ul>
                <Separator />
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium">Tổng tiền</span>
                  <span className="font-semibold tabular-nums">
                    {formatMoney(grandTotal)}
                  </span>
                </div>
              </>
            )}

            <Button
              className="w-full"
              disabled={!canSubmit}
              onClick={() => consolidateMutation.mutate()}
            >
              {consolidateMutation.isPending
                ? "Đang gom…"
                : `Gom vào chuyến (${selectedOrders.length})`}
            </Button>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

"use client";

import { useState } from "react";
import Link from "next/link";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { ArrowLeft, Check } from "lucide-react";

import { ApiError } from "@/lib/api";
import {
  ORDER_STATUS_LABELS,
  STATUS_VARIANT,
  combineLines,
  formatDate,
  formatMoney,
  recordLinePurchase,
  toNumber,
  type Order,
  type OrderLine,
} from "@/lib/orders";
import {
  NEXT_TRIP_STATUS,
  TRIP_STATUS_LABELS,
  TRIP_STATUS_VARIANT,
  changeTripStatus,
  detachOrder,
  getTrip,
  listTripOrders,
  type TripStatus,
} from "@/lib/trips";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Separator } from "@/components/ui/separator";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

/** Trip detail: info + status flow + buying checklist + orders. */
export function TripDetail({ tripId }: { tripId: string }) {
  const queryClient = useQueryClient();

  const tripQuery = useQuery({
    queryKey: ["trips", tripId],
    queryFn: () => getTrip(tripId),
  });
  const ordersQuery = useQuery({
    queryKey: ["trips", tripId, "orders"],
    queryFn: () => listTripOrders(tripId),
  });

  const invalidate = () => {
    queryClient.invalidateQueries({ queryKey: ["trips"] });
    queryClient.invalidateQueries({ queryKey: ["orders"] });
  };

  const statusMutation = useMutation({
    mutationFn: (status: TripStatus) => changeTripStatus(tripId, status),
    onSuccess: (trip) => {
      toast.success(`Chuyến ${trip.code}: ${TRIP_STATUS_LABELS[trip.status]}`);
      invalidate();
    },
    onError: (err: Error) =>
      toast.error(err instanceof ApiError ? err.message : "Có lỗi xảy ra"),
  });

  const detachMutation = useMutation({
    mutationFn: (orderId: string) => detachOrder(tripId, orderId),
    onSuccess: () => {
      toast.success("Đã gỡ đơn khỏi chuyến");
      invalidate();
    },
    onError: (err: Error) =>
      toast.error(err instanceof ApiError ? err.message : "Có lỗi xảy ra"),
  });

  if (tripQuery.isLoading || ordersQuery.isLoading) {
    return (
      <div className="space-y-3">
        <Skeleton className="h-24 w-full" />
        <Skeleton className="h-60 w-full" />
      </div>
    );
  }
  if (tripQuery.isError || !tripQuery.data) {
    return (
      <p className="py-10 text-center text-sm text-destructive">
        Không tải được chuyến hàng.
      </p>
    );
  }

  const trip = tripQuery.data;
  const orders = ordersQuery.data ?? [];
  const manifest = combineLines(orders);
  const grandTotal = orders.reduce(
    (sum, o) => sum + toNumber(o.total_amount),
    0,
  );
  const next = NEXT_TRIP_STATUS[trip.status];

  return (
    <div className="space-y-4">
      <Button asChild variant="ghost" size="sm" className="gap-1.5 -ml-2">
        <Link href="/trips">
          <ArrowLeft aria-hidden />
          Chuyến hàng
        </Link>
      </Button>

      {/* Trip header */}
      <Card>
        <CardContent className="flex flex-wrap items-center justify-between gap-3 py-4">
          <div className="min-w-0">
            <div className="flex flex-wrap items-center gap-2">
              <h1 className="text-lg font-semibold">{trip.name}</h1>
              <Badge variant={TRIP_STATUS_VARIANT[trip.status]}>
                {TRIP_STATUS_LABELS[trip.status]}
              </Badge>
            </div>
            <p className="mt-0.5 text-sm text-muted-foreground">
              {trip.code}
              {trip.shopper_name ? ` · Người xách tay: ${trip.shopper_name}` : ""}
              {trip.departure_date ? ` · Đi ${formatDate(trip.departure_date)}` : ""}
              {trip.arrival_date ? ` · Về ${formatDate(trip.arrival_date)}` : ""}
            </p>
          </div>
          <div className="flex gap-2">
            {trip.status === "planning" && (
              <Button
                size="sm"
                variant="destructive"
                disabled={statusMutation.isPending}
                onClick={() => statusMutation.mutate("cancelled")}
              >
                Hủy chuyến
              </Button>
            )}
            {next && (
              <Button
                size="sm"
                disabled={statusMutation.isPending}
                onClick={() => statusMutation.mutate(next)}
              >
                → {TRIP_STATUS_LABELS[next]}
              </Button>
            )}
          </div>
        </CardContent>
      </Card>

      <div className="lg:grid lg:grid-cols-[minmax(0,1fr)_340px] lg:items-start lg:gap-6">
        {/* Orders in the trip */}
        <div className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Đơn trong chuyến ({orders.length})</CardTitle>
              {trip.status === "buying" && (
                <CardDescription>
                  Tick từng món đã mua và nhập giá mua thực tế — đơn tự chuyển
                  “Đã mua” khi mua đủ.
                </CardDescription>
              )}
            </CardHeader>
            <CardContent className="space-y-4">
              {orders.length === 0 ? (
                <p className="py-4 text-center text-sm text-muted-foreground">
                  Chưa có đơn nào.{" "}
                  <Link
                    href="/orders?tab=consolidate"
                    className="underline underline-offset-4"
                  >
                    Gom đơn
                  </Link>
                </p>
              ) : (
                orders.map((order) => (
                  <div
                    key={order.id}
                    className="rounded-lg border border-border p-3"
                  >
                    <div className="flex flex-wrap items-center justify-between gap-2">
                      <div className="min-w-0">
                        <p className="truncate font-medium">
                          {order.customer_name}{" "}
                          <span className="font-normal text-muted-foreground">
                            · {order.tracking_code}
                          </span>
                        </p>
                      </div>
                      <div className="flex items-center gap-2">
                        <Badge variant={STATUS_VARIANT[order.status]}>
                          {ORDER_STATUS_LABELS[order.status]}
                        </Badge>
                        {trip.status === "planning" && (
                          <Button
                            size="sm"
                            variant="ghost"
                            disabled={detachMutation.isPending}
                            onClick={() => detachMutation.mutate(order.id)}
                          >
                            Gỡ khỏi chuyến
                          </Button>
                        )}
                      </div>
                    </div>
                    <div className="mt-2 space-y-2">
                      {order.lines.map((line) => (
                        <PurchaseLine
                          key={line.id}
                          order={order}
                          line={line}
                          canRecord={order.status === "purchasing"}
                          onSaved={invalidate}
                        />
                      ))}
                    </div>
                  </div>
                ))
              )}
            </CardContent>
          </Card>
        </div>

        {/* Manifest */}
        <div className="mt-4 lg:sticky lg:top-20 lg:mt-0">
          <Card>
            <CardHeader>
              <CardTitle>Danh sách cần mua</CardTitle>
              <CardDescription>
                Gộp theo món — gửi cho người xách tay.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              {manifest.length === 0 ? (
                <p className="text-sm text-muted-foreground">Chưa có món nào.</p>
              ) : (
                <>
                  <ul className="space-y-1.5 text-sm">
                    {manifest.map((line) => (
                      <li
                        key={line.product_id}
                        className="flex items-center justify-between gap-2"
                      >
                        <span className="truncate">{line.product_name}</span>
                        <span className="shrink-0 tabular-nums text-muted-foreground">
                          × {line.quantity}
                        </span>
                      </li>
                    ))}
                  </ul>
                  <Separator />
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium">Tổng tiền bán</span>
                    <span className="font-semibold tabular-nums">
                      {formatMoney(grandTotal)}
                    </span>
                  </div>
                </>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}

/** One order line with purchase-recording controls (qty bought + actual cost). */
function PurchaseLine({
  order,
  line,
  canRecord,
  onSaved,
}: {
  order: Order;
  line: OrderLine;
  canRecord: boolean;
  onSaved: () => void;
}) {
  const [qty, setQty] = useState(
    line.purchased_quantity > 0 ? String(line.purchased_quantity) : "",
  );
  const [cost, setCost] = useState(line.actual_unit_cost ?? "");

  const mutation = useMutation({
    mutationFn: () =>
      recordLinePurchase(order.id, line.id, {
        purchased_quantity: Number(qty),
        actual_unit_cost: cost !== "" ? String(cost) : null,
      }),
    onSuccess: (updated) => {
      toast.success(
        updated.status === "purchased"
          ? `Đơn ${updated.tracking_code} đã mua đủ!`
          : "Đã ghi nhận mua hàng",
      );
      onSaved();
    },
    onError: (err: Error) =>
      toast.error(err instanceof ApiError ? err.message : "Có lỗi xảy ra"),
  });

  const done = line.purchased_quantity >= line.quantity;

  return (
    <div className="flex flex-wrap items-center gap-2 text-sm">
      <span className="min-w-0 flex-1 truncate">
        {done && (
          <Check className="mr-1 inline size-3.5 text-green-600" aria-hidden />
        )}
        {line.product_name}
        <span className="text-muted-foreground"> × {line.quantity}</span>
        <span className="ml-1 tabular-nums text-muted-foreground">
          · bán {formatMoney(line.unit_price)}
        </span>
      </span>
      {canRecord ? (
        <span className="flex items-center gap-1.5">
          <Input
            type="number"
            min={0}
            max={line.quantity}
            value={qty}
            onChange={(event) => setQty(event.target.value)}
            placeholder={`0/${line.quantity}`}
            aria-label="Số lượng đã mua"
            className="h-8 w-20"
          />
          <Input
            type="number"
            min={0}
            step={1000}
            value={cost}
            onChange={(event) => setCost(event.target.value)}
            placeholder="Giá mua"
            aria-label="Giá mua thực tế"
            className="h-8 w-28"
          />
          <Button
            size="sm"
            variant="secondary"
            className="h-8"
            disabled={mutation.isPending || qty === ""}
            onClick={() => mutation.mutate()}
          >
            Lưu
          </Button>
        </span>
      ) : (
        line.purchased_quantity > 0 && (
          <span className="tabular-nums text-muted-foreground">
            đã mua {line.purchased_quantity}/{line.quantity}
            {line.actual_unit_cost
              ? ` · ${formatMoney(line.actual_unit_cost)}`
              : ""}
          </span>
        )
      )}
    </div>
  );
}

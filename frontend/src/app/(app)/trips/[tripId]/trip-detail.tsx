"use client";

import { useState } from "react";
import Link from "next/link";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { AlertTriangle, ArrowLeft, Check } from "lucide-react";

import { cn } from "@/lib/utils";
import { ApiError } from "@/lib/api";
import { getProfitReport } from "@/lib/reports";
import {
  STATUS_VARIANT,
  combineLines,
  formatDate,
  formatMoney,
  orderStatusLabel,
  recordLinePurchase,
  toNumber,
  type Order,
  type OrderLine,
} from "@/lib/orders";
import {
  NEXT_TRIP_STATUS,
  TRIP_STATUS_VARIANT,
  changeTripStatus,
  detachOrder,
  getTrip,
  listTripOrders,
  tripStatusLabel,
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
import { useI18n } from "@/components/i18n-provider";

/** Trip detail: info + status flow + buying checklist + orders. */
export function TripDetail({ tripId }: { tripId: string }) {
  const { t } = useI18n();
  const queryClient = useQueryClient();

  const tripQuery = useQuery({
    queryKey: ["trips", tripId],
    queryFn: () => getTrip(tripId),
  });
  const ordersQuery = useQuery({
    queryKey: ["trips", tripId, "orders"],
    queryFn: () => listTripOrders(tripId),
  });
  const pnlQuery = useQuery({
    queryKey: ["reports", "profit", { tripId }],
    queryFn: () => getProfitReport({ trip_id: tripId }),
  });

  const invalidate = () => {
    queryClient.invalidateQueries({ queryKey: ["trips"] });
    queryClient.invalidateQueries({ queryKey: ["orders"] });
  };

  const statusMutation = useMutation({
    mutationFn: (status: TripStatus) => changeTripStatus(tripId, status),
    onSuccess: (trip) => {
      toast.success(
        t("trips.detail.toastStatus", {
          code: trip.code,
          status: tripStatusLabel(trip.status),
        }),
      );
      invalidate();
    },
    onError: (err: Error) =>
      toast.error(err instanceof ApiError ? err.message : t("common.errorOccurred")),
  });

  const detachMutation = useMutation({
    mutationFn: (orderId: string) => detachOrder(tripId, orderId),
    onSuccess: () => {
      toast.success(t("trips.detail.detachOk"));
      invalidate();
    },
    onError: (err: Error) =>
      toast.error(err instanceof ApiError ? err.message : t("common.errorOccurred")),
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
        {t("trips.detail.error")}
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
          {t("trips.detail.back")}
        </Link>
      </Button>

      {/* Trip header */}
      <Card>
        <CardContent className="flex flex-wrap items-center justify-between gap-3 py-4">
          <div className="min-w-0">
            <div className="flex flex-wrap items-center gap-2">
              <h1 className="text-lg font-semibold">{trip.name}</h1>
              <Badge variant={TRIP_STATUS_VARIANT[trip.status]}>
                {tripStatusLabel(trip.status)}
              </Badge>
            </div>
            <p className="mt-0.5 text-sm text-muted-foreground">
              {trip.code}
              {trip.shopper_name
                ? ` · ${t("trips.detail.shopper")}${trip.shopper_name}`
                : ""}
              {trip.departure_date
                ? ` · ${t("trips.detail.departure")}${formatDate(trip.departure_date)}`
                : ""}
              {trip.arrival_date
                ? ` · ${t("trips.detail.arrival")}${formatDate(trip.arrival_date)}`
                : ""}
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
                {t("trips.detail.cancel")}
              </Button>
            )}
            {next && (
              <Button
                size="sm"
                disabled={statusMutation.isPending}
                onClick={() => statusMutation.mutate(next)}
              >
                {t("trips.detail.advance", { status: tripStatusLabel(next) })}
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
              <CardTitle>
                {t("trips.detail.ordersTitle", { count: orders.length })}
              </CardTitle>
              {trip.status === "buying" && (
                <CardDescription>
                  {t("trips.detail.ordersDesc", {
                    status: t("statuses.order.purchased"),
                  })}
                </CardDescription>
              )}
            </CardHeader>
            <CardContent className="space-y-4">
              {orders.length === 0 ? (
                <p className="py-4 text-center text-sm text-muted-foreground">
                  {t("trips.detail.empty")}
                  <Link
                    href="/orders?tab=consolidate"
                    className="underline underline-offset-4"
                  >
                    {t("trips.detail.emptyCta")}
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
                          {orderStatusLabel(order.status)}
                        </Badge>
                        {trip.status === "planning" && (
                          <Button
                            size="sm"
                            variant="ghost"
                            disabled={detachMutation.isPending}
                            onClick={() => detachMutation.mutate(order.id)}
                          >
                            {t("trips.detail.detach")}
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

        {/* Manifest + P&L */}
        <div className="mt-4 space-y-4 lg:sticky lg:top-20 lg:mt-0">
          {pnlQuery.data && pnlQuery.data.orders_count > 0 && (
            <Card>
              <CardHeader>
                <CardTitle>{t("trips.detail.pnlTitle")}</CardTitle>
              </CardHeader>
              <CardContent className="space-y-2 text-sm">
                <div className="flex items-center justify-between">
                  <span className="text-muted-foreground">
                    {t("trips.detail.pnlRevenue")}
                  </span>
                  <span className="font-medium tabular-nums">
                    {formatMoney(pnlQuery.data.total_revenue)}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-muted-foreground">
                    {t("trips.detail.pnlCost")}
                  </span>
                  <span className="font-medium tabular-nums">
                    {formatMoney(pnlQuery.data.total_cost)}
                  </span>
                </div>
                <Separator />
                <div className="flex items-center justify-between">
                  <span className="font-medium">{t("trips.detail.pnlProfit")}</span>
                  <span
                    className={cn(
                      "font-semibold tabular-nums",
                      toNumber(pnlQuery.data.total_profit) >= 0
                        ? "text-green-600"
                        : "text-destructive",
                    )}
                  >
                    {formatMoney(pnlQuery.data.total_profit)}
                  </span>
                </div>
                {toNumber(pnlQuery.data.total_revenue) > 0 && (
                  <div className="flex items-center justify-between">
                    <span className="text-muted-foreground">
                      {t("trips.detail.pnlMargin")}
                    </span>
                    <span className="tabular-nums text-muted-foreground">
                      {(
                        ((toNumber(pnlQuery.data.total_revenue) -
                          toNumber(pnlQuery.data.total_cost)) /
                          toNumber(pnlQuery.data.total_revenue)) *
                        100
                      ).toFixed(0)}
                      %
                    </span>
                  </div>
                )}
                {pnlQuery.data.orders_with_incomplete_cost > 0 && (
                  <p className="flex items-center gap-1.5 rounded-md bg-amber-500/10 px-2 py-1.5 text-xs text-amber-700">
                    <AlertTriangle className="size-3.5 shrink-0" aria-hidden />
                    {t("trips.detail.pnlIncomplete", {
                      count: pnlQuery.data.orders_with_incomplete_cost,
                    })}
                  </p>
                )}
              </CardContent>
            </Card>
          )}

          <Card>
            <CardHeader>
              <CardTitle>{t("trips.detail.manifestTitle")}</CardTitle>
              <CardDescription>
                {t("trips.detail.manifestDesc")}
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              {manifest.length === 0 ? (
                <p className="text-sm text-muted-foreground">
                  {t("trips.detail.manifestEmpty")}
                </p>
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
                    <span className="text-sm font-medium">
                      {t("trips.detail.salesTotal")}
                    </span>
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
  const { t } = useI18n();
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
          ? t("trips.detail.purchaseToastFull", { code: updated.tracking_code })
          : t("trips.detail.purchaseToast"),
      );
      onSaved();
    },
    onError: (err: Error) =>
      toast.error(err instanceof ApiError ? err.message : t("common.errorOccurred")),
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
          · {t("trips.detail.unitPrice", { money: formatMoney(line.unit_price) })}
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
            aria-label={t("trips.detail.boughtAria")}
            className="h-8 w-20"
          />
          <Input
            type="number"
            min={0}
            step={1000}
            value={cost}
            onChange={(event) => setCost(event.target.value)}
            placeholder={t("trips.detail.costPh")}
            aria-label={t("trips.detail.costAria")}
            className="h-8 w-28"
          />
          <Button
            size="sm"
            variant="secondary"
            className="h-8"
            disabled={mutation.isPending || qty === ""}
            onClick={() => mutation.mutate()}
          >
            {t("trips.detail.save")}
          </Button>
        </span>
      ) : (
        line.purchased_quantity > 0 && (
          <span className="tabular-nums text-muted-foreground">
            {t("trips.detail.boughtCaption", {
              bought: line.purchased_quantity,
              qty: line.quantity,
            })}
            {line.actual_unit_cost
              ? ` · ${formatMoney(line.actual_unit_cost)}`
              : ""}
          </span>
        )
      )}
    </div>
  );
}

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
import { useI18n } from "@/components/i18n-provider";

/**
 * Consolidation: pick confirmed/pending orders (not separate, not already in a
 * trip) and attach them to a buying trip — either an existing PLANNING trip
 * or a new one created inline.
 */
export function ConsolidateOrders() {
  const { t } = useI18n();
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
        const existing = planningTrips.find((item) => item.id === tripChoice);
        if (!existing) throw new Error(t("orders.consolidate.notPlanning"));
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
        t("orders.consolidate.toastConsolidated", {
          count: selectedOrders.length,
          code: trip.code,
        }),
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
      toast.success(t("orders.consolidate.toastReinclude"));
      invalidate();
    },
    onError: (err: Error) =>
      toast.error(err instanceof ApiError ? err.message : t("common.errorOccurred")),
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
            <CardTitle>{t("orders.consolidate.titleWaiting")}</CardTitle>
            <CardDescription>
              {t("orders.consolidate.descWaiting")}
            </CardDescription>
          </CardHeader>
          <CardContent className="divide-y divide-border">
            {eligible.length === 0 ? (
              <p className="py-6 text-center text-sm text-muted-foreground">
                {t("orders.consolidate.emptyWaiting")}
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
                        {o.tracking_code} ·{" "}
                        {t("orders.consolidate.lineCount", {
                          count: o.lines.length,
                        })}{" "}
                        · {formatDate(o.created_at)}
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
            <CardTitle>{t("orders.consolidate.titleSeparate")}</CardTitle>
            <CardDescription>
              {t("orders.consolidate.descSeparate")}
            </CardDescription>
          </CardHeader>
          <CardContent className="divide-y divide-border">
            {separateOrders.length === 0 ? (
              <p className="py-2 text-sm text-muted-foreground">
                {t("orders.consolidate.emptySeparate")}
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
                    {t("orders.consolidate.reinclude")}
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
            <CardTitle>{t("orders.consolidate.titleTrip")}</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="space-y-1.5">
              <Label htmlFor="trip-choice">
                {t("orders.consolidate.tripSelect")}
              </Label>
              <select
                id="trip-choice"
                value={tripChoice}
                onChange={(event) => setTripChoice(event.target.value)}
                className="h-9 w-full rounded-md border border-input bg-transparent px-2 text-sm"
              >
                <option value="new">{t("orders.consolidate.newTrip")}</option>
                {planningTrips.map((trip) => (
                  <option key={trip.id} value={trip.id}>
                    {trip.code} — {trip.name}
                  </option>
                ))}
              </select>
            </div>

            {tripChoice === "new" && (
              <div className="space-y-2">
                <Input
                  value={code}
                  onChange={(event) => setCode(event.target.value)}
                  placeholder={t("orders.consolidate.codePh")}
                  aria-label={t("orders.consolidate.codeAria")}
                />
                <Input
                  value={name}
                  onChange={(event) => setName(event.target.value)}
                  placeholder={t("orders.consolidate.namePh")}
                  aria-label={t("orders.consolidate.nameAria")}
                />
                <Input
                  value={shopper}
                  onChange={(event) => setShopper(event.target.value)}
                  placeholder={t("orders.consolidate.shopperPh")}
                  aria-label={t("orders.consolidate.shopperAria")}
                />
              </div>
            )}

            <Separator />

            {selectedOrders.length === 0 ? (
              <p className="text-sm text-muted-foreground">
                {t("orders.consolidate.selectHint")}
              </p>
            ) : (
              <>
                <div className="flex items-center justify-between text-sm">
                  <span className="text-muted-foreground">
                    {t("orders.consolidate.orderCount")}
                  </span>
                  <span className="font-medium tabular-nums">
                    {selectedOrders.length}
                  </span>
                </div>
                <div className="text-sm">
                  <span className="text-muted-foreground">
                    {t("orders.consolidate.customerPrefix")}
                  </span>
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
                  <span className="text-sm font-medium">
                    {t("orders.money.total")}
                  </span>
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
                ? t("orders.consolidate.consolidatePending")
                : t("orders.consolidate.consolidateBtn", {
                    count: selectedOrders.length,
                  })}
            </Button>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

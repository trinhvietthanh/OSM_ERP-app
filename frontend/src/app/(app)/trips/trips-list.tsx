"use client";

import Link from "next/link";
import { useQuery } from "@tanstack/react-query";
import { Plane } from "lucide-react";

import {
  TRIP_STATUS_VARIANT,
  listTrips,
  tripStatusLabel,
} from "@/lib/trips";
import { formatDate } from "@/lib/orders";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { useI18n } from "@/components/i18n-provider";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

/** Trip list: one row per buying trip, linking to the detail page. */
export function TripsList() {
  const { t } = useI18n();
  const {
    data: trips = [],
    isLoading,
    isError,
    error,
  } = useQuery({ queryKey: ["trips"], queryFn: () => listTrips() });

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
        {t("trips.listError", { message: (error as Error).message })}
      </p>
    );
  }

  if (trips.length === 0) {
    return (
      <div className="flex flex-col items-center gap-3 py-16 text-center">
        <Plane className="size-8 text-muted-foreground" aria-hidden />
        <p className="text-sm text-muted-foreground">{t("trips.empty")}</p>
        <Button asChild size="sm">
          <Link href="/orders?tab=consolidate">{t("trips.emptyCta")}</Link>
        </Button>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Desktop table */}
      <Card className="hidden py-0 lg:block">
        <Table>
          <TableHeader>
            <TableRow className="hover:bg-transparent">
              <TableHead className="w-36">{t("trips.col.code")}</TableHead>
              <TableHead>{t("trips.col.name")}</TableHead>
              <TableHead className="w-44">{t("trips.col.shopper")}</TableHead>
              <TableHead className="w-32">{t("trips.col.departure")}</TableHead>
              <TableHead className="w-32">{t("trips.col.arrival")}</TableHead>
              <TableHead className="w-40">{t("trips.col.status")}</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {trips.map((trip) => (
              <TableRow key={trip.id} className="cursor-pointer">
                <TableCell className="p-0" colSpan={6}>
                  <Link
                    href={`/trips/${trip.id}`}
                    className="grid grid-cols-[9rem_minmax(0,1fr)_11rem_8rem_8rem_10rem] items-center px-2"
                  >
                    <span className="p-2 font-medium tabular-nums">
                      {trip.code}
                    </span>
                    <span className="truncate p-2">{trip.name}</span>
                    <span className="truncate p-2 text-muted-foreground">
                      {trip.shopper_name || "—"}
                    </span>
                    <span className="p-2 text-muted-foreground">
                      {trip.departure_date ? formatDate(trip.departure_date) : "—"}
                    </span>
                    <span className="p-2 text-muted-foreground">
                      {trip.arrival_date ? formatDate(trip.arrival_date) : "—"}
                    </span>
                    <span className="p-2">
                      <Badge variant={TRIP_STATUS_VARIANT[trip.status]}>
                        {tripStatusLabel(trip.status)}
                      </Badge>
                    </span>
                  </Link>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </Card>

      {/* Mobile cards */}
      <div className="grid gap-3 lg:hidden">
        {trips.map((trip) => (
          <Card key={trip.id} className="py-0">
            <CardContent className="px-4 py-3">
              <Link
                href={`/trips/${trip.id}`}
                className="flex items-center justify-between gap-3"
              >
                <div className="min-w-0">
                  <p className="truncate font-medium">{trip.name}</p>
                  <p className="text-xs text-muted-foreground">
                    {trip.code}
                    {trip.shopper_name ? ` · ${trip.shopper_name}` : ""}
                  </p>
                </div>
                <Badge variant={TRIP_STATUS_VARIANT[trip.status]}>
                  {tripStatusLabel(trip.status)}
                </Badge>
              </Link>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}

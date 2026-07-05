"use client";

import Link from "next/link";
import { useQuery } from "@tanstack/react-query";
import { Plane } from "lucide-react";

import {
  TRIP_STATUS_LABELS,
  TRIP_STATUS_VARIANT,
  listTrips,
} from "@/lib/trips";
import { formatDate } from "@/lib/orders";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
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
        Không tải được danh sách chuyến: {(error as Error).message}
      </p>
    );
  }

  if (trips.length === 0) {
    return (
      <div className="flex flex-col items-center gap-3 py-16 text-center">
        <Plane className="size-8 text-muted-foreground" aria-hidden />
        <p className="text-sm text-muted-foreground">
          Chưa có chuyến hàng nào. Gom các đơn đã chốt để tạo chuyến đầu tiên.
        </p>
        <Button asChild size="sm">
          <Link href="/orders?tab=consolidate">Gom đơn ngay</Link>
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
              <TableHead className="w-36">Mã chuyến</TableHead>
              <TableHead>Tên</TableHead>
              <TableHead className="w-44">Người xách tay</TableHead>
              <TableHead className="w-32">Ngày đi</TableHead>
              <TableHead className="w-32">Ngày về</TableHead>
              <TableHead className="w-40">Trạng thái</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {trips.map((t) => (
              <TableRow key={t.id} className="cursor-pointer">
                <TableCell className="p-0" colSpan={6}>
                  <Link
                    href={`/trips/${t.id}`}
                    className="grid grid-cols-[9rem_minmax(0,1fr)_11rem_8rem_8rem_10rem] items-center px-2"
                  >
                    <span className="p-2 font-medium tabular-nums">
                      {t.code}
                    </span>
                    <span className="truncate p-2">{t.name}</span>
                    <span className="truncate p-2 text-muted-foreground">
                      {t.shopper_name || "—"}
                    </span>
                    <span className="p-2 text-muted-foreground">
                      {t.departure_date ? formatDate(t.departure_date) : "—"}
                    </span>
                    <span className="p-2 text-muted-foreground">
                      {t.arrival_date ? formatDate(t.arrival_date) : "—"}
                    </span>
                    <span className="p-2">
                      <Badge variant={TRIP_STATUS_VARIANT[t.status]}>
                        {TRIP_STATUS_LABELS[t.status]}
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
        {trips.map((t) => (
          <Card key={t.id} className="py-0">
            <CardContent className="px-4 py-3">
              <Link
                href={`/trips/${t.id}`}
                className="flex items-center justify-between gap-3"
              >
                <div className="min-w-0">
                  <p className="truncate font-medium">{t.name}</p>
                  <p className="text-xs text-muted-foreground">
                    {t.code}
                    {t.shopper_name ? ` · ${t.shopper_name}` : ""}
                  </p>
                </div>
                <Badge variant={TRIP_STATUS_VARIANT[t.status]}>
                  {TRIP_STATUS_LABELS[t.status]}
                </Badge>
              </Link>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}

import * as React from "react";

import { cn } from "@/lib/utils";
import {
  ORDER_STATUS_LABELS,
  STATUS_STYLE,
  type OrderStatus,
} from "@/lib/orders";

/**
 * Colored status chip — each `OrderStatus` gets a distinct hue (amber, violet,
 * sky, …) plus a leading dot, so the order list is scannable at a glance.
 * Coloring lives in `STATUS_STYLE` (lib/orders.ts) so it stays next to the
 * labels; this component just renders it.
 */
export function StatusBadge({
  status,
  size = "md",
  className,
}: {
  status: OrderStatus;
  size?: "sm" | "md";
  className?: string;
}) {
  const style = STATUS_STYLE[status];
  return (
    <span
      data-slot="status-badge"
      className={cn(
        "inline-flex w-fit shrink-0 items-center gap-1.5 rounded-full font-medium whitespace-nowrap",
        size === "sm" ? "px-2 py-0.5 text-[0.7rem]" : "px-2.5 py-1 text-xs",
        style.chip,
        className,
      )}
    >
      <span
        aria-hidden
        className={cn("size-1.5 rounded-full", style.dot)}
      />
      {ORDER_STATUS_LABELS[status]}
    </span>
  );
}

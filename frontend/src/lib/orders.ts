/**
 * Order domain: API types (mirroring the backend OrderRead), fetchers and
 * pure helpers. Money values arrive as decimal strings ("550000.00") —
 * parse with `toNumber` for math/display.
 */

import { apiFetch } from "@/lib/api";
import { dictionaries } from "@/lib/i18n/dictionaries";
import { LOCALE_BCP47, getActiveLocale, type Locale } from "@/lib/i18n/config";

export type OrderStatus =
  | "pending"
  | "confirmed"
  | "purchasing"
  | "purchased"
  | "arrived"
  | "delivered"
  | "cancelled";

export type ReceiptMethod = "cash" | "bank_transfer" | "other";

export type OrderLine = {
  id: string;
  product_id: string;
  product_code: string;
  product_name: string;
  quantity: number;
  unit_price: string;
  unit_deposit: string;
  line_total: string;
  purchased_quantity: number;
  actual_unit_cost: string | null;
  purchased_at: string | null;
};

export type ReceiptKind = "collection" | "refund";

export type Receipt = {
  id: string;
  amount: string;
  method: ReceiptMethod;
  kind: ReceiptKind;
  received_at: string;
  note: string;
};

export type Order = {
  id: string;
  organization_id: string;
  customer_id: string;
  customer_name: string;
  tracking_code: string;
  status: OrderStatus;
  is_separate: boolean;
  trip_id: string | null;
  note: string;
  lines: OrderLine[];
  receipts: Receipt[];
  total_amount: string;
  deposit_due: string;
  total_collected: string;
  total_refunded: string;
  remaining: string;
  created_at: string;
  updated_at: string;
};

export type OrderLineInput = {
  product_id: string;
  quantity: number;
  unit_price: string;
  unit_deposit?: string;
};

export type CreateReceiptInput = {
  amount: string;
  method?: ReceiptMethod;
  kind?: ReceiptKind;
  note?: string;
};

export type CreateOrderInput = {
  customer_id: string;
  lines: OrderLineInput[];
  is_separate?: boolean;
  note?: string;
  initial_receipt?: CreateReceiptInput | null;
};

export type OrderFilters = {
  status?: OrderStatus;
  customer_id?: string;
  trip_id?: string;
  unassigned?: boolean;
};

/* --------------------------------- fetchers -------------------------------- */

export function listOrders(filters: OrderFilters = {}): Promise<Order[]> {
  const params = new URLSearchParams();
  if (filters.status) params.set("status", filters.status);
  if (filters.customer_id) params.set("customer_id", filters.customer_id);
  if (filters.trip_id) params.set("trip_id", filters.trip_id);
  if (filters.unassigned) params.set("unassigned", "true");
  const qs = params.toString();
  return apiFetch<Order[]>(`/orders${qs ? `?${qs}` : ""}`);
}

export function getOrder(id: string): Promise<Order> {
  return apiFetch<Order>(`/orders/${id}`);
}

export function createOrder(input: CreateOrderInput): Promise<Order> {
  return apiFetch<Order>("/orders", {
    method: "POST",
    body: JSON.stringify(input),
  });
}

export function updateOrder(
  id: string,
  patch: { note?: string; is_separate?: boolean; lines?: OrderLineInput[] },
): Promise<Order> {
  return apiFetch<Order>(`/orders/${id}`, {
    method: "PATCH",
    body: JSON.stringify(patch),
  });
}

export function changeOrderStatus(
  id: string,
  status: OrderStatus,
): Promise<Order> {
  return apiFetch<Order>(`/orders/${id}/status`, {
    method: "POST",
    body: JSON.stringify({ status }),
  });
}

export function addReceipt(
  id: string,
  input: CreateReceiptInput,
): Promise<Order> {
  return apiFetch<Order>(`/orders/${id}/receipts`, {
    method: "POST",
    body: JSON.stringify(input),
  });
}

export function deleteReceipt(id: string, receiptId: string): Promise<void> {
  return apiFetch<void>(`/orders/${id}/receipts/${receiptId}`, {
    method: "DELETE",
  });
}

export type TrackingLine = { product_name: string; quantity: number };

export type Tracking = {
  tracking_code: string;
  status: OrderStatus;
  lines: TrackingLine[];
  total_amount: string;
  total_collected: string;
  remaining: string;
  created_at: string;
  updated_at: string;
};

/** Public lookup — no auth required; unknown/malformed codes → 404. */
export function trackOrder(code: string): Promise<Tracking> {
  return apiFetch<Tracking>(`/tracking/${encodeURIComponent(code.trim())}`);
}

export function recordLinePurchase(
  orderId: string,
  lineId: string,
  input: { purchased_quantity: number; actual_unit_cost?: string | null },
): Promise<Order> {
  return apiFetch<Order>(`/orders/${orderId}/lines/${lineId}/purchase`, {
    method: "POST",
    body: JSON.stringify(input),
  });
}

/* ------------------------------ labels / status ---------------------------- */

/** Localized label for an order status, in the active locale. */
export function orderStatusLabel(status: OrderStatus): string {
  return dictionaries[getActiveLocale()].statuses.order[status];
}

export const STATUS_VARIANT: Record<
  OrderStatus,
  "default" | "secondary" | "destructive" | "outline"
> = {
  pending: "outline",
  confirmed: "secondary",
  purchasing: "secondary",
  purchased: "default",
  arrived: "default",
  delivered: "default",
  cancelled: "destructive",
};

/**
 * Tailwind class strings per status — used by `StatusBadge`. Each status gets a
 * distinct hue so the order list is scannable at a glance; `bar` tints the left
 * accent strip on a mobile order card. Tailwind ships these colors by default.
 */
export const STATUS_STYLE: Record<
  OrderStatus,
  { chip: string; dot: string; bar: string }
> = {
  pending: {
    chip: "bg-amber-100 text-amber-700 dark:bg-amber-500/15 dark:text-amber-300",
    dot: "bg-amber-500",
    bar: "border-amber-400",
  },
  confirmed: {
    chip: "bg-violet-100 text-violet-700 dark:bg-violet-500/15 dark:text-violet-300",
    dot: "bg-violet-500",
    bar: "border-violet-400",
  },
  purchasing: {
    chip: "bg-sky-100 text-sky-700 dark:bg-sky-500/15 dark:text-sky-300",
    dot: "bg-sky-500",
    bar: "border-sky-400",
  },
  purchased: {
    chip: "bg-indigo-100 text-indigo-700 dark:bg-indigo-500/15 dark:text-indigo-300",
    dot: "bg-indigo-500",
    bar: "border-indigo-400",
  },
  arrived: {
    chip: "bg-teal-100 text-teal-700 dark:bg-teal-500/15 dark:text-teal-300",
    dot: "bg-teal-500",
    bar: "border-teal-400",
  },
  delivered: {
    chip: "bg-emerald-100 text-emerald-700 dark:bg-emerald-500/15 dark:text-emerald-300",
    dot: "bg-emerald-500",
    bar: "border-emerald-400",
  },
  cancelled: {
    chip: "bg-rose-100 text-rose-700 dark:bg-rose-500/15 dark:text-rose-300",
    dot: "bg-rose-500",
    bar: "border-rose-400",
  },
};

/** Next legal forward step for the quick-advance button (no cancel here). */
export const NEXT_ORDER_STATUS: Partial<Record<OrderStatus, OrderStatus>> = {
  pending: "confirmed",
  confirmed: "purchasing",
  purchasing: "purchased",
  purchased: "arrived",
  arrived: "delivered",
};

/** Statuses from which the order can still be cancelled. */
export const CANCELLABLE: ReadonlySet<OrderStatus> = new Set([
  "pending",
  "confirmed",
  "purchasing",
]);

/* --------------------------------- helpers --------------------------------- */

export const toNumber = (value: string | null | undefined) =>
  value == null ? 0 : Number(value);

// One formatter per locale (VND currency in both; grouping/symbol differ).
const moneyFormatters: Record<Locale, Intl.NumberFormat> = {
  vi: new Intl.NumberFormat("vi-VN", {
    style: "currency",
    currency: "VND",
    maximumFractionDigits: 0,
  }),
  en: new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "VND",
    maximumFractionDigits: 0,
  }),
};

/** Format a money value as VND in the active locale. */
export const formatMoney = (value: number | string) =>
  moneyFormatters[getActiveLocale()].format(
    typeof value === "string" ? Number(value) : value,
  );

/** Format an ISO date in the active locale. */
export const formatDate = (iso: string) =>
  new Date(iso).toLocaleDateString(LOCALE_BCP47[getActiveLocale()], {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
  });

/** Aggregate orders' lines by product → combined buying manifest. */
export function combineLines(
  orders: Order[],
): { product_id: string; product_name: string; quantity: number; total: number }[] {
  const map = new Map<
    string,
    { product_id: string; product_name: string; quantity: number; total: number }
  >();
  for (const order of orders) {
    for (const line of order.lines) {
      const existing = map.get(line.product_id);
      if (existing) {
        existing.quantity += line.quantity;
        existing.total += toNumber(line.line_total);
      } else {
        map.set(line.product_id, {
          product_id: line.product_id,
          product_name: line.product_name,
          quantity: line.quantity,
          total: toNumber(line.line_total),
        });
      }
    }
  }
  return [...map.values()];
}

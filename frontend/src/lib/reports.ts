/** Reports (lãi/lỗ, công nợ): API types + fetchers (backend /reports). */

import { apiFetch } from "@/lib/api";
import type { OrderStatus } from "@/lib/orders";
import type { TripStatus } from "@/lib/trips";

export type OrderProfit = {
  order_id: string;
  tracking_code: string;
  customer_name: string;
  status: OrderStatus;
  trip_id: string | null;
  revenue: string;
  cost: string;
  profit: string;
  margin_pct: string | null;
  cost_complete: boolean;
  created_at: string;
};

export type ProfitReport = {
  orders: OrderProfit[];
  total_revenue: string;
  total_cost: string;
  total_profit: string;
  orders_count: number;
  orders_with_incomplete_cost: number;
};

export type AgingBucketId = "d0_7" | "d8_30" | "d31_60" | "d61_plus";

export type Receivable = {
  order_id: string;
  tracking_code: string;
  customer_id: string;
  customer_name: string;
  status: OrderStatus;
  total_amount: string;
  total_collected: string;
  remaining: string;
  created_at: string;
  age_days: number;
  aging_bucket: AgingBucketId;
  deposit_due: string;
  deposit_covered: boolean;
};

export type AgingBucket = {
  bucket: AgingBucketId;
  orders_count: number;
  outstanding: string;
};

export type ReceivablesReport = {
  orders: Receivable[];
  total_outstanding: string;
  orders_count: number;
  buckets: AgingBucket[];
  total_deposit_due: string;
  deposit_shortfall: string;
  collection_rate_pct: string;
};

export type StatusCount = {
  status: OrderStatus;
  count: number;
  total_amount: string;
};

export type OverviewReport = {
  status_breakdown: StatusCount[];
  orders_count: number;
  total_revenue: string;
  total_collected: string;
  total_outstanding: string;
  total_deposit_due: string;
  total_cost: string;
  total_profit: string;
  unassigned_count: number;
};

export type DailyBucket = {
  date: string;
  orders_count: number;
  confirmed_count: number;
  revenue: string;
  collected: string;
  cost: string;
};

export type DailySummary = {
  days: DailyBucket[];
  orders_count: number;
  confirmed_count: number;
  revenue: string;
  collected: string;
  cost: string;
};

export type CashFlowReport = {
  cash_in: string;
  cash_out: string;
  refunded: string;
  net: string;
  pending_purchase_cost: string;
};

export type TripPnl = {
  trip_id: string;
  trip_code: string;
  trip_name: string;
  status: TripStatus;
  shopper_name: string;
  departure_date: string | null;
  arrival_date: string | null;
  orders_count: number;
  revenue: string;
  cost: string;
  profit: string;
  margin_pct: string | null;
  collected: string;
  outstanding: string;
  total_quantity: number;
  purchased_quantity: number;
  purchase_progress_pct: string;
  cost_complete: boolean;
};

export type TripReport = {
  trips: TripPnl[];
  trips_count: number;
  total_revenue: string;
  total_cost: string;
  total_profit: string;
};

export type ProductMetric = {
  product_id: string;
  product_code: string;
  product_name: string;
  orders_count: number;
  quantity_sold: number;
  purchased_quantity: number;
  revenue: string;
  cost: string;
  profit: string;
  margin_pct: string | null;
  cost_complete: boolean;
};

export type ProductReport = {
  products: ProductMetric[];
  products_count: number;
  total_quantity: number;
  total_revenue: string;
  total_cost: string;
  total_profit: string;
};

export type CustomerMetric = {
  customer_id: string;
  customer_name: string;
  phone: string;
  orders_count: number;
  revenue: string;
  collected: string;
  outstanding: string;
  avg_order_value: string;
  last_order_at: string;
  is_new: boolean;
};

export type CustomerReport = {
  customers: CustomerMetric[];
  customers_count: number;
  new_customers_count: number;
  returning_customers_count: number;
  total_revenue: string;
  total_outstanding: string;
};

export type StuckStatus = {
  status: OrderStatus;
  count: number;
  oldest_days: number;
  total_amount: string;
};

export type OperationsReport = {
  orders_count: number;
  cancelled_count: number;
  cancellation_rate_pct: string;
  purchase_completion_pct: string;
  unassigned_count: number;
  stale_days: number;
  stuck: StuckStatus[];
};

export type PeriodKpis = {
  date_from: string;
  date_to: string;
  orders_count: number;
  revenue: string;
  collected: string;
  cost: string;
  profit: string;
};

export type PeriodComparison = {
  current: PeriodKpis;
  previous: PeriodKpis;
};

export function getProfitReport(filters: {
  date_from?: string;
  date_to?: string;
  trip_id?: string;
} = {}): Promise<ProfitReport> {
  const params = new URLSearchParams();
  if (filters.date_from) params.set("date_from", filters.date_from);
  if (filters.date_to) params.set("date_to", filters.date_to);
  if (filters.trip_id) params.set("trip_id", filters.trip_id);
  const qs = params.toString();
  return apiFetch<ProfitReport>(`/reports/profit${qs ? `?${qs}` : ""}`);
}

export function getReceivablesReport(): Promise<ReceivablesReport> {
  return apiFetch<ReceivablesReport>("/reports/receivables");
}

export function getOverviewReport(): Promise<OverviewReport> {
  return apiFetch<OverviewReport>("/reports/overview");
}

export function getDailySummaryReport(filters: {
  date_from?: string;
  date_to?: string;
} = {}): Promise<DailySummary> {
  const params = new URLSearchParams();
  if (filters.date_from) params.set("date_from", filters.date_from);
  if (filters.date_to) params.set("date_to", filters.date_to);
  const qs = params.toString();
  return apiFetch<DailySummary>(`/reports/daily-summary${qs ? `?${qs}` : ""}`);
}

export function getCashFlowReport(filters: {
  date_from?: string;
  date_to?: string;
} = {}): Promise<CashFlowReport> {
  const params = new URLSearchParams();
  if (filters.date_from) params.set("date_from", filters.date_from);
  if (filters.date_to) params.set("date_to", filters.date_to);
  const qs = params.toString();
  return apiFetch<CashFlowReport>(`/reports/cash-flow${qs ? `?${qs}` : ""}`);
}

export function getTripReport(): Promise<TripReport> {
  return apiFetch<TripReport>("/reports/trips");
}

export function getProductReport(filters: {
  date_from?: string;
  date_to?: string;
} = {}): Promise<ProductReport> {
  const params = new URLSearchParams();
  if (filters.date_from) params.set("date_from", filters.date_from);
  if (filters.date_to) params.set("date_to", filters.date_to);
  const qs = params.toString();
  return apiFetch<ProductReport>(`/reports/products${qs ? `?${qs}` : ""}`);
}

export function getCustomerReport(filters: {
  date_from?: string;
  date_to?: string;
} = {}): Promise<CustomerReport> {
  const params = new URLSearchParams();
  if (filters.date_from) params.set("date_from", filters.date_from);
  if (filters.date_to) params.set("date_to", filters.date_to);
  const qs = params.toString();
  return apiFetch<CustomerReport>(`/reports/customers${qs ? `?${qs}` : ""}`);
}

export function getOperationsReport(filters: {
  date_from?: string;
  date_to?: string;
  stale_days?: number;
} = {}): Promise<OperationsReport> {
  const params = new URLSearchParams();
  if (filters.date_from) params.set("date_from", filters.date_from);
  if (filters.date_to) params.set("date_to", filters.date_to);
  if (filters.stale_days != null) params.set("stale_days", String(filters.stale_days));
  const qs = params.toString();
  return apiFetch<OperationsReport>(`/reports/operations${qs ? `?${qs}` : ""}`);
}

export function getPeriodComparison(filters: {
  date_from?: string;
  date_to?: string;
} = {}): Promise<PeriodComparison> {
  const params = new URLSearchParams();
  if (filters.date_from) params.set("date_from", filters.date_from);
  if (filters.date_to) params.set("date_to", filters.date_to);
  const qs = params.toString();
  return apiFetch<PeriodComparison>(
    `/reports/period-comparison${qs ? `?${qs}` : ""}`,
  );
}

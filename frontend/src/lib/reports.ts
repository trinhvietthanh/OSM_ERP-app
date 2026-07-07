/** Reports (lãi/lỗ, công nợ): API types + fetchers (backend /reports). */

import { apiFetch } from "@/lib/api";
import type { OrderStatus } from "@/lib/orders";

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
};

export type ReceivablesReport = {
  orders: Receivable[];
  total_outstanding: string;
  orders_count: number;
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

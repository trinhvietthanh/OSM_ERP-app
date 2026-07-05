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

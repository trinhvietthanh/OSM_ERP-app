/** Trip domain (chuyến hàng / gom đơn): API types + fetchers (backend /trips). */

import { apiFetch } from "@/lib/api";
import type { Order } from "@/lib/orders";

export type TripStatus =
  | "planning"
  | "buying"
  | "shipping"
  | "arrived"
  | "completed"
  | "cancelled";

export type Trip = {
  id: string;
  organization_id: string;
  code: string;
  name: string;
  status: TripStatus;
  shopper_name: string;
  departure_date: string | null;
  arrival_date: string | null;
  note: string;
  created_at: string;
  updated_at: string;
};

export const TRIP_STATUS_LABELS: Record<TripStatus, string> = {
  planning: "Lên kế hoạch",
  buying: "Đang mua",
  shipping: "Đang vận chuyển",
  arrived: "Đã về VN",
  completed: "Hoàn tất",
  cancelled: "Đã hủy",
};

export const TRIP_STATUS_VARIANT: Record<
  TripStatus,
  "default" | "secondary" | "destructive" | "outline"
> = {
  planning: "outline",
  buying: "secondary",
  shipping: "secondary",
  arrived: "default",
  completed: "default",
  cancelled: "destructive",
};

/** Next legal forward step for the quick-advance button. */
export const NEXT_TRIP_STATUS: Partial<Record<TripStatus, TripStatus>> = {
  planning: "buying",
  buying: "shipping",
  shipping: "arrived",
  arrived: "completed",
};

export function listTrips(status?: TripStatus): Promise<Trip[]> {
  const qs = status ? `?status=${status}` : "";
  return apiFetch<Trip[]>(`/trips${qs}`);
}

export function getTrip(id: string): Promise<Trip> {
  return apiFetch<Trip>(`/trips/${id}`);
}

export function createTrip(input: {
  code: string;
  name: string;
  shopper_name?: string;
  departure_date?: string | null;
  arrival_date?: string | null;
  note?: string;
}): Promise<Trip> {
  return apiFetch<Trip>("/trips", {
    method: "POST",
    body: JSON.stringify(input),
  });
}

export function updateTrip(
  id: string,
  patch: {
    name?: string;
    shopper_name?: string;
    departure_date?: string | null;
    arrival_date?: string | null;
    note?: string;
  },
): Promise<Trip> {
  return apiFetch<Trip>(`/trips/${id}`, {
    method: "PATCH",
    body: JSON.stringify(patch),
  });
}

export function changeTripStatus(
  id: string,
  status: TripStatus,
): Promise<Trip> {
  return apiFetch<Trip>(`/trips/${id}/status`, {
    method: "POST",
    body: JSON.stringify({ status }),
  });
}

export function listTripOrders(id: string): Promise<Order[]> {
  return apiFetch<Order[]>(`/trips/${id}/orders`);
}

export function attachOrders(id: string, orderIds: string[]): Promise<void> {
  return apiFetch<void>(`/trips/${id}/orders`, {
    method: "POST",
    body: JSON.stringify({ order_ids: orderIds }),
  });
}

export function detachOrder(id: string, orderId: string): Promise<void> {
  return apiFetch<void>(`/trips/${id}/orders/${orderId}`, {
    method: "DELETE",
  });
}

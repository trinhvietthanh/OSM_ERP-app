/** Customer domain: API types + fetchers (backend /customers). */

import { apiFetch } from "@/lib/api";

export type Customer = {
  id: string;
  organization_id: string;
  name: string;
  phone: string | null;
  note: string;
  active: boolean;
  created_at: string;
  updated_at: string;
};

export function listCustomers(search?: string): Promise<Customer[]> {
  const qs = search ? `?search=${encodeURIComponent(search)}` : "";
  return apiFetch<Customer[]>(`/customers${qs}`);
}

export function createCustomer(input: {
  name: string;
  phone?: string;
  note?: string;
}): Promise<Customer> {
  return apiFetch<Customer>("/customers", {
    method: "POST",
    body: JSON.stringify(input),
  });
}

export function updateCustomer(
  id: string,
  patch: { name?: string; phone?: string; note?: string; active?: boolean },
): Promise<Customer> {
  return apiFetch<Customer>(`/customers/${id}`, {
    method: "PATCH",
    body: JSON.stringify(patch),
  });
}

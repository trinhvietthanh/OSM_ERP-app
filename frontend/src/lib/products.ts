/** Catalog products: API types + fetchers (backend /catalog/products). */

import { apiFetch } from "@/lib/api";

export type Product = {
  id: string;
  organization_id: string;
  code: string;
  name: string;
  description: string;
  active: boolean;
  created_at: string;
  updated_at: string;
};

export function listProducts(): Promise<Product[]> {
  return apiFetch<Product[]>("/catalog/products");
}

export function createProduct(input: {
  code: string;
  name: string;
  description?: string;
}): Promise<Product> {
  return apiFetch<Product>("/catalog/products", {
    method: "POST",
    body: JSON.stringify(input),
  });
}

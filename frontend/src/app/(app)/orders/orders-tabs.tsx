"use client";

import { useRouter, useSearchParams } from "next/navigation";

import { cn } from "@/lib/utils";

import { OrdersList } from "./orders-browser";
import { CreateOrderForm } from "./create-order-form";
import { ConsolidateOrders } from "./consolidate-orders";

const TABS = [
  { id: "list", label: "Danh sách" },
  { id: "create", label: "Tạo đơn" },
  { id: "consolidate", label: "Gom đơn" },
] as const;

type TabId = (typeof TABS)[number]["id"];

const isTabId = (value: string | null): value is TabId =>
  !!value && (TABS as readonly { id: string }[]).some((t) => t.id === value);

/**
 * Orders page container. Each tab fetches its own data via TanStack Query;
 * the active tab is driven by `?tab=` so the "New" buttons can deep-link.
 * Wrapped in a Suspense boundary by the server page (useSearchParams).
 */
export function OrdersTabs() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const tabParam = searchParams.get("tab");
  const tab: TabId = isTabId(tabParam) ? tabParam : "list";

  function setTab(next: TabId) {
    router.push(`/orders?tab=${next}`);
  }

  return (
    <div className="space-y-4">
      <div className="inline-flex rounded-xl bg-muted p-1">
        {TABS.map((t) => {
          const active = tab === t.id;
          return (
            <button
              key={t.id}
              type="button"
              aria-pressed={active}
              onClick={() => setTab(t.id)}
              className={cn(
                "rounded-lg px-3.5 py-1.5 text-sm font-medium transition-colors",
                active
                  ? "bg-background text-primary shadow-sm"
                  : "text-muted-foreground hover:text-foreground",
              )}
            >
              {t.label}
            </button>
          );
        })}
      </div>

      {tab === "list" && <OrdersList />}
      {tab === "create" && (
        <CreateOrderForm
          onCreated={() => setTab("list")}
          onCancel={() => setTab("list")}
        />
      )}
      {tab === "consolidate" && <ConsolidateOrders />}
    </div>
  );
}

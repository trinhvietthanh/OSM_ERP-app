"use client";

import { useRouter, useSearchParams } from "next/navigation";

import { cn } from "@/lib/utils";
import { useI18n } from "@/components/i18n-provider";
import type { TranslationKey } from "@/lib/i18n/dictionaries";

import { OrdersList } from "./orders-browser";
import { CreateOrderForm } from "./create-order-form";
import { ConsolidateOrders } from "./consolidate-orders";

const TABS = [
  { id: "list", labelKey: "orders.tabs.list" },
  { id: "create", labelKey: "orders.tabs.create" },
  { id: "consolidate", labelKey: "orders.tabs.consolidate" },
] as const satisfies readonly { id: TabId; labelKey: TranslationKey }[];

type TabId = "list" | "create" | "consolidate";

const isTabId = (value: string | null): value is TabId =>
  !!value && TABS.some((t) => t.id === value);

/**
 * Orders page container. Each tab fetches its own data via TanStack Query;
 * the active tab is driven by `?tab=` so the "New" buttons can deep-link.
 * Wrapped in a Suspense boundary by the server page (useSearchParams).
 */
export function OrdersTabs() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { t } = useI18n();
  const tabParam = searchParams.get("tab");
  const tab: TabId = isTabId(tabParam) ? tabParam : "list";

  function setTab(next: TabId) {
    router.push(`/orders?tab=${next}`);
  }

  return (
    <div className="space-y-4">
      <div className="inline-flex rounded-xl bg-muted p-1">
        {TABS.map((tabItem) => {
          const active = tab === tabItem.id;
          return (
            <button
              key={tabItem.id}
              type="button"
              aria-pressed={active}
              onClick={() => setTab(tabItem.id)}
              className={cn(
                "rounded-lg px-3.5 py-1.5 text-sm font-medium transition-colors",
                active
                  ? "bg-background text-primary shadow-sm"
                  : "text-muted-foreground hover:text-foreground",
              )}
            >
              {t(tabItem.labelKey as TranslationKey)}
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

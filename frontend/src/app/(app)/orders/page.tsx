import { Suspense } from "react";

import { OrdersTabs } from "./orders-tabs";
import { Card } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";

/**
 * Orders page (list · tạo đơn · gom đơn). `OrdersTabs` reads `?tab=` (and the
 * list reads `?q=`) from the URL, so it is wrapped in a Suspense boundary —
 * Next.js requires this for `useSearchParams` to keep the route static.
 */
export default function OrdersPage() {
  return (
    <Suspense fallback={<OrdersFallback />}>
      <OrdersTabs />
    </Suspense>
  );
}

function OrdersFallback() {
  return (
    <div className="space-y-3">
      {Array.from({ length: 6 }).map((_, i) => (
        <Card key={i} className="py-3">
          <Skeleton className="mx-4 h-9 rounded-lg" />
        </Card>
      ))}
    </div>
  );
}

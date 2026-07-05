import { Suspense } from "react";

import { TrackingLookup } from "./tracking-lookup";

export const metadata = {
  title: "Tra cứu đơn hàng | App ERP",
  description: "Nhập mã Code để xem tình trạng đơn hàng của bạn.",
};

export default function TrackingPage() {
  return (
    <Suspense>
      <TrackingLookup />
    </Suspense>
  );
}

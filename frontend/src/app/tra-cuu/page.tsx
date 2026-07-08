import { Suspense } from "react";
import type { Metadata } from "next";

import { getT } from "@/lib/i18n/server";
import { TrackingLookup } from "./tracking-lookup";

export async function generateMetadata(): Promise<Metadata> {
  const t = await getT();
  return {
    title: t("tracking.metaTitle"),
    description: t("tracking.subtitle"),
  };
}

export default function TrackingPage() {
  return (
    <Suspense>
      <TrackingLookup />
    </Suspense>
  );
}

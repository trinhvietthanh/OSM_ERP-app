"use client";

import { useEffect, useSyncExternalStore } from "react";
import { useRouter } from "next/navigation";

import { isAuthenticated } from "@/lib/api";

// `useSyncExternalStore` reads the browser-only token without a hydration
// mismatch: server (and the first client paint) see `false` via the server
// snapshot — a neutral loader — then the client re-renders with the real value.
const subscribe = () => () => {};
const getClientSnapshot = () => isAuthenticated();
const getServerSnapshot = () => false;

/**
 * Client-side route guard for the authenticated shell (`(app)` route group).
 *
 * The JWT lives in localStorage, which is browser-only — so the check can only
 * run on the client (edge middleware can't see it). On mount:
 *   - no token  → redirect to /login, render only a loader (no protected
 *     content flashes before the redirect);
 *   - token present → render children.
 */
export function AuthGuard({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const allowed = useSyncExternalStore(
    subscribe,
    getClientSnapshot,
    getServerSnapshot,
  );

  useEffect(() => {
    if (!allowed) router.replace("/login");
  }, [allowed, router]);

  if (!allowed) {
    return (
      <div className="flex min-h-dvh-safe items-center justify-center bg-background">
        <div className="size-7 animate-spin rounded-full border-2 border-muted border-t-primary" />
      </div>
    );
  }

  return <>{children}</>;
}

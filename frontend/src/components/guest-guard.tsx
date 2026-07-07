"use client";

import { useEffect, useSyncExternalStore } from "react";
import { useRouter } from "next/navigation";

import { isAuthenticated } from "@/lib/api";

const subscribe = () => () => {};
const getClientSnapshot = () => isAuthenticated();
const getServerSnapshot = () => false;

/**
 * Guest-only route guard — the inverse of :class:`AuthGuard`. Used on `/login`:
 * a visitor who is already authenticated is bounced to `/` instead of seeing
 * the sign-in form again.
 */
export function GuestGuard({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const authed = useSyncExternalStore(
    subscribe,
    getClientSnapshot,
    getServerSnapshot,
  );

  useEffect(() => {
    if (authed) router.replace("/");
  }, [authed, router]);

  if (authed) {
    return (
      <div className="flex min-h-dvh-safe items-center justify-center bg-background">
        <div className="size-7 animate-spin rounded-full border-2 border-muted border-t-primary" />
      </div>
    );
  }

  return <>{children}</>;
}

import type { Metadata } from "next";
import Link from "next/link";
import { Check, LayoutGrid } from "lucide-react";

import { GuestGuard } from "@/components/guest-guard";
import { LoginForm } from "./login-form";

export const metadata: Metadata = {
  title: "Sign in",
};

const FEATURES = [
  "Quick pre-order creation for customers",
  "Consolidate orders into delivery batches",
  "Live dashboard analytics on any device",
];

/**
 * Login screen.
 *
 * - Desktop (lg+): a two-column split — a branded marketing panel on the left
 *   and the sign-in form on the right.
 * - Mobile: the form panel alone, centered with a compact logo.
 */
export default function LoginPage() {
  return (
    <GuestGuard>
      <div className="grid min-h-dvh-safe w-full lg:grid-cols-2">
      {/* Brand panel — desktop only */}
      <aside className="relative hidden flex-col justify-between overflow-hidden bg-primary p-10 text-primary-foreground lg:flex">
        <div className="pointer-events-none absolute -top-24 -right-24 size-80 rounded-full bg-primary-foreground/10" />
        <div className="pointer-events-none absolute -bottom-32 -left-24 size-96 rounded-full bg-primary-foreground/5" />

        <div className="relative flex items-center gap-2.5">
          <span className="flex size-9 items-center justify-center rounded-lg bg-primary-foreground/15">
            <LayoutGrid className="size-5" aria-hidden />
          </span>
          <span className="text-lg font-semibold tracking-tight">App ERP</span>
        </div>

        <div className="relative space-y-6">
          <div className="space-y-3">
            <h2 className="max-w-md text-3xl font-bold leading-tight tracking-tight">
              Run your entire operation from one dashboard.
            </h2>
            <p className="max-w-sm text-primary-foreground/70">
              Take pre-orders, consolidate shipments, and fulfill hand-carry
              orders — fast on every device.
            </p>
          </div>
          <ul className="space-y-3">
            {FEATURES.map((feature) => (
              <li key={feature} className="flex items-center gap-3">
                <span className="flex size-6 shrink-0 items-center justify-center rounded-full bg-primary-foreground/15">
                  <Check className="size-3.5" aria-hidden />
                </span>
                <span className="text-sm text-primary-foreground/90">
                  {feature}
                </span>
              </li>
            ))}
          </ul>
        </div>

        <p className="relative text-sm text-primary-foreground/60">
          © 2026 App ERP. All rights reserved.
        </p>
      </aside>

      {/* Form panel */}
      <div className="flex items-center justify-center bg-background p-6 sm:p-10">
        <div className="w-full max-w-sm">
          <div className="mb-8 flex items-center gap-2.5 lg:hidden">
            <span className="flex size-9 items-center justify-center rounded-lg bg-primary text-primary-foreground">
              <LayoutGrid className="size-5" aria-hidden />
            </span>
            <span className="text-lg font-semibold tracking-tight">App ERP</span>
          </div>

          <div className="mb-8 space-y-1.5">
            <h1 className="text-2xl font-bold tracking-tight">Sign in</h1>
            <p className="text-sm text-muted-foreground">
              Enter your credentials to access your dashboard.
            </p>
          </div>

          <LoginForm />

          <p className="mt-6 text-center text-sm text-muted-foreground">
            Don&apos;t have an account?{" "}
            <Link href="#" className="font-medium text-primary hover:underline">
              Sign up
            </Link>
          </p>
        </div>
      </div>
      </div>
    </GuestGuard>
  );
}

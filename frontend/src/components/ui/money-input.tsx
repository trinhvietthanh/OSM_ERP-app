"use client";

import * as React from "react";

import { cn } from "@/lib/utils";

/**
 * VND money input. Amounts here are almost always round thousands of đồng, so
 * the field is edited "in thousands": the user types the magnitude (e.g. 550)
 * and a fixed, faded **000** suffix is shown ready beside it — the bound value
 * is the full amount (e.g. "550000"). This saves typing three trailing zeros on
 * every price/deposit.
 *
 * If the bound value is not a clean multiple of 1000 (set from elsewhere), the
 * raw value is shown and the suffix hidden so it never misleads.
 */
function MoneyInput({
  value,
  onValueChange,
  className,
  ...props
}: Omit<React.ComponentProps<"input">, "value" | "onChange" | "type"> & {
  value: string;
  onValueChange: (value: string) => void;
}) {
  const str = value ?? "";
  const num = Number(str);
  const isCleanMultiple =
    str !== "" && Number.isFinite(num) && num % 1000 === 0;
  const shown = isCleanMultiple ? String(num / 1000) : str;
  const showSuffix = str === "" || isCleanMultiple;

  return (
    <div className="relative">
      <input
        type="number"
        inputMode="numeric"
        data-slot="input"
        value={shown}
        onChange={(event) => {
          const mag = event.target.value;
          if (mag === "") {
            onValueChange("");
            return;
          }
          const n = Number(mag);
          onValueChange(Number.isFinite(n) ? String(n * 1000) : mag);
        }}
        className={cn(
          "h-8 w-full min-w-0 rounded-lg border border-input bg-transparent px-2.5 py-1 pr-10 text-base transition-colors outline-none placeholder:text-muted-foreground focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50 disabled:pointer-events-none disabled:cursor-not-allowed disabled:bg-input/50 disabled:opacity-50 aria-invalid:border-destructive aria-invalid:ring-3 aria-invalid:ring-destructive/20 md:text-sm dark:bg-input/30 dark:disabled:bg-input/80 dark:aria-invalid:border-destructive/50 dark:aria-invalid:ring-destructive/40",
          className,
        )}
        {...props}
      />
      {showSuffix && (
        <span
          aria-hidden
          className="pointer-events-none absolute top-1/2 right-2.5 -translate-y-1/2 text-xs font-medium text-muted-foreground"
        >
          000
        </span>
      )}
    </div>
  );
}

export { MoneyInput };

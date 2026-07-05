"use client";

import { useState } from "react";
import { Check, ChevronDown } from "lucide-react";

import { cn } from "@/lib/utils";
import { Input } from "@/components/ui/input";

export type SearchSelectItem = {
  value: string;
  label: string;
  /** Optional secondary text (phone, sku, …). */
  meta?: string;
};

/**
 * Minimal dependency-free combobox: type to filter, click (or arrow keys) to
 * select. Used for picking customers and products in the order forms.
 */
export function SearchSelect({
  items,
  value,
  onChange,
  placeholder,
  ariaLabel,
  invalid,
}: {
  items: SearchSelectItem[];
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  ariaLabel?: string;
  invalid?: boolean;
}) {
  const selected = items.find((item) => item.value === value);
  const [query, setQuery] = useState(selected?.label ?? "");
  const [lastValue, setLastValue] = useState(value);
  // Keep the text box in sync when the selection changes externally.
  if (value !== lastValue) {
    setLastValue(value);
    setQuery(selected?.label ?? "");
  }

  const [open, setOpen] = useState(false);
  const [active, setActive] = useState(-1);

  const filtered = items.filter((item) =>
    item.label.toLowerCase().includes(query.trim().toLowerCase()),
  );

  function pick(item: SearchSelectItem) {
    onChange(item.value);
    setQuery(item.label);
    setOpen(false);
    setActive(-1);
  }

  function onKeyDown(event: React.KeyboardEvent) {
    if (event.key === "ArrowDown") {
      event.preventDefault();
      setOpen(true);
      setActive((index) => Math.min(index + 1, filtered.length - 1));
    } else if (event.key === "ArrowUp") {
      event.preventDefault();
      setActive((index) => Math.max(index - 1, 0));
    } else if (event.key === "Enter" && active >= 0) {
      event.preventDefault();
      const item = filtered[active];
      if (item) pick(item);
    } else if (event.key === "Escape") {
      setOpen(false);
    }
  }

  return (
    <div className="relative">
      <Input
        role="combobox"
        aria-expanded={open}
        aria-controls="search-select-listbox"
        aria-label={ariaLabel}
        aria-invalid={invalid}
        value={query}
        placeholder={placeholder}
        onChange={(event) => {
          setQuery(event.target.value);
          setOpen(true);
          setActive(-1);
          if (event.target.value === "") onChange("");
        }}
        onFocus={() => setOpen(true)}
        onBlur={() => setTimeout(() => setOpen(false), 120)}
        onKeyDown={onKeyDown}
        className="pr-8"
      />
      <ChevronDown
        className="pointer-events-none absolute top-1/2 right-2.5 size-4 -translate-y-1/2 text-muted-foreground"
        aria-hidden
      />

      {open && filtered.length > 0 && (
        <ul
          id="search-select-listbox"
          role="listbox"
          className="absolute z-50 mt-1 max-h-60 w-full overflow-auto rounded-lg border border-border bg-popover py-1 text-sm shadow-md"
        >
          {filtered.map((item, index) => {
            const isActive = item.value === value;
            return (
              <li key={item.value} role="option" aria-selected={isActive}>
                <button
                  type="button"
                  onMouseDown={(event) => {
                    event.preventDefault();
                    pick(item);
                  }}
                  className={cn(
                    "flex w-full items-center justify-between gap-2 px-2.5 py-1.5 text-left transition-colors",
                    index === active ? "bg-muted" : "hover:bg-muted/60",
                  )}
                >
                  <span className="flex min-w-0 flex-col">
                    <span className="truncate">{item.label}</span>
                    {item.meta && (
                      <span className="truncate text-xs text-muted-foreground">
                        {item.meta}
                      </span>
                    )}
                  </span>
                  {isActive && <Check className="size-4 shrink-0 text-primary" aria-hidden />}
                </button>
              </li>
            );
          })}
        </ul>
      )}
    </div>
  );
}

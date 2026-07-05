import {
  ArrowDownRight,
  ArrowUpRight,
  DollarSign,
  Download,
  ShoppingBag,
  ShoppingCart,
  Users,
} from "lucide-react";

import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";

const STATS = [
  {
    label: "Revenue",
    value: "$48.2k",
    delta: "+12.5%",
    up: true,
    icon: DollarSign,
  },
  { label: "Orders", value: "1,284", delta: "+3.1%", up: true, icon: ShoppingCart },
  { label: "Pre-orders", value: "312", delta: "+8.2%", up: true, icon: ShoppingBag },
  { label: "Customers", value: "642", delta: "+5.4%", up: true, icon: Users },
];

const ACTIVITY = [
  { id: "#1042", title: "Order #1042 shipped", time: "2m ago" },
  { id: "#1036", title: "Pre-order placed: Stark Industries", time: "18m ago" },
  { id: "#1040", title: "Payment received", time: "1h ago" },
  { id: "#1039", title: "New customer signed up", time: "3h ago" },
] as const;

const STATUS_BREAKDOWN = [
  { label: "Paid", count: 2, bar: "bg-primary" },
  { label: "Pending", count: 3, bar: "bg-amber-500" },
  { label: "Shipped", count: 2, bar: "bg-emerald-500" },
  { label: "Cancelled", count: 1, bar: "bg-destructive" },
] as const;
const STATUS_TOTAL = STATUS_BREAKDOWN.reduce((sum, s) => sum + s.count, 0);

const REVENUE = [
  { day: "Mon", value: 6.2 },
  { day: "Tue", value: 7.8 },
  { day: "Wed", value: 5.4 },
  { day: "Thu", value: 9.1 },
  { day: "Fri", value: 8.6 },
  { day: "Sat", value: 4.3 },
  { day: "Sun", value: 6.9 },
];
const REVENUE_MAX = Math.max(...REVENUE.map((d) => d.value));

const TOP_CUSTOMERS = [
  { name: "Hooli", orders: 38, revenue: "$12.4k" },
  { name: "Initech", orders: 27, revenue: "$9.1k" },
  { name: "Acme Corp", orders: 21, revenue: "$6.8k" },
  { name: "Globex", orders: 14, revenue: "$3.9k" },
];

export default function DashboardPage() {
  return (
    <div className="space-y-6">
      <section className="flex items-end justify-between gap-4">
        <div>
          <p className="text-sm text-muted-foreground">Welcome back 👋</p>
          <h2 className="text-2xl font-bold tracking-tight">Dashboard</h2>
        </div>
        <Button variant="outline" size="sm" className="gap-1.5">
          <Download aria-hidden />
          <span className="hidden sm:inline">Export</span>
        </Button>
      </section>

      <div className="lg:grid lg:grid-cols-[minmax(0,1fr)_320px] lg:items-start lg:gap-6">
        {/* Main column */}
        <div className="space-y-6">
          <section className="grid grid-cols-2 gap-3 lg:grid-cols-4">
            {STATS.map(({ label, value, delta, up, icon: Icon }) => (
              <Card key={label} className="gap-0 py-4">
                <CardContent className="px-4">
                  <div className="flex items-center justify-between">
                    <span className="flex size-9 items-center justify-center rounded-lg bg-primary/10 text-primary">
                      <Icon className="size-4.5" aria-hidden />
                    </span>
                    <span
                      className={`inline-flex items-center gap-0.5 text-xs font-medium ${
                        up ? "text-emerald-600" : "text-destructive"
                      }`}
                    >
                      {up ? (
                        <ArrowUpRight className="size-3.5" aria-hidden />
                      ) : (
                        <ArrowDownRight className="size-3.5" aria-hidden />
                      )}
                      {delta}
                    </span>
                  </div>
                  <p className="mt-3 text-2xl font-semibold">{value}</p>
                  <p className="text-sm text-muted-foreground">{label}</p>
                </CardContent>
              </Card>
            ))}
          </section>

          <section className="space-y-3">
            <div className="flex items-center justify-between">
              <h3 className="font-semibold">Revenue</h3>
              <span className="text-sm text-muted-foreground">Last 7 days</span>
            </div>
            <Card>
              <CardContent className="px-4 py-4">
                <div className="flex items-end gap-2">
                  {REVENUE.map((d) => {
                    const pct = Math.round((d.value / REVENUE_MAX) * 100);
                    return (
                      <div
                        key={d.day}
                        className="flex flex-1 flex-col items-center gap-2"
                      >
                        <div className="flex h-32 w-full items-end">
                          <div
                            className="w-full rounded-md bg-primary/80 transition-colors hover:bg-primary"
                            style={{ height: `${Math.max(4, pct)}%` }}
                            title={`$${d.value}k`}
                          />
                        </div>
                        <span className="text-xs text-muted-foreground">
                          {d.day}
                        </span>
                      </div>
                    );
                  })}
                </div>
              </CardContent>
            </Card>
          </section>

          <section className="space-y-3">
            <div className="flex items-center justify-between">
              <h3 className="font-semibold">Recent activity</h3>
              <button className="text-sm font-medium text-primary">See all</button>
            </div>
            <Card className="py-2">
              <CardContent className="divide-y divide-border px-0">
                {ACTIVITY.map((item) => (
                  <div
                    key={item.id}
                    className="flex items-center justify-between px-4 py-3"
                  >
                    <div className="min-w-0">
                      <p className="truncate text-sm font-medium">{item.title}</p>
                      <p className="text-xs text-muted-foreground">{item.time}</p>
                    </div>
                    <Badge variant="secondary">{item.id}</Badge>
                  </div>
                ))}
              </CardContent>
            </Card>
          </section>
        </div>

        {/* Desktop aside */}
        <aside className="hidden space-y-6 lg:block">
          <Card>
            <CardContent className="space-y-3 px-4 py-4">
              <h3 className="font-semibold">Orders by status</h3>
              <ul className="space-y-2.5">
                {STATUS_BREAKDOWN.map((s) => (
                  <li key={s.label}>
                    <div className="flex items-center justify-between text-sm">
                      <span>{s.label}</span>
                      <span className="text-xs text-muted-foreground tabular-nums">
                        {s.count}
                      </span>
                    </div>
                    <div className="mt-1.5 h-1.5 w-full overflow-hidden rounded-full bg-muted">
                      <div
                        className={`h-full rounded-full ${s.bar}`}
                        style={{
                          width: `${Math.round((s.count / STATUS_TOTAL) * 100)}%`,
                        }}
                      />
                    </div>
                  </li>
                ))}
              </ul>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="space-y-3 px-4 py-4">
              <h3 className="font-semibold">Top customers</h3>
              <ul className="divide-y divide-border">
                {TOP_CUSTOMERS.map((c, i) => (
                  <li
                    key={c.name}
                    className="flex items-center justify-between py-2.5 first:pt-0 last:pb-0"
                  >
                    <div className="flex min-w-0 items-center gap-3">
                      <span className="flex size-6 shrink-0 items-center justify-center rounded-full bg-muted text-xs font-medium text-muted-foreground tabular-nums">
                        {i + 1}
                      </span>
                      <span className="truncate text-sm font-medium">{c.name}</span>
                    </div>
                    <div className="text-right">
                      <p className="text-sm font-medium tabular-nums">{c.revenue}</p>
                      <p className="text-xs text-muted-foreground tabular-nums">
                        {c.orders} orders
                      </p>
                    </div>
                  </li>
                ))}
              </ul>
            </CardContent>
          </Card>
        </aside>
      </div>
    </div>
  );
}

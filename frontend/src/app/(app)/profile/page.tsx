import {
  Bell,
  ChevronRight,
  CreditCard,
  LogOut,
  Settings,
  ShieldCheck,
} from "lucide-react";

import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Card, CardContent } from "@/components/ui/card";
import InstallPrompt from "@/components/InstallPrompt";
import { DemoForm } from "@/components/examples/demo-form";

const SETTINGS = [
  { label: "Account settings", icon: Settings },
  { label: "Notifications", icon: Bell },
  { label: "Billing", icon: CreditCard },
  { label: "Security", icon: ShieldCheck },
];

export default function ProfilePage() {
  return (
    <div className="space-y-6 lg:grid lg:grid-cols-[280px_minmax(0,1fr)] lg:items-start lg:gap-6 lg:space-y-0">
      {/* Left rail: identity + sign out */}
      <div className="space-y-6">
        <Card>
          <CardContent className="flex items-center gap-4 px-4">
            <Avatar className="size-14">
              <AvatarFallback className="bg-primary/10 text-lg font-semibold text-primary">
                AL
              </AvatarFallback>
            </Avatar>
            <div className="min-w-0">
              <p className="truncate text-lg font-semibold">Ada Lovelace</p>
              <p className="truncate text-sm text-muted-foreground">
                ada@example.com
              </p>
            </div>
          </CardContent>
        </Card>

        <button className="flex w-full items-center justify-center gap-2 rounded-xl border border-border py-3 text-sm font-medium text-destructive transition-colors hover:bg-destructive/5">
          <LogOut className="size-4" aria-hidden />
          Sign out
        </button>
      </div>

      {/* Right column: settings + install + demo */}
      <div className="space-y-6">
        <Card className="py-2">
          <CardContent className="divide-y divide-border px-0">
            {SETTINGS.map(({ label, icon: Icon }) => (
              <button
                key={label}
                className="flex w-full items-center gap-3 px-4 py-3 text-left transition-colors hover:bg-muted/50"
              >
                <Icon className="size-5 text-muted-foreground" aria-hidden />
                <span className="flex-1 text-sm font-medium">{label}</span>
                <ChevronRight
                  className="size-4 text-muted-foreground"
                  aria-hidden
                />
              </button>
            ))}
          </CardContent>
        </Card>

        <InstallPrompt />

        <section className="space-y-2">
          <h3 className="px-1 text-sm font-medium text-muted-foreground">
            Stack demo
          </h3>
          <DemoForm />
        </section>
      </div>
    </div>
  );
}

import { AppBar } from "@/components/layout/app-bar";
import { BottomNav } from "@/components/layout/bottom-nav";
import { Sidebar } from "@/components/layout/sidebar";

/**
 * Responsive app shell.
 *
 * - Mobile (< lg): a phone-width column with a sticky top app bar and a sticky
 *   bottom tab bar.
 * - Desktop (>= lg): a fixed left sidebar with a full-width content area; the
 *   bottom tab bar is hidden and content is centered to a readable max width.
 */
export default function AppLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <div className="mx-auto flex min-h-dvh-safe w-full max-w-md flex-col bg-background shadow-sm lg:max-w-none lg:flex-row lg:shadow-none">
      <Sidebar />
      <div className="flex min-w-0 flex-1 flex-col">
        <AppBar />
        <main className="flex-1 px-4 py-4 lg:px-8 lg:py-6">
          <div className="mx-auto w-full lg:max-w-6xl xl:max-w-7xl">
            {children}
          </div>
        </main>
        <BottomNav />
      </div>
    </div>
  );
}

"use client";

import { useEffect, useState } from "react";
import { Download, Share } from "lucide-react";

import { Button } from "@/components/ui/button";

type BeforeInstallPromptEvent = Event & {
  prompt: () => Promise<void>;
  userChoice: Promise<{ outcome: "accepted" | "dismissed" }>;
};

/**
 * Shows an "Install" button when the browser fires `beforeinstallprompt`
 * (Chromium), and iOS-specific instructions on Safari, hidden once the
 * app is already running in standalone (installed) mode.
 */
export default function InstallPrompt() {
  const [deferred, setDeferred] = useState<BeforeInstallPromptEvent | null>(
    null,
  );
  const [isIOS, setIsIOS] = useState(false);
  const [isStandalone, setIsStandalone] = useState(false);

  useEffect(() => {
    // Client-only feature detection: values come from browser APIs that are
    // unavailable during SSR, so they must be read after mount.
    /* eslint-disable react-hooks/set-state-in-effect */
    setIsIOS(
      /iPad|iPhone|iPod/.test(navigator.userAgent) && !("MSStream" in window),
    );
    setIsStandalone(window.matchMedia("(display-mode: standalone)").matches);
    /* eslint-enable react-hooks/set-state-in-effect */

    const onPrompt = (e: Event) => {
      e.preventDefault();
      setDeferred(e as BeforeInstallPromptEvent);
    };
    window.addEventListener("beforeinstallprompt", onPrompt);
    return () => window.removeEventListener("beforeinstallprompt", onPrompt);
  }, []);

  if (isStandalone) return null;

  async function install() {
    if (!deferred) return;
    await deferred.prompt();
    await deferred.userChoice;
    setDeferred(null);
  }

  return (
    <div className="rounded-xl border border-border bg-card p-4 text-card-foreground">
      <h3 className="mb-1 font-semibold">Install App ERP</h3>
      {deferred ? (
        <>
          <p className="mb-3 text-sm text-muted-foreground">
            Add the app to your home screen for a full-screen experience.
          </p>
          <Button onClick={install} className="w-full">
            <Download className="size-4" aria-hidden />
            Add to Home Screen
          </Button>
        </>
      ) : isIOS ? (
        <p className="flex items-start gap-1.5 text-sm text-muted-foreground">
          <Share className="mt-0.5 size-4 shrink-0" aria-hidden />
          <span>
            Tap the Share button, then{" "}
            <strong className="text-foreground">Add to Home Screen</strong>.
          </span>
        </p>
      ) : (
        <p className="text-sm text-muted-foreground">
          Your browser will offer to install this app when it&apos;s ready.
        </p>
      )}
    </div>
  );
}

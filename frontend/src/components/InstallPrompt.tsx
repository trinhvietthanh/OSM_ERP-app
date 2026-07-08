"use client";

import { useEffect, useState } from "react";
import { Download, Share } from "lucide-react";

import { Button } from "@/components/ui/button";
import { useI18n } from "@/components/i18n-provider";

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
  const { t } = useI18n();
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
      <h3 className="mb-1 font-semibold">{t("install.title")}</h3>
      {deferred ? (
        <>
          <p className="mb-3 text-sm text-muted-foreground">{t("install.desc")}</p>
          <Button onClick={install} className="w-full">
            <Download className="size-4" aria-hidden />
            {t("install.addHome")}
          </Button>
        </>
      ) : isIOS ? (
        <p className="flex items-start gap-1.5 text-sm text-muted-foreground">
          <Share className="mt-0.5 size-4 shrink-0" aria-hidden />
          <span>
            {t("install.iosPrefix")}
            <strong className="text-foreground">{t("install.iosBold")}</strong>.
          </span>
        </p>
      ) : (
        <p className="text-sm text-muted-foreground">{t("install.fallback")}</p>
      )}
    </div>
  );
}

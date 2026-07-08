import {
  BarChart3,
  LayoutDashboard,
  Plane,
  ShoppingCart,
  User,
} from "lucide-react";
import type { LucideIcon } from "lucide-react";

import type { TranslationKey } from "@/lib/i18n/dictionaries";

export type NavItem = {
  href: string;
  /** Dictionary key rendered via `t(item.label)`. */
  label: TranslationKey;
  icon: LucideIcon;
  /**
   * When true, this item is omitted from the mobile bottom tab bar (which has a
   * fixed slot count) but remains available in the desktop sidebar.
   */
  mobileHidden?: boolean;
};

/** Primary destinations shown in the bottom tab bar (mobile) and sidebar (desktop). */
export const NAV_ITEMS: NavItem[] = [
  { href: "/", label: "nav.home", icon: LayoutDashboard },
  { href: "/orders", label: "nav.orders", icon: ShoppingCart },
  { href: "/trips", label: "nav.trips", icon: Plane },
  { href: "/reports", label: "nav.reports", icon: BarChart3, mobileHidden: true },
  { href: "/profile", label: "nav.profile", icon: User },
];

/** Items shown in the mobile bottom tab bar (excludes `mobileHidden` entries). */
export const MOBILE_NAV_ITEMS = NAV_ITEMS.filter((item) => !item.mobileHidden);

/** Whether `href` is the active route for `pathname` (exact for "/", prefix otherwise). */
export function isNavActive(pathname: string, href: string) {
  if (href === "/") return pathname === "/";
  return pathname === href || pathname.startsWith(`${href}/`);
}

/** Resolve the dictionary key for the current page title (render via `t()`). */
export function navTitleKey(pathname: string): TranslationKey {
  return (
    NAV_ITEMS.find((item) => isNavActive(pathname, item.href))?.label ??
    "nav.appName"
  );
}

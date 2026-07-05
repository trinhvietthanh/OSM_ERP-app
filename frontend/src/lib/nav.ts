import {
  BarChart3,
  LayoutDashboard,
  Plane,
  ShoppingCart,
  User,
} from "lucide-react";
import type { LucideIcon } from "lucide-react";

export type NavItem = {
  href: string;
  label: string;
  icon: LucideIcon;
  /**
   * When true, this item is omitted from the mobile bottom tab bar (which has a
   * fixed slot count) but remains available in the desktop sidebar.
   */
  mobileHidden?: boolean;
};

/** Primary destinations shown in the bottom tab bar (mobile) and sidebar (desktop). */
export const NAV_ITEMS: NavItem[] = [
  { href: "/", label: "Trang chủ", icon: LayoutDashboard },
  { href: "/orders", label: "Đơn hàng", icon: ShoppingCart },
  { href: "/trips", label: "Chuyến hàng", icon: Plane },
  { href: "/reports", label: "Báo cáo", icon: BarChart3, mobileHidden: true },
  { href: "/profile", label: "Cá nhân", icon: User },
];

/** Items shown in the mobile bottom tab bar (excludes `mobileHidden` entries). */
export const MOBILE_NAV_ITEMS = NAV_ITEMS.filter((item) => !item.mobileHidden);

/** Whether `href` is the active route for `pathname` (exact for "/", prefix otherwise). */
export function isNavActive(pathname: string, href: string) {
  if (href === "/") return pathname === "/";
  return pathname === href || pathname.startsWith(`${href}/`);
}

/** Resolve the current page title from the active nav item. */
export function navTitle(pathname: string) {
  return NAV_ITEMS.find((item) => isNavActive(pathname, item.href))?.label ?? "App ERP";
}

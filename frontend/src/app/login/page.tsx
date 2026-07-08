import type { Metadata } from "next";

import { getT } from "@/lib/i18n/server";
import { LoginScreen } from "./login-screen";

export async function generateMetadata(): Promise<Metadata> {
  const t = await getT();
  return { title: t("login.metaTitle") };
}

export default function LoginPage() {
  return <LoginScreen />;
}

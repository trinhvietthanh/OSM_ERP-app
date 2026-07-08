"use client";

import { useMemo, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useForm } from "react-hook-form";
import { standardSchemaResolver } from "@hookform/resolvers/standard-schema";
import { z } from "zod";
import { useMutation } from "@tanstack/react-query";
import { toast } from "sonner";
import { ArrowRight, Eye, EyeOff } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { ApiError, login } from "@/lib/api";
import { useI18n } from "@/components/i18n-provider";

export function LoginForm() {
  const router = useRouter();
  const { t, locale } = useI18n();
  const [showPassword, setShowPassword] = useState(false);

  // Zod schema — single source of truth for validation + types. Built in-component
  // so the messages localize with the active locale.
  const schema = useMemo(
    () =>
      z.object({
        email: z.email(t("login.errors.email")),
        password: z.string().min(8, t("login.errors.password")),
      }),
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [locale],
  );
  type FormValues = z.infer<typeof schema>;

  const form = useForm<FormValues>({
    resolver: standardSchemaResolver(schema),
    defaultValues: { email: "", password: "" },
  });

  const mutation = useMutation({
    mutationFn: (values: FormValues) => login(values),
    onSuccess: () => {
      toast.success(t("login.toast.ok"));
      router.push("/");
    },
    onError: (error: Error) => {
      const message =
        error instanceof ApiError && error.status === 401
          ? t("login.toast.invalid")
          : error.message || t("login.toast.fail");
      toast.error(message);
    },
  });

  return (
    <Form {...form}>
      <form
        onSubmit={form.handleSubmit((values) => mutation.mutate(values))}
        className="space-y-4"
      >
        <FormField
          control={form.control}
          name="email"
          render={({ field }) => (
            <FormItem>
              <FormLabel>{t("login.email")}</FormLabel>
              <FormControl>
                <Input
                  type="email"
                  placeholder={t("login.emailPlaceholder")}
                  autoComplete="email"
                  {...field}
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="password"
          render={({ field }) => (
            <FormItem>
              <div className="flex items-center justify-between">
                <FormLabel>{t("login.password")}</FormLabel>
                <Link
                  href="#"
                  className="text-xs font-medium text-primary hover:underline"
                >
                  {t("login.forgot")}
                </Link>
              </div>
              <div className="relative">
                <FormControl>
                  <Input
                    type={showPassword ? "text" : "password"}
                    placeholder={t("login.passwordPlaceholder")}
                    autoComplete="current-password"
                    className="pr-9"
                    {...field}
                  />
                </FormControl>
                <button
                  type="button"
                  onClick={() => setShowPassword((show) => !show)}
                  aria-label={
                    showPassword ? t("login.hidePw") : t("login.showPw")
                  }
                  aria-pressed={showPassword}
                  className="absolute top-1/2 right-2 flex size-6 -translate-y-1/2 items-center justify-center rounded-md text-muted-foreground transition-colors hover:text-foreground"
                >
                  {showPassword ? (
                    <EyeOff className="size-4" aria-hidden />
                  ) : (
                    <Eye className="size-4" aria-hidden />
                  )}
                </button>
              </div>
              <FormMessage />
            </FormItem>
          )}
        />

        <div className="flex items-center gap-2">
          <input
            id="remember"
            type="checkbox"
            className="size-4 rounded border-input text-primary accent-primary"
          />
          <Label htmlFor="remember" className="text-sm text-muted-foreground">
            {t("login.remember")}
          </Label>
        </div>

        <Button
          type="submit"
          className="w-full gap-1.5"
          disabled={mutation.isPending}
        >
          {mutation.isPending ? t("login.submitting") : t("login.submit")}
          {!mutation.isPending && <ArrowRight aria-hidden />}
        </Button>
      </form>
    </Form>
  );
}

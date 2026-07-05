"use client";

import { useForm } from "react-hook-form";
import { standardSchemaResolver } from "@hookform/resolvers/standard-schema";
import { z } from "zod";
import { useMutation } from "@tanstack/react-query";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

// Zod schema — single source of truth for validation + types.
const schema = z.object({
  name: z.string().min(2, "Name must be at least 2 characters."),
  email: z.email("Enter a valid email address."),
});

type FormValues = z.infer<typeof schema>;

/**
 * Demonstrates the wired stack: shadcn/ui + Tailwind (UI),
 * React Hook Form + Zod (validation), TanStack Query (mutation),
 * and Sonner (toasts). Replace the mutationFn with a real apiFetch call.
 */
export function DemoForm() {
  const form = useForm<FormValues>({
    resolver: standardSchemaResolver(schema),
    defaultValues: { name: "", email: "" },
  });

  const mutation = useMutation({
    mutationFn: async (values: FormValues) => {
      // Stand-in for `apiFetch("/contacts", { method: "POST", ... })`.
      await new Promise((r) => setTimeout(r, 600));
      return values;
    },
    onSuccess: (values) => {
      toast.success(`Saved ${values.name}`);
      form.reset();
    },
    onError: (error: Error) => toast.error(error.message),
  });

  return (
    <Card>
      <CardHeader>
        <CardTitle>Stack demo</CardTitle>
        <CardDescription>
          shadcn/ui · Tailwind · TanStack Query · React Hook Form · Zod
        </CardDescription>
      </CardHeader>
      <CardContent>
        <Form {...form}>
          <form
            onSubmit={form.handleSubmit((v) => mutation.mutate(v))}
            className="space-y-6"
          >
            <FormField
              control={form.control}
              name="name"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Name</FormLabel>
                  <FormControl>
                    <Input placeholder="Ada Lovelace" {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="email"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Email</FormLabel>
                  <FormControl>
                    <Input placeholder="ada@example.com" {...field} />
                  </FormControl>
                  <FormDescription>We never share your email.</FormDescription>
                  <FormMessage />
                </FormItem>
              )}
            />
            <Button type="submit" disabled={mutation.isPending}>
              {mutation.isPending ? "Saving…" : "Submit"}
            </Button>
          </form>
        </Form>
      </CardContent>
    </Card>
  );
}

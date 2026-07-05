# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Warning: Non-standard Next.js

This project uses **Next.js 16** (with React 19), which has breaking changes from the versions in your training data. Before writing any Next.js code, read the relevant guide in `node_modules/next/dist/docs/`. Heed deprecation notices.

## Commands

```bash
pnpm dev          # Start dev server (Turbopack)
pnpm build        # Production build
pnpm lint         # ESLint (eslint.config.mjs)
```

There is no test suite yet.

### Adding UI components (shadcn)

```bash
pnpm dlx shadcn@latest add <component>
```

Components land in `src/components/ui/`. The project uses the `radix-nova` style with Tailwind v4 CSS variables (`src/app/globals.css`).

## Architecture

### Route structure

```
src/app/
  layout.tsx              # Root layout: fonts, PWA metadata, ServiceWorker, Providers, Toaster
  (app)/                  # Authenticated shell (route group, no URL segment)
    layout.tsx            # Responsive app shell: Sidebar (desktop) + AppBar + BottomNav (mobile)
    page.tsx              # / — Dashboard home
    orders/               # /orders — Order management
    profile/              # /profile
  login/                  # /login — outside the authenticated shell
```

The `(app)` route group wraps all authenticated pages. The layout renders a responsive two-column shell: a fixed `Sidebar` on `lg+` screens, and an `AppBar` + `BottomNav` on mobile. Navigation items are defined once in `src/lib/nav.ts` and consumed by all three layout components.

### Data layer

- **`src/lib/api.ts`** — Thin `apiFetch<T>` wrapper over the FastAPI backend (`NEXT_PUBLIC_API_BASE_URL`). Throws `ApiError` on non-2xx. Use this for all backend calls.
- **`src/lib/orders.ts`** — Domain types (`Order`, `OrderLine`, etc.), mock seed data, and pure helpers (`formatMoney`, `combineLines`, `nextOrderId`). The mock data mirrors the expected backend shape so swapping in `apiFetch` later is mechanical.
- **`src/components/providers.tsx`** — `QueryClientProvider` (TanStack Query v5). All data-fetching should go through `useQuery`/`useMutation`; `staleTime` is 60 s by default.

### Form pattern

Forms use **react-hook-form** + **Zod v4** + `@hookform/resolvers/standard-schema`. See `src/app/login/login-form.tsx` for the canonical pattern:

```ts
const schema = z.object({ ... });
type FormValues = z.infer<typeof schema>;
const form = useForm<FormValues>({ resolver: standardSchemaResolver(schema), ... });
```

Mutations wrap the submit handler in `useMutation`; success/error feedback goes through `sonner` toasts.

### PWA

The app is a Progressive Web App. `public/sw.js` is the service worker (registered only in production by `ServiceWorkerRegistration`). `src/app/manifest.ts` generates the web manifest. VAPID keys for Web Push are optional — see `.env.example`.

### Environment variables

| Variable | Default | Purpose |
|---|---|---|
| `NEXT_PUBLIC_API_BASE_URL` | `http://localhost:8000` | FastAPI backend base URL |
| `NEXT_PUBLIC_VAPID_PUBLIC_KEY` | — | Web Push (optional) |
| `VAPID_PRIVATE_KEY` | — | Web Push server-side (optional) |

### Path alias

`@/` maps to `src/`. All imports within `src/` should use this alias.

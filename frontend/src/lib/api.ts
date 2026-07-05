/**
 * Thin typed fetch wrapper around the backend API (../app FastAPI service).
 * Set NEXT_PUBLIC_API_BASE_URL in .env.local to point at the backend.
 *
 * Auth uses a JWT access token stored in localStorage and attached to every
 * request as `Authorization: Bearer <token>`. A 401 clears the token so the
 * next navigation prompts the user to sign in again.
 */

const BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "";

const TOKEN_KEY = "app_erp.access_token";

export class ApiError extends Error {
  constructor(
    public status: number,
    message: string,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

/* ----------------------------- auth token store ---------------------------- */

function readToken(): string | null {
  // localStorage is browser-only; return null during SSR / static rendering.
  if (typeof window === "undefined") return null;
  return window.localStorage.getItem(TOKEN_KEY);
}

export function getAccessToken(): string | null {
  return readToken();
}

export function setAccessToken(token: string): void {
  if (typeof window === "undefined") return;
  window.localStorage.setItem(TOKEN_KEY, token);
}

export function clearAccessToken(): void {
  if (typeof window === "undefined") return;
  window.localStorage.removeItem(TOKEN_KEY);
}

export function isAuthenticated(): boolean {
  return readToken() !== null;
}

/* --------------------------------- client --------------------------------- */

export async function apiFetch<T>(
  path: string,
  init?: RequestInit,
): Promise<T> {
  const headers = new Headers(init?.headers);
  if (init?.body && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }
  const token = readToken();
  if (token && !headers.has("Authorization")) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  const res = await fetch(`${BASE_URL}${path}`, { ...init, headers });

  // Token missing/expired — drop it so the caller can redirect to /login.
  if (res.status === 401) clearAccessToken();

  if (!res.ok) {
    const detail = await res.text().catch(() => res.statusText);
    throw new ApiError(res.status, detail || `Request failed: ${res.status}`);
  }

  if (res.status === 204) return undefined as T;
  return res.json() as Promise<T>;
}

/* ------------------------------- auth domain ------------------------------- */

export type LoginInput = { email: string; password: string };

export type TokenResponse = {
  access_token: string;
  token_type: string;
  expires_in: number;
};

export type User = {
  id: string;
  organization_id: string;
  email: string;
  username: string;
  role: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
};

/** POST /auth/login — exchange credentials for a JWT, then persist it. */
export async function login(payload: LoginInput): Promise<TokenResponse> {
  const token = await apiFetch<TokenResponse>("/auth/login", {
    method: "POST",
    body: JSON.stringify(payload),
  });
  setAccessToken(token.access_token);
  return token;
}

/** Clear any stored token (the JWT is stateless server-side). */
export function logout(): void {
  clearAccessToken();
}

/** GET /auth/me — the currently authenticated user (requires a stored token). */
export function fetchCurrentUser(): Promise<User> {
  return apiFetch<User>("/auth/me");
}

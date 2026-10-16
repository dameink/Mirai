import * as SecureStore from "expo-secure-store";
import { API_URL } from "../constants/api";

const SESSION_KEY = "mirai_session_v2";
const ACCESS_TOKEN_KEY = "mirai_access_token";
const REFRESH_TOKEN_KEY = "mirai_refresh_token";
let refreshInFlight: Promise<string | null> | null = null;
let sessionVersion = 0;
let credentialWrite: Promise<unknown> = Promise.resolve();
function writeCredentials<T>(action: () => Promise<T>): Promise<T> {
  const result = credentialWrite.then(action, action);
  credentialWrite = result.catch(() => {});
  return result;
}
const listeners = new Set<() => void>();

export function getSessionVersion() { return sessionVersion; }

export class AuthError extends Error {
  constructor(message: string, public readonly status: number) {
    super(message);
    this.name = "AuthError";
  }
}

export function onSessionExpired(listener: () => void) {
  listeners.add(listener);
  return () => { listeners.delete(listener); };
}

export async function saveTokens(accessToken: string, refreshToken: string, version = sessionVersion) {
  if (typeof accessToken !== "string" || !accessToken || typeof refreshToken !== "string" || !refreshToken) throw new Error("Invalid authentication response");
  return writeCredentials(async () => {
    if (version !== sessionVersion) return false;
    // One atomic entry prevents a killed app from restoring a mismatched token pair.
    await SecureStore.setItemAsync(SESSION_KEY, JSON.stringify({ accessToken, refreshToken }));
    await SecureStore.deleteItemAsync(ACCESS_TOKEN_KEY);
    await SecureStore.deleteItemAsync(REFRESH_TOKEN_KEY);
    return true;
  });
}

async function readTokens() {
  await credentialWrite;
  const saved = await SecureStore.getItemAsync(SESSION_KEY);
  if (saved) {
    try {
      const tokens = JSON.parse(saved);
      if (tokens && typeof tokens === "object") {
        return {
          accessToken: typeof tokens.accessToken === "string" && tokens.accessToken ? tokens.accessToken : null,
          refreshToken: typeof tokens.refreshToken === "string" && tokens.refreshToken ? tokens.refreshToken : null,
        };
      }
    } catch { /* A damaged local record must not trap the app in startup retries. */ }
    return { accessToken: null, refreshToken: null };
  }
  // Read older APK credentials until the next successful login/refresh migrates them.
  return { accessToken: await SecureStore.getItemAsync(ACCESS_TOKEN_KEY), refreshToken: await SecureStore.getItemAsync(REFRESH_TOKEN_KEY) };
}

export async function getAccessToken() { return (await readTokens()).accessToken; }
export async function getRefreshToken() { return (await readTokens()).refreshToken; }

export async function clearTokens() {
  sessionVersion += 1;
  listeners.forEach((listener) => listener());
  await writeCredentials(async () => {
    await SecureStore.deleteItemAsync(SESSION_KEY);
    await SecureStore.deleteItemAsync(ACCESS_TOKEN_KEY);
    await SecureStore.deleteItemAsync(REFRESH_TOKEN_KEY);
  });
}

export async function apiFetch(endpoint: string, options: RequestInit = {}) {
  const controller = new AbortController();
  const abort = () => controller.abort();
  options.signal?.addEventListener("abort", abort);
  if (options.signal?.aborted) controller.abort();
  const timer = setTimeout(abort, 90000);
  try {
    return await fetch(`${API_URL}${endpoint}`, { ...options, signal: controller.signal });
  } finally {
    clearTimeout(timer);
    options.signal?.removeEventListener("abort", abort);
  }
}

async function authRequest(endpoint: string, body: object) {
  const response = await apiFetch(endpoint, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  let data;
  try { data = await response.json(); }
  catch { throw new AuthError("Server is temporarily unavailable. Please try again.", response.status); }
  if (!response.ok) {
    const detail = data.detail;
    throw new AuthError(typeof detail === "string" ? detail : "Please check your email and password.", response.status);
  }
  return data;
}

export async function login(email: string, password: string) {
  const version = ++sessionVersion;
  const data = await authRequest("/auth/login", { email, password });
  if (version !== sessionVersion) throw new AuthError("Sign-in was cancelled. Please try again.", 409);
  const saved = await saveTokens(data.access_token, data.refresh_token, version);
  if (!saved || version !== sessionVersion) throw new AuthError("Sign-in was cancelled. Please try again.", 409);
  return data;
}

export async function register(email: string, password: string): Promise<{ message: string }> {
  return authRequest("/auth/register", { email, password });
}

export async function logout() {
  const refreshToken = await getRefreshToken();
  // Invalidate local credentials even when the device is offline.
  await clearTokens();
  if (refreshToken) {
    try { await authRequest("/auth/logout", { refresh_token: refreshToken }); }
    catch { /* Local logout is complete; the server token retains its expiry. */ }
  }
}

async function refreshAccessToken() {
  if (!refreshInFlight) {
    const version = sessionVersion;
    refreshInFlight = (async () => {
      const token = await getRefreshToken();
      if (version !== sessionVersion) return null;
      if (!token) {
        if (version === sessionVersion) await clearTokens();
        return null;
      }
      const response = await apiFetch("/auth/refresh", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ refresh_token: token }),
      });
      if (version !== sessionVersion) return null;
      if (response.status === 401 || response.status === 403) {
        await clearTokens();
        return null;
      }
      if (!response.ok) throw new Error("Session refresh is temporarily unavailable");
      const data = await response.json();
      if (version !== sessionVersion) return null;
      const saved = await saveTokens(data.access_token, data.refresh_token, version);
      return saved ? data.access_token as string : null;
    })().finally(() => { refreshInFlight = null; });
  }
  return refreshInFlight;
}

export async function authFetch(endpoint: string, options: RequestInit = {}) {
  const version = sessionVersion;
  const requireCurrentSession = () => {
    if (version !== sessionVersion) throw new AuthError("Request cancelled because the signed-in account changed.", 409);
  };
  let token = await getAccessToken();
  requireCurrentSession();
  if (!token) {
    const refresh = await getRefreshToken();
    requireCurrentSession();
    if (refresh) token = await refreshAccessToken();
  }
  const send = (accessToken: string | null) => {
    requireCurrentSession();
    const headers = new Headers(options.headers);
    headers.set("Content-Type", "application/json");
    if (accessToken) headers.set("Authorization", `Bearer ${accessToken}`);
    return apiFetch(endpoint, { ...options, headers });
  };
  const response = await send(token);
  if (response.status !== 401 || version !== sessionVersion) return response;
  // Another request may already have rotated the token while this one was running.
  const latest = await getAccessToken();
  if (version !== sessionVersion) return response;
  const refreshed = latest && latest !== token ? latest : await refreshAccessToken();
  if (!refreshed || version !== sessionVersion) return response;
  const retried = await send(refreshed);
  if (retried.status === 401 && version === sessionVersion) await clearTokens();
  return retried;
}

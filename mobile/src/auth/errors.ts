export class RequestError extends Error {
  constructor(message: string, public readonly status: number, public readonly code?: string) {
    super(message);
    this.name = "RequestError";
  }
}

export async function throwResponseError(response: Response): Promise<never> {
  let code: string | undefined;
  try { code = (await response.json()).code; } catch { /* Gateways can return HTML. */ }
  throw new RequestError("Request failed", response.status, code);
}

export function requestErrorMessage(error: unknown): string {
  const status = error instanceof RequestError ? error.status : undefined;
  if (status === 401 || status === 403) return "Your session has expired. Please sign in again.";
  if (status === 429 || (error instanceof RequestError && error.code === "model_rate_limited")) {
    return "Mirai's AI service has reached its request limit. Please try again later.";
  }
  if (status && status >= 500) return "Mirai's service is temporarily unavailable. Your message is saved; please retry shortly.";
  if (error instanceof Error && error.name === "AbortError") return "The server took too long to respond. Your message is saved; please retry.";
  return "Could not reach Mirai. Check your connection and try again.";
}

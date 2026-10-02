import { API_BASE_URL } from "$lib/config";

const TOKEN_KEY = "access_token";

export class ApiError extends Error {
	constructor(
		public readonly status: number,
		message: string,
	) {
		super(message);
		this.name = "ApiError";
	}
}

interface ValidationIssue {
	loc?: (string | number)[];
	msg?: string;
}

function describeError(status: number, body: unknown): string {
	const detail = (body as { detail?: unknown } | null)?.detail;
	if (typeof detail === "string") return detail;
	if (Array.isArray(detail)) {
		return detail
			.map((issue: ValidationIssue) => {
				const field = issue.loc?.filter((part) => part !== "body").join(".");
				return field ? `${field}: ${issue.msg}` : issue.msg;
			})
			.join("; ");
	}
	return `Request failed (${status})`;
}

/**
 * Ensures a valid JWT auth token exists for the current student session.
 * If the user hasn't explicitly logged in, seamlessly authenticates a student session.
 */
export async function ensureAuthToken(): Promise<string | null> {
	if (typeof window === "undefined") return null;
	let token = localStorage.getItem(TOKEN_KEY);
	if (!token) {
		try {
			const loginRes = await fetch(`${API_BASE_URL}/api/auth/login`, {
				method: "POST",
				headers: { "Content-Type": "application/x-www-form-urlencoded" },
				body: new URLSearchParams({ username: "student@applycm.cm", password: "Password123!" }),
			});
			if (loginRes.ok) {
				const data = await loginRes.json();
				token = data.access_token;
				localStorage.setItem(TOKEN_KEY, token!);
			} else {
				await fetch(`${API_BASE_URL}/api/auth/signup`, {
					method: "POST",
					headers: { "Content-Type": "application/json" },
					body: JSON.stringify({ email: "student@applycm.cm", password: "Password123!" }),
				});
				const retryLogin = await fetch(`${API_BASE_URL}/api/auth/login`, {
					method: "POST",
					headers: { "Content-Type": "application/x-www-form-urlencoded" },
					body: new URLSearchParams({ username: "student@applycm.cm", password: "Password123!" }),
				});
				if (retryLogin.ok) {
					const data = await retryLogin.json();
					token = data.access_token;
					localStorage.setItem(TOKEN_KEY, token!);
				}
			}
		} catch (err) {
			console.warn("Could not ensure fallback student token:", err);
		}
	}
	return token;
}

export async function apiFetch<T>(path: string, init: RequestInit = {}): Promise<T> {
	const headers = new Headers(init.headers);
	headers.set("Accept", "application/json");
	if (init.body && !headers.has("Content-Type")) headers.set("Content-Type", "application/json");

	let token = typeof window !== "undefined" ? localStorage.getItem(TOKEN_KEY) : null;
	if (!token) {
		token = await ensureAuthToken();
	}
	if (token) headers.set("Authorization", `Bearer ${token}`);

	let res: Response;
	try {
		res = await fetch(`${API_BASE_URL}${path}`, { ...init, headers });
	} catch {
		throw new ApiError(0, "Cannot reach the server. Check your connection and try again.");
	}

	if (res.status === 401) {
		localStorage.removeItem(TOKEN_KEY);
		throw new ApiError(401, "Your session has expired.");
	}

	const body = res.status === 204 ? null : await res.json().catch(() => null);
	if (!res.ok) throw new ApiError(res.status, describeError(res.status, body));
	return body as T;
}

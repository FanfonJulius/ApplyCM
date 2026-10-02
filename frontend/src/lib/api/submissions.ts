import { API_BASE_URL } from "$lib/config";
import { ApiError, apiFetch, ensureAuthToken } from "./client";
import type { ProfileSection } from "./profile";

export type SubmissionStatus = "sending" | "sent" | "failed";
export type SubmitOutcome = "sent" | "failed" | "already_sent" | "in_progress";

export interface Submission {
	school_id: string;
	school_name: string;
	status: SubmissionStatus;
	recipient_email: string;
	error: string | null;
	sent_at: string | null;
	updated_at: string | null;
}

export interface SubmitResult {
	school_id: string;
	school_name: string;
	status: SubmitOutcome;
	error: string | null;
}

export interface SubmitResponse {
	results: SubmitResult[];
	sent_count: number;
	student_copy_sent: boolean;
}

/** Wizard sections a student must finish before submitting (testing is optional). */
export const REQUIRED_SECTIONS: { id: ProfileSection; label: string }[] = [
	{ id: "profile", label: "Profile" },
	{ id: "contact", label: "Contact" },
	{ id: "education", label: "Education" },
	{ id: "activities", label: "Activities" },
	{ id: "writing", label: "Writing" },
];

export function fetchSubmissions(): Promise<Submission[]> {
	return apiFetch<Submission[]>("/api/submissions");
}

export function submitApplication(schoolIds: string[]): Promise<SubmitResponse> {
	return apiFetch<SubmitResponse>("/api/submissions", {
		method: "POST",
		body: JSON.stringify({ school_ids: schoolIds }),
	});
}

/** Downloads the student's application PDF as a Blob (the route needs the auth header). */
export async function fetchApplicationPdf(): Promise<Blob> {
	const token = await ensureAuthToken();
	let res: Response;
	try {
		res = await fetch(`${API_BASE_URL}/api/students/me/application.pdf`, {
			headers: token ? { Authorization: `Bearer ${token}` } : {},
		});
	} catch {
		throw new ApiError(0, "Cannot reach the server. Check your connection and try again.");
	}
	if (!res.ok) {
		const body = await res.json().catch(() => null);
		const detail = (body as { detail?: unknown } | null)?.detail;
		throw new ApiError(res.status, typeof detail === "string" ? detail : `Could not generate the PDF (${res.status})`);
	}
	return res.blob();
}

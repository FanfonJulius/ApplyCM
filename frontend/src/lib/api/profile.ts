import { ApiError, apiFetch } from "./client";

export type ProfileSection = "profile" | "contact" | "education" | "testing" | "activities" | "writing";

export interface StudentProfile {
	id: string;
	user_id: string;
	full_name: string | null;
	phone: string | null;
	first_name: string | null;
	last_name: string | null;
	email: string | null;
	declared_state: string | null;
	address: string | null;
	city: string | null;
	region: string | null;
	emergency_contact_name: string | null;
	emergency_contact_phone: string | null;
	secondary_school: string | null;
	o_level_slip_url: string | null;
	a_level_slip_url: string | null;
	o_level_passes: string | null;
	a_level_points: string | null;
	english_test_type: string | null;
	english_test_score: string | null;
	activity_name: string | null;
	activity_role: string | null;
	activity_description: string | null;
	honors_awards: string | null;
	essay_prompt: string | null;
	writing_sample: string | null;
	additional_info: string | null;
	created_at: string | null;
	updated_at: string | null;
	completed_sections: ProfileSection[];
}

/** Returns the signed-in student's profile, or null if nothing has been saved yet. */
export async function fetchMyProfile(): Promise<StudentProfile | null> {
	try {
		return await apiFetch<StudentProfile>("/api/students/me");
	} catch (err) {
		if (err instanceof ApiError && err.status === 404) return null;
		throw err;
	}
}

export function saveProfileSection(section: ProfileSection, data: Record<string, string>): Promise<StudentProfile> {
	return apiFetch<StudentProfile>(`/api/students/me/${section}`, {
		method: "PUT",
		body: JSON.stringify(data),
	});
}

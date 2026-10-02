import {
	fetchMyProfile,
	saveProfileSection,
	type ProfileSection,
	type StudentProfile,
} from "$lib/api/profile";

export const profileState = $state<{
	profile: StudentProfile | null;
	loaded: boolean;
	error: string | null;
}>({ profile: null, loaded: false, error: null });

let inflight: Promise<StudentProfile | null> | null = null;

/** Loads the profile once and shares it across the wizard, layout and dashboard. */
export function loadProfile(): Promise<StudentProfile | null> {
	if (profileState.loaded) return Promise.resolve(profileState.profile);
	inflight ??= fetchMyProfile()
		.then((profile) => {
			profileState.profile = profile;
			profileState.loaded = true;
			profileState.error = null;
			return profile;
		})
		.catch((err: unknown) => {
			profileState.error = err instanceof Error ? err.message : "Could not load your saved profile.";
			return null;
		})
		.finally(() => {
			inflight = null;
		});
	return inflight;
}

export async function saveSection(section: ProfileSection, data: Record<string, string>): Promise<StudentProfile> {
	const profile = await saveProfileSection(section, data);
	profileState.profile = profile;
	profileState.loaded = true;
	profileState.error = null;
	return profile;
}

export function isSectionComplete(section: ProfileSection): boolean {
	return profileState.profile?.completed_sections.includes(section) ?? false;
}

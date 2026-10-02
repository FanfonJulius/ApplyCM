import pytest

PROFILE = {
    "first_name": "Ngwa",
    "last_name": "Berinyuy",
    "email": "ngwa@example.com",
    "phone": "+237 6 70 00 00 00",
    "declared_state": "Northwest",
}
CONTACT = {
    "address": "Mile 4 Nkwen",
    "city": "Bamenda",
    "region": "Northwest",
    "emergency_contact_name": "Mama Berinyuy",
    "emergency_contact_phone": "+237670000001",
}
EDUCATION = {
    "secondary_school": "GBHS Bamenda",
    "o_level_slip_url": "https://files.example.com/o.png",
    "a_level_slip_url": "https://files.example.com/a.png",
}
TESTING = {"o_level_passes": "9 Passes", "a_level_points": "15 Points", "english_test_type": "", "english_test_score": ""}
ACTIVITIES = {
    "activity_name": "Debate Club",
    "activity_role": "President",
    "activity_description": "Led weekly debates.",
    "honors_awards": "",
}
WRITING = {"essay_prompt": "Personal Statement", "writing_sample": "I want to study medicine.", "additional_info": ""}

ALL_SECTIONS = {
    "profile": PROFILE,
    "contact": CONTACT,
    "education": EDUCATION,
    "testing": TESTING,
    "activities": ACTIVITIES,
    "writing": WRITING,
}


def test_section_endpoints_require_authentication(client):
    for section, payload in ALL_SECTIONS.items():
        assert client.put(f"/api/students/me/{section}", json=payload).status_code == 401


def test_get_profile_returns_404_before_first_save(client, auth):
    assert client.get("/api/students/me", headers=auth).status_code == 404


def test_any_section_can_be_saved_first_and_creates_the_profile(client, auth):
    res = client.put("/api/students/me/contact", json=CONTACT, headers=auth)

    assert res.status_code == 200
    body = res.json()
    assert body["city"] == "Bamenda"
    assert body["full_name"] is None
    assert body["completed_sections"] == ["contact"]


def test_profile_section_sets_full_name_and_updates_in_place(client, auth):
    first = client.put("/api/students/me/profile", json=PROFILE, headers=auth).json()
    second = client.put("/api/students/me/profile", json={**PROFILE, "first_name": "Julius"}, headers=auth).json()

    assert first["full_name"] == "Ngwa Berinyuy"
    assert second["full_name"] == "Julius Berinyuy"
    assert second["id"] == first["id"]
    assert second["phone"] == PROFILE["phone"]


def test_saving_one_section_keeps_the_others(client, auth):
    client.put("/api/students/me/profile", json=PROFILE, headers=auth)
    client.put("/api/students/me/education", json=EDUCATION, headers=auth)

    body = client.get("/api/students/me", headers=auth).json()
    assert body["first_name"] == "Ngwa"
    assert body["secondary_school"] == "GBHS Bamenda"
    assert body["completed_sections"] == ["profile", "education"]


def test_all_sections_saved_marks_every_section_complete(client, auth):
    for section, payload in ALL_SECTIONS.items():
        assert client.put(f"/api/students/me/{section}", json=payload, headers=auth).status_code == 200

    body = client.get("/api/students/me", headers=auth).json()
    assert body["completed_sections"] == list(ALL_SECTIONS)
    assert body["writing_sample"] == "I want to study medicine."


def test_blank_optional_fields_are_stored_as_null(client, auth):
    body = client.put("/api/students/me/testing", json=TESTING, headers=auth).json()

    assert body["english_test_type"] is None
    assert body["english_test_score"] is None
    assert "testing" in body["completed_sections"]


@pytest.mark.parametrize(
    "section,payload",
    [
        ("profile", {**PROFILE, "declared_state": "Paris"}),
        ("profile", {**PROFILE, "email": "not-an-email"}),
        ("profile", {**PROFILE, "phone": "call me"}),
        ("profile", {**PROFILE, "first_name": "   "}),
        ("contact", {k: v for k, v in CONTACT.items() if k != "city"}),
        ("testing", {**TESTING, "english_test_type": "SAT"}),
        ("writing", {**WRITING, "essay_prompt": "Anything"}),
    ],
)
def test_invalid_section_payloads_are_rejected(client, auth, section, payload):
    assert client.put(f"/api/students/me/{section}", json=payload, headers=auth).status_code == 422


def test_client_cannot_choose_the_profile_owner(client, auth, make_auth):
    victim = make_auth("victim@example.com")
    victim_profile = client.put("/api/students/me/profile", json=PROFILE, headers=victim).json()

    res = client.put(
        "/api/students/me/contact", json={**CONTACT, "user_id": victim_profile["user_id"]}, headers=auth
    )

    assert res.status_code == 422
    assert client.get("/api/students/me", headers=victim).json()["address"] is None


def test_profiles_are_isolated_per_account(client, auth, make_auth):
    other = make_auth("other@example.com")
    client.put("/api/students/me/profile", json=PROFILE, headers=auth)

    assert client.get("/api/students/me", headers=other).status_code == 404

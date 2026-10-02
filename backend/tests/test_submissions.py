import pytest

from app.core.config import settings
from app.db.database import SessionLocal
from app.models.school import School
from app.services import email_service, submission_service
from tests.test_application_profile import ALL_SECTIONS, PROFILE


@pytest.fixture
def outbox(monkeypatch):
    sent = []

    def fake_send(message):
        if any("fail.example" in address for address in message.to):
            raise email_service.EmailSendError("Email provider rejected the message (400): bad recipient")
        sent.append(message)

    monkeypatch.setattr(submission_service, "send_email", fake_send)
    return sent


def _school(name: str, email: str | None = "admissions@school.example") -> str:
    with SessionLocal() as db:
        school = School(name=name, contact_email=email)
        db.add(school)
        db.commit()
        return str(school.id)


def _complete_profile(client, auth, skip=()):
    for section, payload in ALL_SECTIONS.items():
        if section not in skip:
            assert client.put(f"/api/students/me/{section}", json=payload, headers=auth).status_code == 200


def _favorite(client, auth, school_id):
    assert client.post("/api/favorites", json={"school_id": school_id}, headers=auth).status_code == 200


def _submit(client, auth, school_ids):
    return client.post("/api/submissions", json={"school_ids": school_ids}, headers=auth)


def test_submission_routes_require_authentication(client):
    assert client.get("/api/submissions").status_code == 401
    assert client.post("/api/submissions", json={"school_ids": []}).status_code == 401
    assert client.get("/api/students/me/application.pdf").status_code == 401


def test_pdf_download_returns_a_pdf_of_the_profile(client, auth):
    _complete_profile(client, auth)

    res = client.get("/api/students/me/application.pdf", headers=auth)

    assert res.status_code == 200
    assert res.headers["content-type"] == "application/pdf"
    assert res.content.startswith(b"%PDF")
    assert 'filename="ApplyCM_Application_Ngwa_Berinyuy.pdf"' in res.headers["content-disposition"]


def test_pdf_download_404_without_profile(client, auth):
    assert client.get("/api/students/me/application.pdf", headers=auth).status_code == 404


def test_submit_emails_pdf_to_each_school_and_a_copy_to_the_student(client, auth, outbox):
    _complete_profile(client, auth)
    ict = _school("ICT University", "admissions@ict.example")
    mist = _school("MIST", "info@mist.example")
    _favorite(client, auth, ict)
    _favorite(client, auth, mist)

    res = _submit(client, auth, [ict, mist])

    assert res.status_code == 200
    body = res.json()
    assert body["sent_count"] == 2
    assert body["student_copy_sent"] is True
    assert [r["status"] for r in body["results"]] == ["sent", "sent"]

    school_mail, other_school_mail, student_mail = outbox
    assert school_mail.to == ["admissions@ict.example"]
    assert other_school_mail.to == ["info@mist.example"]
    assert school_mail.reply_to == PROFILE["email"]
    assert "Ngwa Berinyuy" in school_mail.subject
    attachment = school_mail.attachments[0]
    assert attachment.filename.endswith(".pdf") and attachment.content.startswith(b"%PDF")

    assert set(student_mail.to) == {"student@example.com", PROFILE["email"]}
    assert "ICT University" in student_mail.text and "MIST" in student_mail.text
    assert student_mail.attachments[0].content == attachment.content

    listed = client.get("/api/submissions", headers=auth).json()
    assert {(s["school_name"], s["status"]) for s in listed} == {("ICT University", "sent"), ("MIST", "sent")}
    assert all(s["sent_at"] for s in listed)


def test_incomplete_profile_cannot_be_submitted(client, auth, outbox):
    _complete_profile(client, auth, skip=("writing", "contact"))
    school = _school("ICT University")
    _favorite(client, auth, school)

    res = _submit(client, auth, [school])

    assert res.status_code == 400
    assert "Contact" in res.json()["detail"] and "Writing" in res.json()["detail"]
    assert outbox == []


def test_testing_section_is_optional_for_submission(client, auth, outbox):
    _complete_profile(client, auth, skip=("testing",))
    school = _school("ICT University")
    _favorite(client, auth, school)

    assert _submit(client, auth, [school]).json()["sent_count"] == 1


def test_only_favorited_schools_can_be_submitted_to(client, auth, outbox):
    _complete_profile(client, auth)
    favorite = _school("ICT University")
    not_favorite = _school("Polytech")
    _favorite(client, auth, favorite)

    res = _submit(client, auth, [favorite, not_favorite])

    assert res.status_code == 400
    assert outbox == []


def test_resubmitting_skips_schools_already_sent(client, auth, outbox):
    _complete_profile(client, auth)
    school = _school("ICT University")
    _favorite(client, auth, school)
    _submit(client, auth, [school])
    outbox.clear()

    res = _submit(client, auth, [school, school]).json()

    assert res["results"] == [{"school_id": school, "school_name": "ICT University", "status": "already_sent", "error": None}]
    assert res["sent_count"] == 0
    assert res["student_copy_sent"] is False
    assert outbox == []


def test_failed_send_is_reported_and_can_be_retried(client, auth, outbox):
    _complete_profile(client, auth)
    good = _school("ICT University", "admissions@ict.example")
    bad = _school("MIST", "admissions@fail.example")
    no_email = _school("IUSTY", None)
    for school in (good, bad, no_email):
        _favorite(client, auth, school)

    body = _submit(client, auth, [good, bad, no_email]).json()

    statuses = {r["school_name"]: (r["status"], r["error"]) for r in body["results"]}
    assert statuses["ICT University"] == ("sent", None)
    assert statuses["MIST"][0] == "failed" and "bad recipient" in statuses["MIST"][1]
    assert statuses["IUSTY"][0] == "failed" and "no admissions email" in statuses["IUSTY"][1]
    assert body["sent_count"] == 1
    assert "MIST" not in outbox[-1].text  # student copy lists only delivered schools

    with SessionLocal() as db:
        db.query(School).filter(School.name == "MIST").update({"contact_email": "admissions@mist.example"})
        db.commit()
    retry = _submit(client, auth, [bad]).json()
    assert retry["results"][0]["status"] == "sent"


def test_submissions_are_isolated_per_account(client, auth, make_auth, outbox):
    _complete_profile(client, auth)
    school = _school("ICT University")
    _favorite(client, auth, school)
    _submit(client, auth, [school])

    other = make_auth("other@example.com")
    assert client.get("/api/submissions", headers=other).json() == []


@pytest.mark.parametrize("payload", [{"school_ids": []}, {"school_ids": ["not-a-uuid"]}, {"school_ids": [], "student_id": "x"}])
def test_invalid_submit_payloads_are_rejected(client, auth, payload):
    assert client.post("/api/submissions", json=payload, headers=auth).status_code == 422


def test_submit_refused_when_email_is_not_configured(client, auth, outbox, monkeypatch):
    monkeypatch.setattr(settings, "EMAIL_BACKEND", "brevo")
    monkeypatch.setattr(settings, "BREVO_API_KEY", None)
    _complete_profile(client, auth)
    school = _school("ICT University")
    _favorite(client, auth, school)

    res = _submit(client, auth, [school])

    assert res.status_code == 503
    assert "BREVO" not in res.json()["detail"]
    assert client.get("/api/submissions", headers=auth).json() == []


def test_pdf_escapes_markup_in_user_text(client, auth):
    _complete_profile(client, auth)
    hostile = {**ALL_SECTIONS["writing"], "writing_sample": "<b>bold</b> & <link href='x'>unclosed"}
    client.put("/api/students/me/writing", json=hostile, headers=auth)

    assert client.get("/api/students/me/application.pdf", headers=auth).status_code == 200


# --- email_service ---------------------------------------------------------

def _message(**overrides):
    fields = dict(to=["school@example.com"], subject="Hello", html="<p>Hi</p>", text="Hi",
                  reply_to="student@example.com",
                  attachments=[email_service.Attachment("a.pdf", b"%PDF-1.4")])
    fields.update(overrides)
    return email_service.EmailMessage(**fields)


class _FakeResponse:
    def __init__(self, status_code, body=None):
        self.status_code = status_code
        self._body = body or {}
        self.text = str(self._body)

    def json(self):
        return self._body


def _use_brevo(monkeypatch, response):
    calls = []
    monkeypatch.setattr(settings, "EMAIL_BACKEND", "brevo")
    monkeypatch.setattr(settings, "BREVO_API_KEY", "test-key")
    monkeypatch.setattr(settings, "EMAIL_FROM_ADDRESS", "noreply@applycm.example")
    monkeypatch.setattr(email_service.httpx, "post", lambda url, **kw: calls.append((url, kw)) or response)
    return calls


def test_brevo_payload_includes_sender_reply_to_and_base64_pdf(monkeypatch):
    calls = _use_brevo(monkeypatch, _FakeResponse(201, {"messageId": "1"}))

    email_service.send_email(_message())

    url, kwargs = calls[0]
    assert url == email_service.BREVO_SEND_URL
    assert kwargs["headers"]["api-key"] == "test-key"
    body = kwargs["json"]
    assert body["sender"] == {"name": "ApplyCM", "email": "noreply@applycm.example"}
    assert body["to"] == [{"email": "school@example.com"}]
    assert body["replyTo"] == {"email": "student@example.com"}
    assert body["attachment"] == [{"name": "a.pdf", "content": "JVBERi0xLjQ="}]


def test_brevo_error_raises_email_send_error(monkeypatch):
    _use_brevo(monkeypatch, _FakeResponse(400, {"message": "sender not verified"}))

    with pytest.raises(email_service.EmailSendError, match="sender not verified"):
        email_service.send_email(_message())


def test_redirect_sends_to_test_inbox_and_names_real_recipient(monkeypatch):
    calls = _use_brevo(monkeypatch, _FakeResponse(201))
    monkeypatch.setattr(settings, "EMAIL_REDIRECT_TO", "me@example.com")

    email_service.send_email(_message())

    body = calls[0][1]["json"]
    assert body["to"] == [{"email": "me@example.com"}]
    assert body["subject"] == "[TEST - for school@example.com] Hello"

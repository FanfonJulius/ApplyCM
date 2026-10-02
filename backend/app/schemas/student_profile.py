import re
from datetime import datetime
from typing import Annotated, Dict, List, Literal, Optional, Type
from uuid import UUID

from pydantic import AfterValidator, BaseModel, BeforeValidator, ConfigDict, EmailStr, Field, StringConstraints, computed_field
from pydantic_core import PydanticCustomError

CameroonRegion = Literal[
    "Adamawa", "Centre", "East", "Far North", "Littoral",
    "North", "Northwest", "South", "Southwest", "West",
]
EnglishTestType = Literal["IELTS", "TOEFL", "Duolingo", "GCE_English"]
EssayPrompt = Literal["Personal Statement", "Challenge Overcome", "Community Impact", "Open Prompt"]


def _blank_to_none(value: object) -> object:
    if isinstance(value, str) and not value.strip():
        return None
    return value


def _text(max_length: int) -> StringConstraints:
    return StringConstraints(strip_whitespace=True, min_length=1, max_length=max_length)


Text100 = Annotated[str, _text(100)]
Text200 = Annotated[str, _text(200)]
Text255 = Annotated[str, _text(255)]
Text2048 = Annotated[str, _text(2048)]
Text5000 = Annotated[str, _text(5000)]
Text20000 = Annotated[str, _text(20000)]
OptionalText100 = Annotated[Optional[Text100], BeforeValidator(_blank_to_none)]
OptionalText2000 = Annotated[Optional[Annotated[str, _text(2000)]], BeforeValidator(_blank_to_none)]
OptionalText5000 = Annotated[Optional[Text5000], BeforeValidator(_blank_to_none)]


_PHONE_RE = re.compile(r"^\+?[0-9\s\-()]{6,32}$")


def _check_phone(value: str) -> str:
    if not _PHONE_RE.fullmatch(value):
        raise PydanticCustomError("phone_number", "Enter a valid phone number, e.g. +237 6XX XX XX XX")
    return value


Phone = Annotated[str, StringConstraints(strip_whitespace=True), AfterValidator(_check_phone)]


class StudentProfileBase(BaseModel):
    full_name: str
    phone: Optional[str] = None
    education_summary: Optional[str] = None
    writing_sample: Optional[str] = None


class StudentProfileCreate(StudentProfileBase):
    user_id: UUID


class StudentProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    education_summary: Optional[str] = None
    writing_sample: Optional[str] = None


# --- Application profile wizard sections -------------------------------------
# Fields without a default are required: a section counts as complete once all
# of its required fields are stored.

class _Section(BaseModel):
    model_config = ConfigDict(extra="forbid")


class ProfileSection(_Section):
    first_name: Text100
    last_name: Text100
    email: EmailStr
    phone: Phone
    declared_state: CameroonRegion


class ContactSection(_Section):
    address: Text255
    city: Text100
    region: CameroonRegion
    emergency_contact_name: Text200
    emergency_contact_phone: Phone


class EducationSection(_Section):
    secondary_school: Text255
    o_level_slip_url: Text2048
    a_level_slip_url: Text2048


class TestingSection(_Section):
    o_level_passes: Text255
    a_level_points: Text255
    english_test_type: Annotated[Optional[EnglishTestType], BeforeValidator(_blank_to_none)] = None
    english_test_score: OptionalText100 = None


class ActivitiesSection(_Section):
    activity_name: Text200
    activity_role: Text200
    activity_description: Text5000
    honors_awards: OptionalText2000 = None


class WritingSection(_Section):
    essay_prompt: EssayPrompt
    writing_sample: Text20000 = Field(description="The personal statement / essay text.")
    additional_info: OptionalText5000 = None


SECTION_SCHEMAS: Dict[str, Type[_Section]] = {
    "profile": ProfileSection,
    "contact": ContactSection,
    "education": EducationSection,
    "testing": TestingSection,
    "activities": ActivitiesSection,
    "writing": WritingSection,
}

SECTION_REQUIRED_FIELDS: Dict[str, List[str]] = {
    section: [name for name, field in schema.model_fields.items() if field.is_required()]
    for section, schema in SECTION_SCHEMAS.items()
}


class StudentProfile(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    full_name: Optional[str] = None
    phone: Optional[str] = None
    education_summary: Optional[str] = None
    writing_sample: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    declared_state: Optional[str] = None

    address: Optional[str] = None
    city: Optional[str] = None
    region: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None

    secondary_school: Optional[str] = None
    o_level_slip_url: Optional[str] = None
    a_level_slip_url: Optional[str] = None

    o_level_passes: Optional[str] = None
    a_level_points: Optional[str] = None
    english_test_type: Optional[str] = None
    english_test_score: Optional[str] = None

    activity_name: Optional[str] = None
    activity_role: Optional[str] = None
    activity_description: Optional[str] = None
    honors_awards: Optional[str] = None

    essay_prompt: Optional[str] = None
    additional_info: Optional[str] = None

    @computed_field
    @property
    def completed_sections(self) -> List[str]:
        return [
            section
            for section, fields in SECTION_REQUIRED_FIELDS.items()
            if all(getattr(self, name) not in (None, "") for name in fields)
        ]


class ApplicationSectionStatus(BaseModel):
    key: str
    label: str
    href: str
    complete: bool


class DashboardSummaryResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    firstName: str = ""
    first_name: Optional[str] = None
    applicationSections: List[ApplicationSectionStatus] = Field(default_factory=list)
    application_sections: Optional[List[ApplicationSectionStatus]] = None
    overallProgress: int = 0
    overall_progress: Optional[int] = None
    universitiesOnList: int = 0
    universities_on_list: Optional[int] = None
    universitiesInProgress: int = 0
    universities_in_progress: Optional[int] = None
    favoritedUniversities: int = 0
    favorited_universities: Optional[int] = None
    requiredDocumentsOutstanding: int = 0
    required_documents_outstanding: Optional[int] = None


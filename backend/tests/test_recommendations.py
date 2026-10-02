"""
Tests for ApplyCM AI Career Recommender.
Tests metadata endpoint, field mappings, tuition parsing, ML recommendation,
budget filtering, and validation error handling.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.ml.field_mapping import map_program_to_fields
from app.services.recommendation_service import parse_tuition_fee

client = TestClient(app)


def test_get_questionnaire_meta():
    """Verify GET /api/recommendations/questions returns all 12 questions and choices."""
    response = client.get("/api/recommendations/questions")
    assert response.status_code == 200
    data = response.json()

    assert "questions" in data
    assert len(data["questions"]) == 12
    assert "series_options" in data
    assert "Science" in data["series_options"]
    assert "subject_options" in data
    assert "Maths" in data["subject_options"]
    assert data["currency"] == "FCFA"


def test_field_mapping():
    """Verify taxonomy mapping correctly maps exact and cross-disciplinary programs."""
    # Exact mapping
    se_fields = map_program_to_fields("Software Engineering")
    assert "Computing & IT" in se_fields

    # Cross-disciplinary mapping
    bio_fields = map_program_to_fields("Biomedical Engineering & Hospital Equipment Maintenance")
    assert "Engineering" in bio_fields
    assert "Health Sciences" in bio_fields

    # Finance mapping
    acc_fields = map_program_to_fields("Accounting, Audit & Financial Control")
    assert "Business & Finance" in acc_fields


def test_tuition_parser():
    """Verify parsing various FCFA tuition string formats."""
    assert parse_tuition_fee("730,000 FCFA / year") == 730000.0
    assert parse_tuition_fee("50,000 FCFA / year (State tuition)") == 50000.0
    assert parse_tuition_fee("1,100,000 FCFA / year") == 1100000.0
    assert parse_tuition_fee(None) is None
    assert parse_tuition_fee("Contact Admissions Office") is None


def test_recommendation_endpoint_success():
    """Verify full POST /api/recommendations flow with high tech interest."""
    payload = {
        "series": "Science",
        "subjects": ["Computer Science", "Maths", "Physics"],
        "answers": {
            "q1_building": 4,
            "q2_math_logic": 5,
            "q3_helping_sick": 1,
            "q4_organising_data": 2,
            "q5_leadership_selling": 2,
            "q6_creative_design": 3,
            "q7_debating_law": 1,
            "q8_computers_tech": 5,
            "q9_nature_outdoors": 1,
            "q10_teaching": 2,
            "q11_lab_experiments": 3,
            "q12_writing_reading": 2,
        },
        "max_budget": 1000000.0,
    }

    response = client.post("/api/recommendations/", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert "top_fields" in data
    assert len(data["top_fields"]) == 3

    top_field = data["top_fields"][0]
    assert top_field["rank"] == 1
    assert "Computing & IT" in [f["field_name"] for f in data["top_fields"]]
    assert top_field["percentage"] > 0
    assert "explanation" in top_field
    assert len(top_field["explanation"]) > 10

    assert "model_info" in data
    assert data["model_info"]["model_type"] == "RandomForestClassifier"


def test_recommendation_budget_filter():
    """Verify that strict budget filtering excludes expensive programs."""
    payload = {
        "series": "Science",
        "subjects": ["Maths", "Physics", "Technical Drawing"],
        "answers": {
            "q1_building": 5,
            "q2_math_logic": 5,
            "q3_helping_sick": 1,
            "q4_organising_data": 2,
            "q5_leadership_selling": 1,
            "q6_creative_design": 3,
            "q7_debating_law": 1,
            "q8_computers_tech": 4,
            "q9_nature_outdoors": 2,
            "q10_teaching": 1,
            "q11_lab_experiments": 4,
            "q12_writing_reading": 1,
        },
        "max_budget": 100000.0,  # Strict budget: only public/subsidized tuition like Polytech (50,000 FCFA)
    }

    response = client.post("/api/recommendations/", json=payload)
    assert response.status_code == 200
    data = response.json()

    # All matched programs must be <= 100,000 FCFA
    for prog in data["all_matching_programs"]:
        if prog["parsed_tuition"] is not None:
            assert prog["parsed_tuition"] <= 100000.0


def test_recommendation_validation_error():
    """Verify validation error when required fields are missing."""
    invalid_payload = {
        "series": "Science",
        # Missing subjects and answers
    }

    response = client.post("/api/recommendations/", json=invalid_payload)
    assert response.status_code == 422

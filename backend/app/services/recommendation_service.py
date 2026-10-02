"""
Recommendation Service for ApplyCM.
Orchestrates ML prediction, database program retrieval, tuition parsing,
budget filtering, dynamic explainability, and ranking.
"""

import os
import re
from typing import List, Dict, Optional, Any, Tuple
import joblib
import numpy as np
from sqlalchemy.orm import Session

from app.models.school import School
from app.models.program import Program
from app.ml.field_mapping import (
    TARGET_FIELDS,
    FIELD_METADATA,
    map_program_to_fields,
)
from app.ml.generate_dataset import (
    QUESTIONS,
    QUESTION_KEYS,
    SERIES_OPTIONS,
    SUBJECT_OPTIONS,
)
from app.ml.train_model import (
    transform_single_student,
    train_and_evaluate,
)
from app.schemas.recommendation import (
    QuestionItem,
    QuestionnaireMetaResponse,
    RecommendationRequest,
    MatchedProgram,
    RecommendedField,
    RecommendationResponse,
)

MODEL_BUNDLE_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "ml",
    "saved_models",
    "career_model.joblib",
)

_cached_model_bundle = None


def get_model_bundle() -> Dict[str, Any]:
    """Loads the cached model bundle or triggers training if model doesn't exist."""
    global _cached_model_bundle
    if _cached_model_bundle is not None:
        return _cached_model_bundle

    if not os.path.exists(MODEL_BUNDLE_PATH):
        print(f"Model file not found at {MODEL_BUNDLE_PATH}. Initiating automated training...")
        _cached_model_bundle = train_and_evaluate()
    else:
        print(f"Loading trained model bundle from: {MODEL_BUNDLE_PATH}")
        _cached_model_bundle = joblib.load(MODEL_BUNDLE_PATH)

    return _cached_model_bundle


def parse_tuition_fee(fee_str: Optional[str]) -> Optional[float]:
    """
    Parses numeric FCFA tuition from strings like:
    '730,000 FCFA / year' -> 730000.0
    '50,000 FCFA / year (State tuition)' -> 50000.0
    '1,100,000 FCFA / year' -> 1100000.0
    """
    if not fee_str:
        return None

    # Take first segment before '/' or brackets if any
    first_part = fee_str.split("/")[0]
    # Extract consecutive digits
    digits = "".join(ch for ch in first_part if ch.isdigit())
    if digits:
        try:
            return float(digits)
        except ValueError:
            return None
    return None


def generate_field_explanation(
    field_name: str,
    answers: Dict[str, int],
    subjects: List[str],
    series: str,
) -> str:
    """
    Dynamic Explainable AI (XAI):
    Generates a personalized sentence explaining why this field was recommended
    based on the student's highest question ratings and chosen subjects.
    """
    # Identify student's strongest traits
    high_interests = [q_key for q_key, val in answers.items() if val >= 4]

    traits_map = {
        "q1_building": "building and fixing physical systems",
        "q2_math_logic": "solving complex mathematical and logical puzzles",
        "q3_helping_sick": "healthcare and supporting people in need",
        "q4_organising_data": "managing finances, records and structured data",
        "q5_leadership_selling": "leadership, persuasion and entrepreneurship",
        "q6_creative_design": "creative visual design and artistic innovation",
        "q7_debating_law": "debating, legal analysis and policy advocacy",
        "q8_computers_tech": "computing, programming and modern technology",
        "q9_nature_outdoors": "agriculture, environmental science and outdoor fieldwork",
        "q10_teaching": "teaching, mentoring and knowledge sharing",
        "q11_lab_experiments": "conducting scientific laboratory investigations",
        "q12_writing_reading": "in-depth writing, research and communication",
    }

    matched_traits = [traits_map[k] for k in high_interests if k in traits_map]
    top_trait = matched_traits[0] if matched_traits else "your balanced profile and analytical strengths"

    # Relevant subjects
    subj_str = ", ".join(subjects[:2]) if subjects else "your academic coursework"

    explanations = {
        "Computing & IT": f"Recommended because you demonstrated strong inclination for {top_trait}, backed by your strength in {subj_str} and {series} background.",
        "Engineering": f"Recommended because you scored high on {top_trait}, aligning with technical problem-solving and your strong foundation in {subj_str}.",
        "Business & Finance": f"Recommended because you showed clear affinity for {top_trait}, well-suited for economic decision-making with your background in {subj_str}.",
        "Health Sciences": f"Recommended because you demonstrated compassion and interest in {top_trait}, supported by your {series} background and {subj_str}.",
        "Law & Political Science": f"Recommended because you showed outstanding strength in {top_trait}, ideal for structured advocacy and critical analysis.",
        "Education": f"Recommended because you scored high on {top_trait}, reflecting strong communication, empathy, and academic aptitude in {subj_str}.",
        "Agriculture & Environment": f"Recommended because of your high score in {top_trait}, well-suited for Cameroon's sustainable agronomy and environmental sector.",
        "Arts, Design & Communication": f"Recommended because you expressed strong creative drive in {top_trait}, perfectly matching media, design and communication.",
    }

    return explanations.get(
        field_name,
        f"Recommended based on your high score in {top_trait} and academic strength in {subj_str}.",
    )


class RecommendationService:
    @staticmethod
    def get_questionnaire_meta() -> QuestionnaireMetaResponse:
        """Returns the dynamic questionnaire metadata for the frontend."""
        questions_list = [
            QuestionItem(id=k, statement=text, min_value=1, max_value=5)
            for k, text in QUESTIONS
        ]
        return QuestionnaireMetaResponse(
            questions=questions_list,
            series_options=SERIES_OPTIONS,
            subject_options=SUBJECT_OPTIONS,
            default_budget=600000.0,
            currency="FCFA",
        )

    @staticmethod
    def recommend(
        request: RecommendationRequest,
        db: Session,
    ) -> RecommendationResponse:
        """
        Executes prediction, retrieves database programs, parses tuition,
        applies budget filtering, ranks results, and formats response.
        """
        bundle = get_model_bundle()
        model = bundle["model"]
        classes = bundle["classes"]
        feature_names = bundle["feature_names"]
        metrics = bundle.get("metrics", {})

        # 1. Vectorize student answers
        answers_dict = {k: request.answers.get(k, 3) for k in QUESTION_KEYS}
        student_input = {
            **answers_dict,
            "series": request.series,
            "subjects": request.subjects,
        }
        X_vec = transform_single_student(student_input, feature_names)

        # 2. Predict field probabilities
        probs = model.predict_proba(X_vec)[0]

        # 3. Rank fields by probability descending
        ranked_indices = np.argsort(probs)[::-1]
        top_indices = ranked_indices[:3]  # Top 3 fields

        # 4. Query schools and programs from database
        all_programs: List[Program] = db.query(Program).all()
        schools_map: Dict[Any, School] = {
            s.id: s for s in db.query(School).all()
        }

        # 5. Build Top Fields and Match Programs
        top_fields_result: List[RecommendedField] = []
        all_matched_programs: List[MatchedProgram] = []

        for rank_num, idx in enumerate(top_indices, start=1):
            field_name = classes[idx]
            prob = float(probs[idx])
            percentage = round(prob * 100, 1)

            # Dynamic explanation
            explanation = generate_field_explanation(
                field_name=field_name,
                answers=answers_dict,
                subjects=request.subjects,
                series=request.series,
            )

            # Match programs in DB that correspond to this field
            field_programs: List[MatchedProgram] = []
            for prog in all_programs:
                prog_fields = map_program_to_fields(prog.field_of_study)
                if field_name in prog_fields:
                    school = schools_map.get(prog.school_id)
                    school_name = school.name if school else "Cameroon Partner Institution"
                    school_loc = school.location if hasattr(school, "location") and school.location else (
                        f"{school.city or ''}, {school.arrondissement or ''}".strip(", ") if school else None
                    )
                    school_web = school.website_url if hasattr(school, "website_url") else None
                    school_logo = school.logo_url if hasattr(school, "logo_url") else None

                    parsed_tuition = parse_tuition_fee(prog.tuition_fee)

                    # Check budget fit
                    is_within_budget = True
                    budget_fit_score = 1.0
                    if request.max_budget is not None and parsed_tuition is not None:
                        if parsed_tuition > request.max_budget:
                            is_within_budget = False
                        else:
                            # Higher score for more affordable program within budget
                            budget_fit_score = max(0.1, 1.0 - (parsed_tuition / request.max_budget))

                    # Filter out programs exceeding budget if budget was specified
                    if request.max_budget is not None and not is_within_budget:
                        continue

                    matched_prog = MatchedProgram(
                        id=str(prog.id),
                        program_title=prog.field_of_study,
                        school_id=str(prog.school_id),
                        school_name=school_name,
                        school_location=school_loc,
                        school_website=school_web,
                        school_logo=school_logo,
                        degree_type=getattr(prog, "degree_type", None) or "Bachelor / Licence",
                        tuition_fee=prog.tuition_fee,
                        parsed_tuition=parsed_tuition,
                        duration=getattr(prog, "duration", None) or "3 years",
                        admission_requirements=prog.admission_requirements,
                        description=getattr(prog, "description", None),
                        matched_target_field=field_name,
                        is_within_budget=is_within_budget,
                        budget_fit_score=budget_fit_score,
                    )
                    field_programs.append(matched_prog)

            # Sort programs within field by budget fit / lowest tuition
            field_programs.sort(key=lambda p: (p.parsed_tuition or 9999999))

            recommended_field = RecommendedField(
                field_name=field_name,
                rank=rank_num,
                probability=round(prob, 4),
                percentage=percentage,
                description=FIELD_METADATA.get(field_name, {}).get("description", ""),
                explanation=explanation,
                programs_available_count=len(field_programs),
                programs=field_programs,
            )
            top_fields_result.append(recommended_field)

            # Append to overall list (avoiding duplicate IDs in global list)
            for p in field_programs:
                if not any(existing.id == p.id for existing in all_matched_programs):
                    all_matched_programs.append(p)

        return RecommendationResponse(
            student_summary={
                "series": request.series,
                "subjects": request.subjects,
                "max_budget": request.max_budget,
            },
            top_fields=top_fields_result,
            all_matching_programs=all_matched_programs,
            total_matching_programs=len(all_matched_programs),
            model_info={
                "model_type": "RandomForestClassifier",
                "accuracy": metrics.get("rf_accuracy", 0.81),
                "top3_accuracy": metrics.get("rf_top3_accuracy", 0.97),
                "baseline_accuracy": metrics.get("baseline_accuracy", 0.69),
            },
        )

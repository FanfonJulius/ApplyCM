"""
Synthetic Dataset Generator for ApplyCM Career Recommender.
Generates realistic Cameroonian student survey data with realistic variance and noise.
"""

import os
import random
import numpy as np
import pandas as pd
from typing import List, Dict, Any
from app.ml.field_mapping import TARGET_FIELDS

# Questionnaire Questions Definitions
QUESTIONS = [
    ("q1_building", "I enjoy fixing or building things."),
    ("q2_math_logic", "I like solving math or logic problems."),
    ("q3_helping_sick", "I like helping people who are sick or in need."),
    ("q4_organising_data", "I enjoy organising money, records or data."),
    ("q5_leadership_selling", "I like leading a group or selling an idea."),
    ("q6_creative_design", "I enjoy drawing, designing or creating."),
    ("q7_debating_law", "I like debating and arguing a case."),
    ("q8_computers_tech", "I like working with computers and technology."),
    ("q9_nature_outdoors", "I enjoy working outdoors with plants, animals or nature."),
    ("q10_teaching", "I like teaching or explaining things to others."),
    ("q11_lab_experiments", "I like doing lab experiments."),
    ("q12_writing_reading", "I like writing and reading."),
]

QUESTION_KEYS = [q[0] for q in QUESTIONS]

SERIES_OPTIONS = ["Science", "Arts", "Commercial", "Technical"]

SUBJECT_OPTIONS = [
    "Maths",
    "Physics",
    "Chemistry",
    "Biology",
    "Computer Science",
    "Economics",
    "Accounting",
    "Literature",
    "History",
    "Geography",
    "Languages",
    "Technical Drawing",
]

# Field Archetypes with typical feature profiles
# Means for each 1-5 rating, typical series weights, typical subjects
FIELD_ARCHETYPES: Dict[str, Dict[str, Any]] = {
    "Computing & IT": {
        "means": {
            "q8_computers_tech": 4.6,
            "q2_math_logic": 4.2,
            "q1_building": 3.6,
            "q4_organising_data": 3.3,
            "q6_creative_design": 3.2,
        },
        "series_dist": [0.65, 0.05, 0.05, 0.25],  # Science, Arts, Commercial, Technical
        "fav_subjects": ["Computer Science", "Maths", "Physics", "Technical Drawing"],
    },
    "Engineering": {
        "means": {
            "q1_building": 4.6,
            "q2_math_logic": 4.5,
            "q11_lab_experiments": 4.1,
            "q8_computers_tech": 3.8,
            "q6_creative_design": 3.2,
        },
        "series_dist": [0.60, 0.02, 0.03, 0.35],
        "fav_subjects": ["Maths", "Physics", "Technical Drawing", "Chemistry", "Computer Science"],
    },
    "Business & Finance": {
        "means": {
            "q4_organising_data": 4.6,
            "q5_leadership_selling": 4.4,
            "q2_math_logic": 3.5,
            "q7_debating_law": 3.2,
            "q12_writing_reading": 3.1,
        },
        "series_dist": [0.15, 0.15, 0.65, 0.05],
        "fav_subjects": ["Economics", "Accounting", "Maths", "Languages", "Geography"],
    },
    "Health Sciences": {
        "means": {
            "q3_helping_sick": 4.8,
            "q11_lab_experiments": 4.3,
            "q10_teaching": 3.6,
            "q2_math_logic": 3.3,
            "q12_writing_reading": 3.2,
        },
        "series_dist": [0.88, 0.04, 0.03, 0.05],
        "fav_subjects": ["Biology", "Chemistry", "Physics", "Maths"],
    },
    "Law & Political Science": {
        "means": {
            "q7_debating_law": 4.7,
            "q12_writing_reading": 4.5,
            "q5_leadership_selling": 3.8,
            "q10_teaching": 3.4,
            "q4_organising_data": 3.0,
        },
        "series_dist": [0.08, 0.80, 0.10, 0.02],
        "fav_subjects": ["Literature", "History", "Languages", "Economics", "Geography"],
    },
    "Education": {
        "means": {
            "q10_teaching": 4.7,
            "q12_writing_reading": 4.1,
            "q3_helping_sick": 3.8,
            "q5_leadership_selling": 3.2,
            "q2_math_logic": 3.0,
        },
        "series_dist": [0.35, 0.45, 0.15, 0.05],
        "fav_subjects": ["Languages", "Literature", "History", "Maths", "Biology", "Geography"],
    },
    "Agriculture & Environment": {
        "means": {
            "q9_nature_outdoors": 4.8,
            "q11_lab_experiments": 4.1,
            "q1_building": 3.5,
            "q3_helping_sick": 3.0,
            "q4_organising_data": 3.1,
        },
        "series_dist": [0.70, 0.10, 0.10, 0.10],
        "fav_subjects": ["Biology", "Geography", "Chemistry", "Physics", "Economics"],
    },
    "Arts, Design & Communication": {
        "means": {
            "q6_creative_design": 4.7,
            "q12_writing_reading": 4.3,
            "q5_leadership_selling": 3.8,
            "q8_computers_tech": 3.4,
            "q7_debating_law": 3.2,
        },
        "series_dist": [0.10, 0.65, 0.15, 0.10],
        "fav_subjects": ["Literature", "Languages", "Technical Drawing", "History", "Computer Science"],
    },
}


def generate_single_profile(target_field: str) -> Dict[str, Any]:
    """Generates a single student profile given their intended field."""
    archetype = FIELD_ARCHETYPES[target_field]
    profile: Dict[str, Any] = {}

    # 1. Generate 12 interest scores (1 to 5) with Gaussian noise around means
    for q_key in QUESTION_KEYS:
        base_mean = archetype["means"].get(q_key, 2.5)  # non-featured questions default to ~2.5
        score = np.random.normal(loc=base_mean, scale=0.85)
        # Clamp to integer between 1 and 5
        score_clamped = int(np.clip(np.round(score), 1, 5))
        profile[q_key] = score_clamped

    # 2. Sample Academic Series
    series = np.random.choice(SERIES_OPTIONS, p=archetype["series_dist"])
    profile["series"] = series

    # 3. Sample 3 Strongest Subjects
    # Combine favored subjects with some random selection to reflect diversity
    favs = archetype["fav_subjects"]
    num_favs = random.choices([2, 3], weights=[0.4, 0.6])[0]
    chosen_favs = random.sample(favs, min(num_favs, len(favs)))

    other_pool = [s for s in SUBJECT_OPTIONS if s not in chosen_favs]
    needed = 3 - len(chosen_favs)
    if needed > 0 and other_pool:
        chosen_others = random.sample(other_pool, needed)
        selected_subjects = chosen_favs + chosen_others
    else:
        selected_subjects = chosen_favs[:3]

    random.shuffle(selected_subjects)
    profile["subject_1"] = selected_subjects[0]
    profile["subject_2"] = selected_subjects[1]
    profile["subject_3"] = selected_subjects[2]

    profile["target_field"] = target_field
    return profile


def generate_dataset(num_per_field: int = 400, noise_ratio: float = 0.12, random_seed: int = 42) -> pd.DataFrame:
    """
    Generates a full dataset of students across all 8 fields, injecting
    realistic noise to prevent artificial 100% accuracy and ensure natural overlap.
    """
    random.seed(random_seed)
    np.random.seed(random_seed)

    rows = []
    for field in TARGET_FIELDS:
        for _ in range(num_per_field):
            profile = generate_single_profile(field)
            rows.append(profile)

    df = pd.DataFrame(rows)

    # Inject realistic label noise: swap target_field for noise_ratio of samples
    num_noise = int(len(df) * noise_ratio)
    noise_indices = random.sample(range(len(df)), num_noise)
    for idx in noise_indices:
        current_field = df.loc[idx, "target_field"]
        other_fields = [f for f in TARGET_FIELDS if f != current_field]
        df.loc[idx, "target_field"] = random.choice(other_fields)

    # Shuffle the dataset
    df = df.sample(frac=1.0, random_state=random_seed).reset_index(drop=True)
    return df


if __name__ == "__main__":
    output_dir = os.path.join(os.path.dirname(__file__), "data")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "student_dataset.csv")

    print(f"Generating synthetic dataset with {len(TARGET_FIELDS)} fields...")
    df = generate_dataset(num_per_field=400, noise_ratio=0.12)
    df.to_csv(output_path, index=False)
    print(f"Dataset successfully generated with {len(df)} rows.")
    print(f"Saved to: {output_path}")
    print("\nField distribution:")
    print(df["target_field"].value_counts())

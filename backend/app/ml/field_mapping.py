"""
Field of study taxonomy and mapping logic for ApplyCM.
Maps program titles to 8 standardized broad fields of study.
"""

from typing import List, Dict, Tuple, Optional

# Standard 8 target fields predicted by the model
TARGET_FIELDS: List[str] = [
    "Computing & IT",
    "Engineering",
    "Business & Finance",
    "Health Sciences",
    "Law & Political Science",
    "Education",
    "Agriculture & Environment",
    "Arts, Design & Communication",
]

# Field descriptions for presentation & UI display
FIELD_METADATA: Dict[str, Dict[str, str]] = {
    "Computing & IT": {
        "icon": "computer",
        "description": "Software engineering, cybersecurity, data science, networking, and modern digital architectures.",
    },
    "Engineering": {
        "icon": "cog",
        "description": "Civil, mechanical, electrical, biomedical, and industrial technology and infrastructure.",
    },
    "Business & Finance": {
        "icon": "chart-bar",
        "description": "Accounting, financial management, corporate strategy, logistics, marketing, and entrepreneurship.",
    },
    "Health Sciences": {
        "icon": "heart-pulse",
        "description": "Medicine, biomedical engineering, nursing, public health, and diagnostic technology.",
    },
    "Law & Political Science": {
        "icon": "scale",
        "description": "Corporate law, international relations, public policy, governance, and dispute resolution.",
    },
    "Education": {
        "icon": "academic-cap",
        "description": "Pedagogy, curriculum development, educational leadership, and STEM teaching.",
    },
    "Agriculture & Environment": {
        "icon": "leaf",
        "description": "Agronomy, agribusiness, environmental management, forestry, and sustainable resources.",
    },
    "Arts, Design & Communication": {
        "icon": "sparkles",
        "description": "Digital media, journalism, graphic design, public relations, and creative communication.",
    },
}

# Known program title exact/partial matches with primary and secondary fields
PROGRAM_FIELD_MAP: Dict[str, Tuple[str, Optional[str]]] = {
    "Software Engineering": ("Computing & IT", None),
    "Cybersecurity & Digital Forensics": ("Computing & IT", None),
    "Information Systems & Big Data Analytics": ("Computing & IT", "Business & Finance"),
    "Computer Engineering & Artificial Intelligence": ("Computing & IT", "Engineering"),
    "Telecommunications & Network Engineering": ("Engineering", "Computing & IT"),
    "Civil & Environmental Engineering": ("Engineering", "Agriculture & Environment"),
    "Software Engineering & Database Administration": ("Computing & IT", None),
    "Accounting, Audit & Financial Control": ("Business & Finance", None),
    "Logistics & Transport Management": ("Business & Finance", None),
    "Biomedical Engineering & Hospital Equipment Maintenance": ("Engineering", "Health Sciences"),
    "Electrical Power Systems & Renewable Energy": ("Engineering", None),
    "Computer Systems & Network Security": ("Computing & IT", None),
    "Banking, Finance & Fintech": ("Business & Finance", "Computing & IT"),
    "Business Law & Corporate Governance": ("Law & Political Science", "Business & Finance"),
    "Human Resource Management": ("Business & Finance", "Education"),
}

# Keyword fallbacks for arbitrary program titles
KEYWORD_MAPPINGS: List[Tuple[List[str], str]] = [
    (["software", "computer", "cyber", "data", "web", "programming", "ai", "artificial intelligence", "database", "it", "ict", "cloud", "devops", "systems"], "Computing & IT"),
    (["civil", "electrical", "mechanical", "telecom", "renewable", "robotics", "architecture", "engineering", "industrial"], "Engineering"),
    (["accounting", "finance", "business", "management", "logistics", "audit", "marketing", "bank", "trade", "commerce", "economics"], "Business & Finance"),
    (["biomedical", "health", "nursing", "medicine", "pharmacy", "medical", "hospital", "clinic"], "Health Sciences"),
    (["law", "legal", "political", "governance", "public policy", "international relations"], "Law & Political Science"),
    (["education", "teaching", "curriculum", "pedagogy"], "Education"),
    (["agronomy", "agriculture", "forestry", "environment", "agro", "crop", "animal science"], "Agriculture & Environment"),
    (["media", "communication", "design", "journalism", "arts", "graphic", "multimedia"], "Arts, Design & Communication"),
]


def map_program_to_fields(field_of_study: str) -> List[str]:
    """
    Returns a list of matching broad target fields (primary and optional secondary)
    for a given program field_of_study string.
    """
    cleaned = field_of_study.strip()

    # 1. Exact match in catalog
    if cleaned in PROGRAM_FIELD_MAP:
        primary, secondary = PROGRAM_FIELD_MAP[cleaned]
        return [primary] if not secondary else [primary, secondary]

    # 2. Case-insensitive substring match in catalog
    lower_title = cleaned.lower()
    for known_title, (primary, secondary) in PROGRAM_FIELD_MAP.items():
        if known_title.lower() in lower_title or lower_title in known_title.lower():
            return [primary] if not secondary else [primary, secondary]

    # 3. Keyword heuristic search
    matched_fields: List[str] = []
    for keywords, target_field in KEYWORD_MAPPINGS:
        if any(kw in lower_title for kw in keywords):
            if target_field not in matched_fields:
                matched_fields.append(target_field)

    return matched_fields if matched_fields else ["Computing & IT"]

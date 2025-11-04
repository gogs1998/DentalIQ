"""
User Profile Schema for DentalCorrectIQ

This module defines the user profile structure and onboarding questions.
Each user gets a personalized configuration based on their practice style.
"""

from pydantic import BaseModel
from typing import List, Optional, Dict
from enum import Enum

class DentalNotation(str, Enum):
    FDI = "FDI"  # International (11-48)
    PALMER = "Palmer"  # UK traditional (quadrants)
    UNIVERSAL = "Universal"  # US system (1-32)

class PracticeType(str, Enum):
    NHS = "NHS"
    PRIVATE = "Private"
    MIXED = "Mixed"

class Specialty(str, Enum):
    GENERAL = "General Dentistry"
    ORTHODONTICS = "Orthodontics"
    PERIODONTICS = "Periodontics"
    ENDODONTICS = "Endodontics"
    ORAL_SURGERY = "Oral Surgery"
    PROSTHODONTICS = "Prosthodontics"
    PAEDIATRIC = "Paediatric Dentistry"

class UserProfile(BaseModel):
    user_id: str
    name: str
    gdc_number: Optional[str] = None

    # Practice settings
    notation_system: DentalNotation = DentalNotation.FDI
    practice_type: PracticeType = PracticeType.MIXED
    specialty: Specialty = Specialty.GENERAL

    # Language preferences
    primary_languages: List[str] = ["English"]  # Languages they type notes in

    # Common procedures (for abbreviation expansion)
    common_procedures: List[str] = []

    # Custom abbreviations (user-specific)
    custom_abbreviations: Dict[str, str] = {}  # e.g., {"RCT": "root canal treatment"}

    # Note-taking style
    verbose_notes: bool = False  # True = detailed, False = concise
    include_radiograph_justification: bool = True
    always_include_medical_history: bool = True

    # Patient demographics (helps with context)
    typical_patient_age_range: str = "Mixed ages"  # "Children", "Adults", "Elderly", "Mixed"
    common_patient_languages: List[str] = ["English"]

    # Compliance preferences
    gdc_score_threshold: int = 80  # Minimum acceptable score
    auto_add_missing_elements: bool = False  # Auto-suggest additions

    # Referral patterns
    common_referral_specialties: List[str] = []

    # Style learning - NEW
    example_notes: List[str] = []  # 3-5 example notes from user
    style_profile: Optional[Dict] = None  # Analyzed writing style
    example_notes_scores: List[Dict] = []  # GDC scores of their examples


# Onboarding Questions
ONBOARDING_QUESTIONS = [
    {
        "id": "name",
        "question": "What is your name?",
        "type": "text",
        "required": True,
        "help": "This helps personalize your experience"
    },
    {
        "id": "gdc_number",
        "question": "GDC Registration Number (optional)",
        "type": "text",
        "required": False,
        "help": "Your General Dental Council registration number"
    },
    {
        "id": "notation_system",
        "question": "Which dental notation system do you prefer?",
        "type": "select",
        "options": [
            {"value": "FDI", "label": "FDI (International) - e.g., 11, 16, 46"},
            {"value": "Palmer", "label": "Palmer (UK traditional) - e.g., UR1, UL6, LL6"},
            {"value": "Universal", "label": "Universal (US) - e.g., 1-32"}
        ],
        "default": "FDI",
        "required": True,
        "help": "The system will convert your abbreviations to match this notation"
    },
    {
        "id": "practice_type",
        "question": "What type of practice do you work in?",
        "type": "select",
        "options": [
            {"value": "NHS", "label": "NHS only"},
            {"value": "Private", "label": "Private only"},
            {"value": "Mixed", "label": "Mixed NHS and Private"}
        ],
        "default": "Mixed",
        "required": True,
        "help": "This affects documentation requirements and terminology"
    },
    {
        "id": "specialty",
        "question": "What is your specialty?",
        "type": "select",
        "options": [
            {"value": "General Dentistry", "label": "General Dentistry"},
            {"value": "Orthodontics", "label": "Orthodontics"},
            {"value": "Periodontics", "label": "Periodontics"},
            {"value": "Endodontics", "label": "Endodontics"},
            {"value": "Oral Surgery", "label": "Oral Surgery"},
            {"value": "Prosthodontics", "label": "Prosthodontics"},
            {"value": "Paediatric Dentistry", "label": "Paediatric Dentistry"}
        ],
        "default": "General Dentistry",
        "required": True,
        "help": "Helps tailor note templates to your specialty"
    },
    {
        "id": "primary_languages",
        "question": "Which languages do you commonly type notes in?",
        "type": "multi_select",
        "options": [
            {"value": "English", "label": "English"},
            {"value": "Polish", "label": "Polish"},
            {"value": "Romanian", "label": "Romanian"},
            {"value": "Urdu", "label": "Urdu"},
            {"value": "Hindi", "label": "Hindi"},
            {"value": "Arabic", "label": "Arabic"},
            {"value": "Portuguese", "label": "Portuguese"},
            {"value": "Spanish", "label": "Spanish"}
        ],
        "default": ["English"],
        "required": True,
        "help": "Select all languages you use when typing quick notes"
    },
    {
        "id": "common_procedures",
        "question": "What procedures do you perform most often? (Select up to 5)",
        "type": "multi_select",
        "max_selections": 5,
        "options": [
            {"value": "Examinations", "label": "Routine examinations"},
            {"value": "Fillings", "label": "Composite/amalgam fillings"},
            {"value": "Extractions", "label": "Extractions"},
            {"value": "Root canal treatment", "label": "Root canal treatment"},
            {"value": "Crowns", "label": "Crowns and bridges"},
            {"value": "Dentures", "label": "Dentures"},
            {"value": "Hygiene", "label": "Hygiene/scale and polish"},
            {"value": "Orthodontics", "label": "Orthodontic treatment"},
            {"value": "Implants", "label": "Implants"},
            {"value": "Cosmetic", "label": "Cosmetic procedures"}
        ],
        "default": ["Examinations", "Fillings"],
        "required": True,
        "help": "This helps suggest relevant templates and terminology"
    },
    {
        "id": "note_style",
        "question": "How detailed should your clinical notes be?",
        "type": "select",
        "options": [
            {"value": "concise", "label": "Concise - Short, essential information only"},
            {"value": "standard", "label": "Standard - Balanced detail"},
            {"value": "verbose", "label": "Verbose - Comprehensive, detailed notes"}
        ],
        "default": "standard",
        "required": True,
        "help": "The system will adjust output length to match your preference"
    },
    {
        "id": "compliance_preferences",
        "question": "How strict should GDC compliance checking be?",
        "type": "select",
        "options": [
            {"value": "strict", "label": "Strict - Flag anything below 90/100", "threshold": 90},
            {"value": "standard", "label": "Standard - Flag anything below 80/100", "threshold": 80},
            {"value": "lenient", "label": "Lenient - Only flag below 60/100", "threshold": 60}
        ],
        "default": "standard",
        "required": True,
        "help": "Determines when the system warns you about missing documentation"
    },
    {
        "id": "auto_suggestions",
        "question": "Would you like automatic suggestions for missing elements?",
        "type": "select",
        "options": [
            {"value": "always", "label": "Yes, always suggest additions to my notes"},
            {"value": "when_low", "label": "Only when GDC score is low"},
            {"value": "never", "label": "No, just show me the score"}
        ],
        "default": "when_low",
        "required": True,
        "help": "Control how proactive the assistant is with suggestions"
    },
    {
        "id": "example_notes",
        "question": "Provide 3-5 examples of your typical clinical notes",
        "type": "multi_text",
        "min_entries": 3,
        "max_entries": 5,
        "required": True,
        "help": "We'll analyze your note-taking style and personalize suggestions to match YOUR writing style. Paste 3-5 real examples (remove patient names/IDs). Include different types: routine exams, treatments, emergencies, etc.",
        "placeholder": "Example: Mhx reviewed NAD. Pt c/o pain LR6. O/E large MOD cavity..."
    }
]


# Example user profile
EXAMPLE_PROFILE = {
    "user_id": "dr_kowalski",
    "name": "Dr. Anna Kowalski",
    "gdc_number": "123456",
    "notation_system": "FDI",
    "practice_type": "Mixed",
    "specialty": "General Dentistry",
    "primary_languages": ["Polish", "English"],
    "common_procedures": ["Examinations", "Fillings", "Extractions", "Root canal treatment"],
    "custom_abbreviations": {
        "RCT": "root canal treatment",
        "PA": "periapical radiograph",
        "BW": "bitewing radiograph",
        "C&B": "crown and bridge"
    },
    "verbose_notes": False,
    "include_radiograph_justification": True,
    "always_include_medical_history": True,
    "typical_patient_age_range": "Mixed ages",
    "common_patient_languages": ["Polish", "English"],
    "gdc_score_threshold": 80,
    "auto_add_missing_elements": True,
    "common_referral_specialties": ["Orthodontics", "Oral Surgery"]
}

"""
LLM-Based GDC Compliance Scoring

Uses the LLM to intelligently evaluate clinical notes against GDC standards,
rather than simple keyword matching.
"""

import httpx
import json
from typing import Dict, List, Tuple


async def call_ollama(prompt: str, max_tokens: int = 1000) -> str:
    """Call local Ollama API"""
    OLLAMA_URL = "http://localhost:11434/api/generate"

    payload = {
        "model": "llama3.2:3b",
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.2,  # Very low for consistent scoring
            "num_predict": max_tokens
        }
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(OLLAMA_URL, json=payload)
        response.raise_for_status()
        result = response.json()
        return result["response"].strip()


def create_scoring_prompt(corrected_text: str, user_profile: dict) -> str:
    """
    Create a structured prompt for LLM to score the clinical note.
    Returns a prompt that asks for JSON-structured scoring.
    """

    specialty = user_profile.get("specialty", "General Dentistry")
    practice_type = user_profile.get("practice_type", "Mixed")

    prompt = f"""You are a UK GDC compliance auditor reviewing clinical notes for a {specialty} dentist in a {practice_type} practice.

CLINICAL NOTE TO EVALUATE:
"{corrected_text}"

Evaluate this note against UK GDC standards. Score each element 0-20 points.

GDC REQUIRED ELEMENTS:

1. MEDICAL HISTORY (0-20 points)
   - 20: Medical history explicitly reviewed/documented with detail
   - 15: Medical history mentioned but minimal detail
   - 10: Implied but not clearly documented
   - 0: No medical history documentation

2. CLINICAL EXAMINATION (0-20 points)
   - 20: Detailed examination findings (extra-oral, intra-oral, specific findings)
   - 15: Good examination documentation
   - 10: Basic examination findings mentioned
   - 5: Minimal examination noted
   - 0: No examination documented

3. DIAGNOSIS (0-20 points)
   - 20: Clear, specific diagnosis stated
   - 15: Working diagnosis or clinical impression given
   - 10: Diagnosis implied from treatment
   - 5: Very vague diagnosis
   - 0: No diagnosis stated

4. TREATMENT PLAN (0-20 points)
   - 20: Comprehensive plan with options discussed, prognosis, alternatives
   - 15: Good treatment plan documented
   - 10: Basic treatment plan mentioned
   - 5: Treatment mentioned but not clearly planned
   - 0: No treatment plan

5. CONSENT (0-20 points)
   - 20: Detailed consent with risks, benefits, alternatives discussed
   - 15: Consent documented with some detail
   - 10: Patient agreement/consent mentioned
   - 5: Implied consent only
   - 0: No consent documentation

SPECIAL CHECKS:
- IR(ME)R: If radiograph mentioned, MUST have clinical justification
  - Valid justification = "justified by clinical presentation/symptoms"
  - Invalid = "routine", "regular check", or no justification
  - DEDUCT 10 points if radiograph mentioned without proper justification

OUTPUT FORMAT (respond with ONLY this JSON, no other text):
{{
  "medical_history": {{"score": 0-20, "feedback": "specific feedback"}},
  "clinical_examination": {{"score": 0-20, "feedback": "specific feedback"}},
  "diagnosis": {{"score": 0-20, "feedback": "specific feedback"}},
  "treatment_plan": {{"score": 0-20, "feedback": "specific feedback"}},
  "consent": {{"score": 0-20, "feedback": "specific feedback"}},
  "irmer_compliant": true/false,
  "irmer_feedback": "feedback about radiograph justification if applicable",
  "total_score": 0-100,
  "overall_feedback": "brief summary of note quality"
}}

Evaluate the note now:"""

    return prompt


def create_enhanced_correction_prompt(text: str, detected_lang: str, user_profile: dict) -> str:
    """
    Create an enhanced prompt with strict GDC guidelines for note correction.
    """

    from gdc_guidelines import get_gdc_prompt_guidelines

    specialty = user_profile.get("specialty", "General Dentistry")
    notation = user_profile.get("notation_system", "FDI")
    verbose = user_profile.get("verbose_notes", False)
    practice_type = user_profile.get("practice_type", "Mixed")

    # Get personalized GDC guidelines
    gdc_guidelines = get_gdc_prompt_guidelines(user_profile)

    prompt = f"""You are a UK dental clinical documentation expert helping a {specialty} dentist write GDC-compliant notes.

{gdc_guidelines}

TASK: Convert the input text into a properly structured UK GDC-compliant clinical note.

INPUT LANGUAGE: {detected_lang}
OUTPUT REQUIRED: Professional UK clinical English

STRICT REQUIREMENTS:
1. If input is not English, translate to English first
2. Expand ALL abbreviations using the list above
3. Use {notation} tooth notation system
4. Structure the note logically (Medical history → Examination → Diagnosis → Plan → Consent)
5. {"Provide comprehensive detail" if verbose else "Be concise but complete"}
6. If radiograph mentioned, ADD proper IR(ME)R justification
7. Ensure ALL 5 GDC elements are present (add minimal versions if missing)

INPUT TEXT:
{text}

EXAMPLE OUTPUT STRUCTURE:
Medical history reviewed [or "no changes" or specific detail].
Patient complains of [symptoms].
Clinical examination: [findings].
Diagnosis: [clear diagnosis].
Treatment plan: [plan discussed].
Consent: [risks/benefits discussed, patient agreed].

Now convert the input text following these guidelines. Output ONLY the corrected clinical note:"""

    return prompt


async def llm_score_note(corrected_text: str, user_profile: dict) -> Dict:
    """
    Use LLM to intelligently score the clinical note.

    Returns:
        {
            "total_score": 0-100,
            "element_scores": {...},
            "feedback": {...},
            "missing_elements": [...],
            "suggestions": [...]
        }
    """

    # Create scoring prompt
    prompt = create_scoring_prompt(corrected_text, user_profile)

    # Get LLM evaluation
    try:
        response = await call_ollama(prompt, max_tokens=1000)

        # Try to parse JSON response
        # Remove markdown code blocks if present
        response = response.replace("```json", "").replace("```", "").strip()

        scoring_result = json.loads(response)

        # Extract scores and feedback
        element_scores = {
            "medical_history": scoring_result["medical_history"]["score"],
            "clinical_examination": scoring_result["clinical_examination"]["score"],
            "diagnosis": scoring_result["diagnosis"]["score"],
            "treatment_plan": scoring_result["treatment_plan"]["score"],
            "consent": scoring_result["consent"]["score"]
        }

        # Determine missing elements (score < 10 = missing)
        missing_elements = [
            elem.replace("_", " ").title()
            for elem, score in element_scores.items()
            if score < 10
        ]

        # Generate suggestions based on feedback
        suggestions = []

        for element, data in scoring_result.items():
            if element in ["medical_history", "clinical_examination", "diagnosis", "treatment_plan", "consent"]:
                if data["score"] < 15:
                    suggestions.append(f"{element.replace('_', ' ').title()}: {data['feedback']}")

        # IR(ME)R check
        if not scoring_result.get("irmer_compliant", True):
            suggestions.insert(0, f"⚠️ IR(ME)R ISSUE: {scoring_result.get('irmer_feedback', 'Radiograph justification required')}")

        return {
            "total_score": scoring_result["total_score"],
            "element_scores": element_scores,
            "feedback": {
                "medical_history": scoring_result["medical_history"]["feedback"],
                "clinical_examination": scoring_result["clinical_examination"]["feedback"],
                "diagnosis": scoring_result["diagnosis"]["feedback"],
                "treatment_plan": scoring_result["treatment_plan"]["feedback"],
                "consent": scoring_result["consent"]["feedback"]
            },
            "missing_elements": missing_elements,
            "suggestions": suggestions,
            "overall_feedback": scoring_result.get("overall_feedback", ""),
            "irmer_compliant": scoring_result.get("irmer_compliant", True)
        }

    except (json.JSONDecodeError, KeyError) as e:
        # Fallback to simple scoring if LLM response is malformed
        print(f"LLM scoring failed, using fallback: {e}")
        return fallback_score(corrected_text)


def fallback_score(text: str) -> Dict:
    """
    Fallback scoring using simple keyword matching if LLM fails.
    """

    score = 0
    missing = []
    text_lower = text.lower()

    elements = {
        "medical_history": ["medical history", "mhx", "health reviewed"],
        "clinical_examination": ["examined", "examination", "findings"],
        "diagnosis": ["diagnosis", "diagnosed"],
        "treatment_plan": ["plan", "treatment plan", "advised"],
        "consent": ["consent", "agreed", "discussed"]
    }

    element_scores = {}
    for element, keywords in elements.items():
        if any(kw in text_lower for kw in keywords):
            score += 20
            element_scores[element] = 20
        else:
            missing.append(element.replace("_", " ").title())
            element_scores[element] = 0

    return {
        "total_score": score,
        "element_scores": element_scores,
        "feedback": {},
        "missing_elements": missing,
        "suggestions": ["Consider adding: " + elem for elem in missing],
        "overall_feedback": "Basic compliance check completed",
        "irmer_compliant": True
    }


# Examples of scoring in action
SCORING_EXAMPLES = {
    "poor_note": {
        "text": "pt c/o pain ul6, filling done",
        "expected_score": 20,
        "feedback": "Missing medical history, examination detail, diagnosis, consent"
    },
    "good_note": {
        "text": "Medical history reviewed, no changes. Patient complains of pain UL6. Examined, large cavity noted. Diagnosis: dental caries. Treatment plan: composite filling discussed. Patient consented. Composite filling placed.",
        "expected_score": 90,
        "feedback": "Excellent note with all elements present"
    }
}

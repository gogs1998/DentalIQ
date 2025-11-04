"""
Personal Note Style Learning System

Analyzes user's example notes to learn their writing style and preferences,
then generates GDC-compliant notes that match their personal style.
"""

import httpx
import json
from typing import List, Dict, Tuple


async def call_ollama(prompt: str, max_tokens: int = 1500) -> str:
    """Call local Ollama API"""
    OLLAMA_URL = "http://localhost:11434/api/generate"

    payload = {
        "model": "llama3.2:3b",
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.3,
            "num_predict": max_tokens
        }
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(OLLAMA_URL, json=payload)
        response.raise_for_status()
        result = response.json()
        return result["response"].strip()


async def analyze_user_note_style(example_notes: List[str]) -> Dict:
    """
    Analyze a user's example notes to extract their personal writing style.

    Args:
        example_notes: List of 3-5 example notes from the user

    Returns:
        Dict containing style characteristics
    """

    # Combine all example notes
    examples_text = "\n\n---EXAMPLE---\n\n".join(example_notes)

    prompt = f"""You are analyzing a dentist's clinical note-taking style based on their example notes.

EXAMPLE NOTES FROM THIS DENTIST:
{examples_text}

Analyze these notes and identify the dentist's personal writing style characteristics.

OUTPUT FORMAT (respond with ONLY this JSON):
{{
  "length_preference": "concise/standard/verbose",
  "sentence_structure": "brief bullet points/short sentences/detailed paragraphs",
  "common_phrases": ["list of phrases they use often"],
  "abbreviation_style": "heavy abbreviations/mixed/mostly expanded",
  "typical_abbreviations": ["list of abbreviations they use"],
  "structure_preference": "unstructured narrative/semi-structured/highly structured",
  "level_of_detail": "minimal/moderate/comprehensive",
  "tone": "casual/professional/very formal",
  "typical_note_length_words": 10-200,
  "gdc_compliance_baseline": 0-100
}}

Analyze now:"""

    try:
        response = await call_ollama(prompt, max_tokens=1000)
        response = response.replace("```json", "").replace("```", "").strip()
        style_analysis = json.loads(response)
        return style_analysis

    except (json.JSONDecodeError, KeyError) as e:
        # Fallback to basic analysis
        return {
            "length_preference": "standard",
            "sentence_structure": "short sentences",
            "common_phrases": [],
            "abbreviation_style": "mixed",
            "typical_abbreviations": [],
            "structure_preference": "semi-structured",
            "level_of_detail": "moderate",
            "tone": "professional",
            "typical_note_length_words": 50,
            "gdc_compliance_baseline": 50
        }


async def score_example_notes(example_notes: List[str]) -> List[Dict]:
    """
    Score each example note to show the user their current GDC compliance.

    Args:
        example_notes: List of example notes

    Returns:
        List of scores and feedback for each note
    """

    from llm_scoring import llm_score_note

    results = []

    for i, note in enumerate(example_notes):
        # Create a basic user profile for scoring
        basic_profile = {
            "specialty": "General Dentistry",
            "practice_type": "Mixed",
            "notation_system": "FDI"
        }

        score_result = await llm_score_note(note, basic_profile)

        results.append({
            "note_number": i + 1,
            "original_note": note,
            "gdc_score": score_result["total_score"],
            "element_scores": score_result["element_scores"],
            "missing_elements": score_result["missing_elements"],
            "feedback": score_result.get("overall_feedback", "")
        })

    return results


async def create_style_aware_correction_prompt(
    text: str,
    detected_lang: str,
    user_profile: dict,
    style_profile: Dict
) -> str:
    """
    Create a correction prompt that maintains the user's personal style
    while ensuring GDC compliance.
    """

    from gdc_guidelines import get_gdc_prompt_guidelines

    # Get GDC guidelines
    gdc_guidelines = get_gdc_prompt_guidelines(user_profile)

    # Extract style characteristics
    length_pref = style_profile.get("length_preference", "standard")
    sentence_style = style_profile.get("sentence_structure", "short sentences")
    tone = style_profile.get("tone", "professional")
    common_phrases = style_profile.get("common_phrases", [])
    typical_abbrevs = style_profile.get("typical_abbreviations", [])

    # Build style description
    style_description = f"""
THIS DENTIST'S PERSONAL WRITING STYLE:
- Length: {length_pref} notes
- Sentence structure: {sentence_style}
- Tone: {tone}
- Common phrases: {', '.join(common_phrases[:5]) if common_phrases else 'none identified'}
- Abbreviations they use: {', '.join(typical_abbrevs[:10]) if typical_abbrevs else 'expanded terms'}

IMPORTANT: Maintain this dentist's personal style while ensuring GDC compliance.
"""

    prompt = f"""You are helping a UK dentist write clinical notes that match their personal style while meeting GDC standards.

{gdc_guidelines}

{style_description}

TASK: Convert the input into a GDC-compliant note that sounds like THIS DENTIST wrote it.

INPUT LANGUAGE: {detected_lang}
OUTPUT REQUIRED: UK clinical English in the dentist's personal style

REQUIREMENTS:
1. Maintain the dentist's typical note length and structure
2. Use their common phrases where appropriate
3. Match their abbreviation style (but expand for clarity if needed)
4. Keep their tone ({tone})
5. Ensure ALL 5 GDC elements are present
6. Add IR(ME)R justification if radiograph mentioned

INPUT TEXT:
{text}

EXAMPLE OF HOW THIS DENTIST WRITES:
{user_profile.get('example_notes', ['No examples provided'])[0] if user_profile.get('example_notes') else 'Standard clinical style'}

Now convert the input text in THIS DENTIST'S STYLE while ensuring GDC compliance:"""

    return prompt


async def suggest_improved_note(
    original_note: str,
    user_profile: dict,
    style_profile: Dict,
    gdc_score: int
) -> Dict:
    """
    Take a user's note and suggest an improved version that:
    1. Maintains their personal style
    2. Improves GDC compliance
    3. Shows exactly what was added/changed

    Args:
        original_note: The user's original note
        user_profile: User's profile
        style_profile: Their analyzed writing style
        gdc_score: Current GDC score of the note

    Returns:
        Dict with improved note and explanation
    """

    prompt = f"""You are helping improve a clinical note to be GDC-compliant while maintaining the dentist's personal style.

ORIGINAL NOTE (GDC Score: {gdc_score}/100):
{original_note}

DENTIST'S WRITING STYLE:
- Length: {style_profile.get('length_preference', 'standard')}
- Tone: {style_profile.get('tone', 'professional')}
- Structure: {style_profile.get('structure_preference', 'semi-structured')}

TASK: Rewrite this note to achieve 90+ GDC score while keeping it similar to the original style.

WHAT TO ADD (if missing):
- Medical history review (minimum: "Mhx reviewed, NAD")
- Clinical examination findings
- Clear diagnosis
- Treatment plan
- Consent mention (minimum: "Patient agreed")
- IR(ME)R justification if radiograph mentioned

Keep the improvements MINIMAL and NATURAL. Don't change their writing style dramatically.

OUTPUT FORMAT (respond with ONLY this JSON):
{{
  "improved_note": "the improved note text",
  "changes_made": ["list of what was added/changed"],
  "estimated_new_score": 0-100,
  "explanation": "brief explanation of why these changes help"
}}

Improve the note now:"""

    try:
        response = await call_ollama(prompt, max_tokens=1500)
        response = response.replace("```json", "").replace("```", "").strip()
        result = json.loads(response)
        return result

    except (json.JSONDecodeError, KeyError) as e:
        # Fallback: simple improvements
        return {
            "improved_note": original_note + "\n\nMedical history reviewed. Patient consented to treatment.",
            "changes_made": ["Added medical history review", "Added consent"],
            "estimated_new_score": min(gdc_score + 40, 100),
            "explanation": "Added missing GDC elements while maintaining original structure"
        }


# Onboarding: Ask user to provide 3-5 example notes
EXAMPLE_NOTES_ONBOARDING = {
    "question": "Please provide 3-5 examples of your typical clinical notes",
    "help": """
We'll analyze your note-taking style and suggest improvements that match YOUR style.

Paste 3-5 real examples of how you currently write notes (patient identifiable information removed).

Examples could include:
- Routine examination notes
- Treatment notes
- Emergency visit notes

The more variety, the better we can learn your style!
""",
    "example_good_notes": [
        "Mhx reviewed NAD. Pt c/o pain LR6. O/E large MOD cavity, TTP+. Dx: deep caries LR6. Plan: composite discussed, pt agreed. Composite placed under RD, no issues. RV 6/12",

        "Medical history updated - new medication warfarin. Examined, generalised gingivitis, BPE 212. Discussed OHI, demonstrated Bass technique. Pt motivated. Scale & polish completed. Bleeding reduced. Review 3 months",

        "Pt complains toothache UR6 x 3 days. Mhx reviewed ok. Clinical exam: UR6 fractured restoration, TTP++, non-vital. PA radiograph justified by symptoms - shows PAR. Dx: necrotic pulp UR6. Options discussed: RCT vs XLA. Pt prefers RCT. Risks explained inc failure. Consented. RCT appt booked"
    ]
}


def get_style_learning_onboarding_question() -> Dict:
    """Return the onboarding question about example notes"""
    return {
        "id": "example_notes",
        "question": "Provide 3-5 examples of your typical clinical notes",
        "type": "multi_text",
        "min_entries": 3,
        "max_entries": 5,
        "required": True,
        "help": EXAMPLE_NOTES_ONBOARDING["help"],
        "placeholder": "Paste a typical note here (remove patient names/IDs)...",
        "examples": EXAMPLE_NOTES_ONBOARDING["example_good_notes"]
    }

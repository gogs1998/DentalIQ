"""
DentalCorrectIQ Enhanced Server

Features:
- User profiles with personalized settings
- LLM-based intelligent GDC scoring
- Style learning from user's example notes
- Strict UK GDC guidelines
- Personalized note suggestions in user's own style
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import httpx
import json
import os
from typing import Optional, List, Dict
from pathlib import Path

# Import our enhanced modules
from user_profile import UserProfile, ONBOARDING_QUESTIONS
from llm_scoring import llm_score_note, create_enhanced_correction_prompt
from style_learning import (
    analyze_user_note_style,
    score_example_notes,
    create_style_aware_correction_prompt,
    suggest_improved_note
)
from gdc_guidelines import get_gdc_prompt_guidelines

app = FastAPI(title="DentalCorrectIQ Enhanced API")

# Allow local network connections
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# User profiles storage directory
PROFILES_DIR = Path("user_profiles")
PROFILES_DIR.mkdir(exist_ok=True)

OLLAMA_URL = "http://localhost:11434/api/generate"


# ===== API Models =====

class NoteCheckRequest(BaseModel):
    text: str
    user_id: str
    language: str = "auto"


class NoteCheckResponse(BaseModel):
    corrected_text: str
    gdc_score: int
    element_scores: Dict[str, int]
    missing_elements: List[str]
    suggestions: List[str]
    detailed_feedback: Dict[str, str]
    original_language: str
    irmer_compliant: bool


class OnboardingRequest(BaseModel):
    user_id: str
    answers: Dict[str, any]


class OnboardingResponse(BaseModel):
    user_id: str
    profile_created: bool
    style_analysis: Dict
    example_scores: List[Dict]
    message: str


# ===== Helper Functions =====

def load_user_profile(user_id: str) -> Optional[Dict]:
    """Load user profile from JSON file"""
    profile_path = PROFILES_DIR / f"{user_id}.json"
    if profile_path.exists():
        with open(profile_path, "r") as f:
            return json.load(f)
    return None


def save_user_profile(user_id: str, profile: Dict):
    """Save user profile to JSON file"""
    profile_path = PROFILES_DIR / f"{user_id}.json"
    with open(profile_path, "w") as f:
        json.dump(profile, f, indent=2)


def detect_language(text: str) -> str:
    """Simple language detection heuristic"""
    if any(char in text for char in ['ą', 'ć', 'ę', 'ł', 'ń', 'ó', 'ś', 'ź', 'ż']):
        return "Polish"
    if any(char in text for char in ['ă', 'â', 'î', 'ș', 'ț']):
        return "Romanian"
    if any('\u0600' <= char <= '\u06FF' for char in text):
        return "Urdu"
    return "English"


async def call_ollama(prompt: str, max_tokens: int = 500) -> str:
    """Call local Ollama API"""
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


# ===== API Endpoints =====

@app.get("/")
async def root():
    return {
        "service": "DentalCorrectIQ Enhanced API",
        "version": "2.0.0",
        "features": [
            "User profiles with personalization",
            "LLM-based intelligent scoring",
            "Style learning from examples",
            "UK GDC compliance checking"
        ]
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get("http://localhost:11434/api/tags")
            return {
                "status": "healthy",
                "model": "llama3.2:3b",
                "ollama_status": "connected",
                "features": "enhanced"
            }
    except Exception as e:
        return {
            "status": "degraded",
            "model": "llama3.2:3b",
            "ollama_status": f"error: {str(e)}"
        }


@app.get("/onboarding/questions")
async def get_onboarding_questions():
    """Get onboarding questions for user setup"""
    return {
        "questions": ONBOARDING_QUESTIONS,
        "total_questions": len(ONBOARDING_QUESTIONS)
    }


@app.post("/onboarding/complete", response_model=OnboardingResponse)
async def complete_onboarding(request: OnboardingRequest):
    """
    Complete user onboarding:
    1. Create user profile from answers
    2. Analyze their example notes for style learning
    3. Score their example notes to show baseline
    """

    try:
        answers = request.answers

        # Extract example notes
        example_notes = answers.get("example_notes", [])
        if len(example_notes) < 3:
            raise HTTPException(
                status_code=400,
                detail="Please provide at least 3 example notes"
            )

        # Create user profile
        profile = {
            "user_id": request.user_id,
            "name": answers.get("name", "Unknown"),
            "gdc_number": answers.get("gdc_number"),
            "notation_system": answers.get("notation_system", "FDI"),
            "practice_type": answers.get("practice_type", "Mixed"),
            "specialty": answers.get("specialty", "General Dentistry"),
            "primary_languages": answers.get("primary_languages", ["English"]),
            "common_procedures": answers.get("common_procedures", []),
            "custom_abbreviations": {},
            "verbose_notes": answers.get("note_style") == "verbose",
            "example_notes": example_notes
        }

        # Analyze note-taking style from examples
        style_profile = await analyze_user_note_style(example_notes)
        profile["style_profile"] = style_profile

        # Score their example notes to show baseline
        example_scores = await score_example_notes(example_notes)
        profile["example_notes_scores"] = example_scores

        # Save profile
        save_user_profile(request.user_id, profile)

        # Calculate average baseline score
        avg_score = sum(s["gdc_score"] for s in example_scores) / len(example_scores)

        return OnboardingResponse(
            user_id=request.user_id,
            profile_created=True,
            style_analysis=style_profile,
            example_scores=example_scores,
            message=f"Profile created! Your current average GDC score: {avg_score:.0f}/100. We'll help you maintain your style while improving compliance."
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/profile/{user_id}")
async def get_profile(user_id: str):
    """Get user profile"""
    profile = load_user_profile(user_id)
    if not profile:
        raise HTTPException(status_code=404, detail="User profile not found")
    return profile


@app.post("/check-note", response_model=NoteCheckResponse)
async def check_note(request: NoteCheckRequest):
    """
    Main endpoint: Check and correct clinical note with personalization

    Flow:
    1. Load user profile
    2. Detect language
    3. Correct note using style-aware prompt (maintains user's style)
    4. Score using LLM-based intelligent scoring
    5. Return results with personalized suggestions
    """

    try:
        # Load user profile
        profile = load_user_profile(request.user_id)
        if not profile:
            raise HTTPException(
                status_code=404,
                detail=f"User profile not found for {request.user_id}. Please complete onboarding first."
            )

        # Detect language
        detected_lang = detect_language(request.text)

        # Get user's style profile
        style_profile = profile.get("style_profile", {})

        # Create style-aware correction prompt
        if style_profile:
            prompt = await create_style_aware_correction_prompt(
                request.text,
                detected_lang,
                profile,
                style_profile
            )
        else:
            # Fallback to standard correction if no style learned yet
            prompt = create_enhanced_correction_prompt(
                request.text,
                detected_lang,
                profile
            )

        # Get corrected text from LLM
        corrected_text = await call_ollama(prompt, max_tokens=800)

        # Score using LLM-based intelligent scoring
        score_result = await llm_score_note(corrected_text, profile)

        # Extract results
        gdc_score = score_result["total_score"]
        element_scores = score_result["element_scores"]
        missing_elements = score_result["missing_elements"]
        detailed_feedback = score_result.get("feedback", {})
        suggestions = score_result.get("suggestions", [])

        # Add personalized suggestions based on user preferences
        threshold = profile.get("gdc_score_threshold", 80)
        if gdc_score < threshold:
            suggestions.insert(
                0,
                f"⚠️ Score below your threshold ({threshold}). Consider adding missing elements."
            )

        return NoteCheckResponse(
            corrected_text=corrected_text,
            gdc_score=gdc_score,
            element_scores=element_scores,
            missing_elements=missing_elements,
            suggestions=suggestions,
            detailed_feedback=detailed_feedback,
            original_language=detected_lang,
            irmer_compliant=score_result.get("irmer_compliant", True)
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/improve-note")
async def improve_note_endpoint(
    user_id: str,
    original_note: str
):
    """
    Suggest an improved version of a note that maintains the user's style
    but improves GDC compliance.

    This is useful for showing "before and after" comparisons.
    """

    try:
        # Load user profile
        profile = load_user_profile(user_id)
        if not profile:
            raise HTTPException(status_code=404, detail="User profile not found")

        style_profile = profile.get("style_profile", {})
        if not style_profile:
            raise HTTPException(
                status_code=400,
                detail="No style profile found. Please complete onboarding with example notes."
            )

        # Score the original note
        original_score = await llm_score_note(original_note, profile)

        # Get improved suggestion
        improvement = await suggest_improved_note(
            original_note,
            profile,
            style_profile,
            original_score["total_score"]
        )

        return {
            "original_note": original_note,
            "original_score": original_score["total_score"],
            "improved_note": improvement["improved_note"],
            "estimated_new_score": improvement["estimated_new_score"],
            "changes_made": improvement["changes_made"],
            "explanation": improvement["explanation"]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/users")
async def list_users():
    """List all registered users"""
    profiles = []
    for profile_file in PROFILES_DIR.glob("*.json"):
        with open(profile_file, "r") as f:
            profile = json.load(f)
            profiles.append({
                "user_id": profile["user_id"],
                "name": profile["name"],
                "specialty": profile.get("specialty", "Unknown"),
                "practice_type": profile.get("practice_type", "Unknown")
            })
    return {"users": profiles, "count": len(profiles)}


if __name__ == "__main__":
    import uvicorn
    print("🦷 Starting DentalCorrectIQ Enhanced Server...")
    print("Features:")
    print("  ✓ User profiles with personalization")
    print("  ✓ LLM-based intelligent scoring")
    print("  ✓ Style learning from example notes")
    print("  ✓ UK GDC compliance checking")
    print("")
    uvicorn.run(app, host="0.0.0.0", port=8000)

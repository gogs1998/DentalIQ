from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import httpx
import json
import re

app = FastAPI()

# Allow local network connections
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Only local network anyway
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class NoteCheckRequest(BaseModel):
    text: str
    language: str = "auto"  # auto-detect or specify

class NoteCheckResponse(BaseModel):
    corrected_text: str
    gdc_score: int
    missing_elements: list[str]
    suggestions: list[str]
    original_language: str

OLLAMA_URL = "http://localhost:11434/api/generate"

GDC_REQUIRED_ELEMENTS = {
    "medical_history": ["medical history", "mhx", "health", "medical conditions", "health questionnaire"],
    "clinical_findings": ["examined", "clinical examination", "findings", "observed"],
    "diagnosis": ["diagnosis", "dx", "diagnosed", "impression"],
    "treatment_plan": ["treatment plan", "advised", "recommended", "plan", "proposed"],
    "consent": ["consent", "agreed", "options discussed", "risks explained", "informed"]
}

def calculate_gdc_score(text: str) -> tuple[int, list[str]]:
    """Rule-based GDC compliance scoring"""
    score = 0
    missing = []
    text_lower = text.lower()

    for element, keywords in GDC_REQUIRED_ELEMENTS.items():
        if any(keyword in text_lower for keyword in keywords):
            score += 20
        else:
            missing.append(element.replace("_", " ").title())

    return score, missing

def detect_language(text: str) -> str:
    """Simple language detection heuristic"""
    # Polish character check
    if any(char in text for char in ['ą', 'ć', 'ę', 'ł', 'ń', 'ó', 'ś', 'ź', 'ż']):
        return "Polish"
    # Romanian character check
    if any(char in text for char in ['ă', 'â', 'î', 'ș', 'ț']):
        return "Romanian"
    # Urdu/Arabic script check
    if any('\u0600' <= char <= '\u06FF' for char in text):
        return "Urdu"
    # Add more language detection as needed
    return "English"

async def call_ollama(prompt: str, max_tokens: int = 500) -> str:
    """Call local Ollama API"""
    payload = {
        "model": "llama3.2:3b",
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.3,  # Low temperature for consistency
            "num_predict": max_tokens
        }
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(OLLAMA_URL, json=payload)
        response.raise_for_status()
        result = response.json()
        return result["response"].strip()

def create_correction_prompt(text: str, detected_lang: str) -> str:
    """Create prompt for LLM to correct and translate clinical notes"""
    return f"""You are a UK dental clinical documentation assistant.

INPUT LANGUAGE: {detected_lang}
OUTPUT REQUIRED: UK GDC-compliant clinical English

Your task: Convert the input into clear, professional UK dental clinical notes.

Rules:
1. If input is not English, translate to English first
2. Expand all abbreviations (pt→Patient, ul6→upper left first molar, ttp→tender to percussion)
3. Use proper UK dental terminology
4. Keep it concise and clinical
5. Maintain all clinical facts from input
6. Output ONLY the corrected clinical note, nothing else

INPUT TEXT:
{text}

CORRECTED UK CLINICAL NOTE:"""

@app.post("/check-note", response_model=NoteCheckResponse)
async def check_note(request: NoteCheckRequest):
    """Main endpoint: Check and correct clinical note"""

    try:
        # Detect language
        detected_lang = detect_language(request.text)

        # Get corrected text from LLM
        prompt = create_correction_prompt(request.text, detected_lang)
        corrected_text = await call_ollama(prompt)

        # Calculate GDC score on corrected text
        gdc_score, missing_elements = calculate_gdc_score(corrected_text)

        # Generate suggestions based on missing elements
        suggestions = []
        if "Medical History" in missing_elements:
            suggestions.append("Consider adding: 'Medical history reviewed, no changes since last visit'")
        if "Consent" in missing_elements:
            suggestions.append("Consider documenting: 'Treatment options discussed, patient consented to proposed treatment'")
        if "Clinical Findings" in missing_elements:
            suggestions.append("Consider documenting clinical examination findings")
        if "Diagnosis" in missing_elements:
            suggestions.append("Consider adding a diagnosis or clinical impression")
        if "Treatment Plan" in missing_elements:
            suggestions.append("Consider documenting the treatment plan")

        # Check for radiograph justification
        text_lower = request.text.lower() + " " + corrected_text.lower()
        if any(word in text_lower for word in ["radiograph", "x-ray", "xray", "pa", "bw", "periapical", "bitewing"]):
            if not any(word in text_lower for word in ["justified", "justification", "ir(me)r", "irmer", "clinical presentation"]):
                suggestions.append("Radiograph mentioned but no IR(ME)R justification found - required for UK compliance")

        return NoteCheckResponse(
            corrected_text=corrected_text,
            gdc_score=gdc_score,
            missing_elements=missing_elements,
            suggestions=suggestions,
            original_language=detected_lang
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Test if Ollama is accessible
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get("http://localhost:11434/api/tags")
            return {
                "status": "healthy",
                "model": "llama3.2:3b",
                "ollama_status": "connected"
            }
    except Exception as e:
        return {
            "status": "degraded",
            "model": "llama3.2:3b",
            "ollama_status": f"error: {str(e)}"
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

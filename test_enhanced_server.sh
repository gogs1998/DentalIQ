#!/bin/bash

# Test script for DentalCorrectIQ Enhanced Server (v2.0)

echo "🦷 DentalCorrectIQ Enhanced Server Tests"
echo "========================================"
echo ""

SERVER_URL="${1:-http://localhost:8000}"

echo "Testing server at: $SERVER_URL"
echo ""

# Test 1: Health check
echo "Test 1: Health Check"
echo "--------------------"
response=$(curl -s "$SERVER_URL/health")
echo "$response" | python3 -m json.tool
echo ""

# Test 2: Get onboarding questions
echo "Test 2: Get Onboarding Questions"
echo "--------------------------------"
response=$(curl -s "$SERVER_URL/onboarding/questions")
echo "$response" | python3 -m json.tool | head -50
echo "... (truncated for brevity)"
echo ""

# Test 3: Complete onboarding (create test user)
echo "Test 3: Complete Onboarding - Create Test User"
echo "-----------------------------------------------"
curl -s -X POST "$SERVER_URL/onboarding/complete" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_dentist",
    "answers": {
      "name": "Dr. Test User",
      "gdc_number": "123456",
      "notation_system": "FDI",
      "practice_type": "Mixed",
      "specialty": "General Dentistry",
      "primary_languages": ["English"],
      "common_procedures": ["Examinations", "Fillings"],
      "note_style": "standard",
      "compliance_preferences": "standard",
      "auto_suggestions": "when_low",
      "example_notes": [
        "Mhx reviewed NAD. Pt c/o pain LR6. O/E large MOD cavity, TTP+. Dx: deep caries LR6. Plan: composite discussed, pt agreed. Composite placed under RD, no issues. RV 6/12",
        "Medical history updated - new medication warfarin. Examined, generalised gingivitis, BPE 212. Discussed OHI, demonstrated Bass technique. Scale & polish completed. Review 3 months",
        "Emergency: swelling LL6. Mhx ok. Clinical exam: tender swelling buccal. PA radiograph justified by clinical presentation shows PAR. Dx: acute abscess LL6. Abx prescribed amoxicillin 500mg TDS 5 days. RCT or XLA discussed, pt prefers RCT. Appt booked 2 weeks. Advised re symptoms requiring earlier review"
      ]
    }
  }' | python3 -m json.tool

echo ""
echo ""

# Test 4: Check note with user profile
echo "Test 4: Check Note (With User Profile)"
echo "--------------------------------------"
curl -s -X POST "$SERVER_URL/check-note" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "pt c/o pain ul6 ttp",
    "user_id": "test_dentist",
    "language": "auto"
  }' | python3 -m json.tool

echo ""
echo ""

# Test 5: Improve note
echo "Test 5: Improve Note (Before/After)"
echo "-----------------------------------"
curl -s -X POST "$SERVER_URL/improve-note?user_id=test_dentist" \
  -H "Content-Type: application/json" \
  -d '"pt pain, cavity, filling done"' | python3 -m json.tool

echo ""
echo ""

# Test 6: Get user profile
echo "Test 6: Get User Profile"
echo "-----------------------"
curl -s "$SERVER_URL/profile/test_dentist" | python3 -m json.tool | head -30
echo "... (truncated for brevity)"
echo ""

# Test 7: List all users
echo "Test 7: List All Users"
echo "---------------------"
curl -s "$SERVER_URL/users" | python3 -m json.tool
echo ""

echo ""
echo "✅ All tests completed!"
echo ""
echo "Note: If any tests failed, check:"
echo "  1. Server is running (./server/run.sh)"
echo "  2. Ollama is running (ollama serve)"
echo "  3. Llama 3.2 3B model is installed (ollama list)"
echo "  4. Check server logs for errors"

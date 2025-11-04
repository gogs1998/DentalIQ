#!/bin/bash

# Quick test script for DentalCorrectIQ server

echo "🦷 DentalCorrectIQ Server Test"
echo "=============================="
echo ""

# Configuration
SERVER_URL="${1:-http://localhost:8000}"

echo "Testing server at: $SERVER_URL"
echo ""

# Test 1: Health check
echo "Test 1: Health Check"
echo "--------------------"
response=$(curl -s -w "\nHTTP_CODE:%{http_code}" "$SERVER_URL/health")
http_code=$(echo "$response" | grep "HTTP_CODE" | cut -d: -f2)
body=$(echo "$response" | sed '/HTTP_CODE/d')

if [ "$http_code" = "200" ]; then
    echo "✅ Health check passed"
    echo "$body" | python3 -m json.tool
else
    echo "❌ Health check failed (HTTP $http_code)"
    echo "$body"
    exit 1
fi

echo ""
echo ""

# Test 2: Simple English note
echo "Test 2: Simple English Note"
echo "---------------------------"
curl -s -X POST "$SERVER_URL/check-note" \
  -H "Content-Type: application/json" \
  -d '{"text": "pt c/o pain ul6 ttp"}' | python3 -m json.tool

echo ""
echo ""

# Test 3: Polish note
echo "Test 3: Polish Note (Multi-language)"
echo "------------------------------------"
curl -s -X POST "$SERVER_URL/check-note" \
  -H "Content-Type: application/json" \
  -d '{"text": "pacjent skarży się na ból ul6 ttp perc"}' | python3 -m json.tool

echo ""
echo ""

# Test 4: Note with better GDC compliance
echo "Test 4: GDC-Compliant Note"
echo "-------------------------"
curl -s -X POST "$SERVER_URL/check-note" \
  -H "Content-Type: application/json" \
  -d '{"text": "Medical history reviewed, no changes. Patient examined, caries ul6. Diagnosis: dental caries. Treatment plan: restoration discussed. Patient consented to composite filling."}' | python3 -m json.tool

echo ""
echo ""
echo "✅ All tests completed!"
echo ""
echo "Note: If LLM responses seem slow or empty, check:"
echo "  1. Ollama is running (ollama serve)"
echo "  2. Llama 3.2 3B model is installed (ollama list)"
echo "  3. Check server logs for errors"

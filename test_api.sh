#!/bin/bash

# Test script for LLM Chat API
# Tests all endpoints

API_URL="${1:-http://210.79.129.25:8000}"

echo "=========================================="
echo "Testing LLM Chat API at: $API_URL"
echo "=========================================="
echo ""

# Test health endpoint
echo "1. Testing /health endpoint..."
curl -s "${API_URL}/health" | python3 -m json.tool
echo ""

# Test teach endpoint
echo "2. Teaching model about chess..."
curl -s -X POST "${API_URL}/teach" \
  -H "Content-Type: application/json" \
  -d '{
    "knowledge": "In chess, the king can move one square in any direction. The queen can move any number of squares horizontally, vertically, or diagonally. The rook moves horizontally or vertically any number of squares.",
    "topic": "chess"
  }' | python3 -m json.tool
echo ""

sleep 2

# Test chat endpoint
echo "3. Chatting about chess..."
curl -s -X POST "${API_URL}/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "How does the king move in chess?"
  }' | python3 -m json.tool
echo ""

# Test knowledge retrieval
echo "4. Retrieving stored knowledge..."
curl -s "${API_URL}/knowledge?topic=chess" | python3 -m json.tool
echo ""

echo "=========================================="
echo "Tests complete!"
echo "=========================================="


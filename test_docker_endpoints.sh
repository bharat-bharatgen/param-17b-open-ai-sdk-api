#!/bin/bash

# Test script for BharatGen OpenAI-compatible API
# Usage: ./test_docker_endpoints.sh [PORT]

PORT=${1:-8456}
BASE_URL="http://localhost:$PORT"
API_KEY="sk-test-key"

echo "Testing BharatGen OpenAI API on port $PORT"
echo "=============================================="
echo

# Test 1: Chat Completions (Non-streaming)
echo "Test 1: Chat Completions (Non-streaming)"
echo "----------------------------------------"
curl -s -X POST "$BASE_URL/v1/chat/completions" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "bharatgen-param-17b",
    "messages": [
      {"role": "user", "content": "What is the capital of India? Answer in one sentence."}
    ],
    "temperature": 0.7,
    "max_tokens": 50
  }' | jq '.'
echo
echo

# Test 2: Chat Completions with System Message
echo "Test 2: Chat Completions with System Message"
echo "--------------------------------------------"
curl -s -X POST "$BASE_URL/v1/chat/completions" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "bharatgen-param-17b",
    "messages": [
      {"role": "system", "content": "You are a helpful assistant that speaks like a pirate."},
      {"role": "user", "content": "Tell me about India"}
    ],
    "temperature": 0.8,
    "max_tokens": 100
  }' | jq '.'
echo
echo

# Test 3: Streaming Response
echo "Test 3: Chat Completions (Streaming)"
echo "------------------------------------"
curl -s -X POST "$BASE_URL/v1/chat/completions" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "bharatgen-param-17b",
    "messages": [
      {"role": "user", "content": "Count from 1 to 5"}
    ],
    "stream": true,
    "max_tokens": 50
  }'
echo
echo
echo

# Test 4: Invalid API Key
echo "Test 4: Invalid API Key (Should Fail)"
echo "-------------------------------------"
curl -s -X POST "$BASE_URL/v1/chat/completions" \
  -H "Authorization: Bearer invalid-key" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "bharatgen-param-17b",
    "messages": [
      {"role": "user", "content": "Hello"}
    ]
  }' | jq '.'
echo
echo

# Test 5: Missing Authorization Header
echo "Test 5: Missing Authorization (Should Fail)"
echo "-------------------------------------------"
curl -s -X POST "$BASE_URL/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "bharatgen-param-17b",
    "messages": [
      {"role": "user", "content": "Hello"}
    ]
  }' | jq '.'
echo
echo

# Test 6: Temperature variations
echo "Test 6: Temperature Test (0.1 vs 0.9)"
echo "--------------------------------------"
echo "Low temperature (0.1):"
curl -s -X POST "$BASE_URL/v1/chat/completions" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "bharatgen-param-17b",
    "messages": [
      {"role": "user", "content": "Say hello"}
    ],
    "temperature": 0.1,
    "max_tokens": 20
  }' | jq '.choices[0].message.content'
echo

echo "High temperature (0.9):"
curl -s -X POST "$BASE_URL/v1/chat/completions" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "bharatgen-param-17b",
    "messages": [
      {"role": "user", "content": "Say hello"}
    ],
    "temperature": 0.9,
    "max_tokens": 20
  }' | jq '.choices[0].message.content'
echo
echo

echo "=============================================="
echo "Testing complete!"

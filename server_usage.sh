#!/bin/bash

# Example: Using the FastAPI server

echo "=========================================="
echo "BharatGen OpenAI API Server Usage Examples"
echo "=========================================="
echo ""

# Start the server in the background
echo "Starting server..."
echo "(In practice, run: python -m bharatgen_openai.server)"
echo ""

# Example 1: Non-streaming request
echo "Example 1: Non-Streaming Request"
echo "=========================================="
cat << 'EOF'
curl http://localhost:8000/v1/chat/completions \
  -H "Authorization: Bearer sk-test-key" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "bharatgen-param-17b",
    "messages": [
      {"role": "user", "content": "What is the capital of India?"}
    ],
    "temperature": 0.7
  }'
EOF
echo ""
echo ""

# Example 2: Streaming request
echo "Example 2: Streaming Request"
echo "=========================================="
cat << 'EOF'
curl http://localhost:8000/v1/chat/completions \
  -H "Authorization: Bearer sk-test-key" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "bharatgen-param-17b",
    "messages": [
      {"role": "user", "content": "Count from 1 to 5"}
    ],
    "stream": true
  }'
EOF
echo ""
echo ""

# Example 3: List models
echo "Example 3: List Models"
echo "=========================================="
cat << 'EOF'
curl http://localhost:8000/v1/models \
  -H "Authorization: Bearer sk-test-key"
EOF
echo ""
echo ""

# Example 4: Health check
echo "Example 4: Health Check"
echo "=========================================="
cat << 'EOF'
curl http://localhost:8000/health
EOF
echo ""
echo ""

# Example 5: Using with OpenAI Python SDK
echo "Example 5: Using with OpenAI Python SDK"
echo "=========================================="
cat << 'EOF'
from openai import OpenAI

# Point to local server
client = OpenAI(
    base_url="http://localhost:8000/v1",
    api_key="sk-test-key"
)

response = client.chat.completions.create(
    model="bharatgen-param-17b",
    messages=[
        {"role": "user", "content": "Hello!"}
    ]
)

print(response.choices[0].message.content)
EOF
echo ""

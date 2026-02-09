"""Test the API server endpoints."""

import requests
import json

BASE_URL = "http://localhost:8000"
API_KEY = "sk-test-key"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

print("=" * 80)
print("Testing BharatGen OpenAI-Compatible API Server")
print("=" * 80)

# Test 1: Health check
print("\n1. Testing /health endpoint")
print("-" * 80)
response = requests.get(f"{BASE_URL}/health")
print(f"Status: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2)}")

# Test 2: List models
print("\n2. Testing /v1/models endpoint")
print("-" * 80)
response = requests.get(f"{BASE_URL}/v1/models", headers=headers)
print(f"Status: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2)}")

# Test 3: Non-streaming chat completion
print("\n3. Testing /v1/chat/completions (non-streaming)")
print("-" * 80)
payload = {
    "model": "bharatgen-param-17b",
    "messages": [
        {"role": "user", "content": "Say hello in one sentence"}
    ],
    "max_tokens": 2048,
    "temperature": 0.7,
    "stream": False
}
response = requests.post(f"{BASE_URL}/v1/chat/completions", headers=headers, json=payload)
print(f"Status: {response.status_code}")
if response.status_code == 200:
    result = response.json()
    print(f"ID: {result['id']}")
    print(f"Model: {result['model']}")
    print(f"Content: {result['choices'][0]['message']['content']}")
    print(f"Tokens: {result['usage']}")
else:
    print(f"Error: {response.text}")

# Test 4: Streaming chat completion
print("\n4. Testing /v1/chat/completions (streaming)")
print("-" * 80)
payload = {
    "model": "bharatgen-param-17b",
    "messages": [
        {"role": "user", "content": "Count from 1 to 3"}
    ],
    "max_tokens": 2048,
    "temperature": 0.7,
    "stream": True
}
response = requests.post(f"{BASE_URL}/v1/chat/completions", headers=headers, json=payload, stream=True)
print(f"Status: {response.status_code}")
if response.status_code == 200:
    print("Streaming response: ", end="", flush=True)
    chunk_count = 0
    for line in response.iter_lines(decode_unicode=True):
        if line.startswith("data: "):
            data_str = line[6:]
            if data_str == "[DONE]":
                print("\n[DONE]")
                break
            try:
                chunk = json.loads(data_str)
                if chunk['choices'][0]['delta'].get('content'):
                    print(chunk['choices'][0]['delta']['content'], end="", flush=True)
                    chunk_count += 1
            except json.JSONDecodeError:
                pass
    print(f"\nReceived {chunk_count} content chunks")
else:
    print(f"Error: {response.text}")

# Test 5: Invalid API key
print("\n5. Testing authentication (invalid API key)")
print("-" * 80)
bad_headers = {
    "Authorization": "Bearer invalid-key",
    "Content-Type": "application/json"
}
response = requests.get(f"{BASE_URL}/v1/models", headers=bad_headers)
print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")

# Test 6: Missing API key
print("\n6. Testing authentication (missing API key)")
print("-" * 80)
response = requests.get(f"{BASE_URL}/v1/models")
print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")

print("\n" + "=" * 80)
print("✅ Server testing complete!")
print("=" * 80)

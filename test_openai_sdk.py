"""Test using official OpenAI Python SDK with our server."""

from openai import OpenAI

print("=" * 80)
print("Testing Official OpenAI SDK with BharatGen Server")
print("=" * 80)

# Point OpenAI SDK to our local server
client = OpenAI(
    base_url="http://localhost:8000/v1",
    api_key="sk-test-key"
)

# Test 1: List models
print("\n1. Listing models")
print("-" * 80)
models = client.models.list()
print(f"Available models: {[m.id for m in models.data]}")

# Test 2: Non-streaming completion
print("\n2. Non-streaming chat completion")
print("-" * 80)
response = client.chat.completions.create(
    model="bharatgen-param-17b",
    messages=[
        {"role": "user", "content": "What is 2+2? Answer in one sentence."}
    ],
    max_tokens=2048,
    temperature=0.7
)

print(f"Response ID: {response.id}")
print(f"Model: {response.model}")
print(f"Content: {response.choices[0].message.content}")
print(f"Finish reason: {response.choices[0].finish_reason}")
print(f"Usage: {response.usage}")

# Test 3: Streaming completion
print("\n3. Streaming chat completion")
print("-" * 80)
print("Response: ", end="", flush=True)

stream = client.chat.completions.create(
    model="bharatgen-param-17b",
    messages=[
        {"role": "user", "content": "List 3 colors"}
    ],
    max_tokens=2048,
    temperature=0.7,
    stream=True
)

chunk_count = 0
for chunk in stream:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="", flush=True)
        chunk_count += 1

print(f"\n\nReceived {chunk_count} chunks")

# Test 4: Multi-turn conversation
print("\n4. Multi-turn conversation")
print("-" * 80)
messages = [
    {"role": "system", "content": "You are a helpful math tutor."},
    {"role": "user", "content": "What is 10 + 15?"}
]

response = client.chat.completions.create(
    model="bharatgen-param-17b",
    messages=messages,
    max_tokens=2048
)

print(f"User: {messages[-1]['content']}")
print(f"Assistant: {response.choices[0].message.content}")

# Add to conversation
messages.append({"role": "assistant", "content": response.choices[0].message.content})
messages.append({"role": "user", "content": "Now multiply that by 2"})

response = client.chat.completions.create(
    model="bharatgen-param-17b",
    messages=messages,
    max_tokens=2048
)

print(f"\nUser: {messages[-1]['content']}")
print(f"Assistant: {response.choices[0].message.content}")

print("\n" + "=" * 80)
print("✅ Official OpenAI SDK works perfectly with our server!")
print("=" * 80)
print("\nThis means you can use our server as a drop-in replacement")
print("for OpenAI in any existing application that uses the OpenAI SDK.")

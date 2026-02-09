# BharatGen OpenAI API - Quick Start Guide

## Installation

```bash
cd bharatgen-param-17b
uv sync
```

## 1. Using the Python SDK

### Basic Usage

```python
from bharatgen_openai import BharatGenOpenAI

# Initialize
client = BharatGenOpenAI()

# Chat
response = client.chat.completions.create(
    messages=[
        {"role": "user", "content": "What is the capital of India?"}
    ]
)

print(response.choices[0].message.content)
```

### Streaming

```python
stream = client.chat.completions.create(
    messages=[
        {"role": "user", "content": "Count from 1 to 5"}
    ],
    stream=True
)

for chunk in stream:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="", flush=True)
```

### With System Prompt

```python
response = client.chat.completions.create(
    messages=[
        {"role": "system", "content": "You are a helpful math tutor."},
        {"role": "user", "content": "What is 15 + 27?"}
    ]
)
```

## 2. Using the API Server

### Start Server

```bash
python -m bharatgen_openai.server
```

Server will start on `http://localhost:8000`

### Make Requests

```bash
# Non-streaming
curl http://localhost:8000/v1/chat/completions \
  -H "Authorization: Bearer sk-test-key" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "bharatgen-param-17b",
    "messages": [{"role": "user", "content": "Hello!"}]
  }'

# Streaming
curl http://localhost:8000/v1/chat/completions \
  -H "Authorization: Bearer sk-test-key" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "bharatgen-param-17b",
    "messages": [{"role": "user", "content": "Count to 3"}],
    "stream": true
  }'

# List models
curl http://localhost:8000/v1/models \
  -H "Authorization: Bearer sk-test-key"
```

## 3. Using with Official OpenAI SDK

```python
from openai import OpenAI

# Point to local server
client = OpenAI(
    base_url="http://localhost:8000/v1",
    api_key="sk-test-key"
)

# Use exactly like OpenAI
response = client.chat.completions.create(
    model="bharatgen-param-17b",
    messages=[
        {"role": "user", "content": "Hello!"}
    ]
)

print(response.choices[0].message.content)
```

## Configuration

### Environment Variables

```bash
# Set Gradio API URL (if different)
export BHARATGEN_BASE_URL="https://your-gradio-instance.com/gradio_api"

# Set API keys for server
export BHARATGEN_API_KEYS="sk-prod-key1,sk-prod-key2"

# Set server port
export BHARATGEN_PORT="8000"
```

## Examples

Run the included examples:

```bash
# Python SDK examples
python examples/basic_chat.py

# View server usage examples
cat examples/server_usage.sh
```

## Common Parameters

```python
client.chat.completions.create(
    messages=[...],           # Required: List of message dicts
    model="bharatgen-param-17b",  # Optional: Model name
    temperature=0.7,          # Optional: 0.0-2.0 (default: 0.7)
    max_tokens=2048,          # Optional: Max response tokens (default: 2048)
    top_p=1.0,                # Optional: Nucleus sampling (default: 1.0)
    stream=False,             # Optional: Enable streaming (default: False)
)
```

## Troubleshooting

### Empty Responses
- Increase `max_tokens` (try 2048 or higher)
- Check that Gradio API is accessible

### Connection Errors
- Verify `BHARATGEN_BASE_URL` is correct
- Test with: `curl $BHARATGEN_BASE_URL`

### Authentication Errors
- Check API key matches `BHARATGEN_API_KEYS`
- Default key is `sk-test-key`

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Check [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) for technical details
- Explore [examples/](examples/) directory for more examples

## Support

For issues or questions:
- Check the troubleshooting section in README.md
- Review example code in examples/
- Check implementation details in source files

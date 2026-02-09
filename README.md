# BharatGen OpenAI-Compatible API

OpenAI-compatible API wrapper for BharatGen, providing both a Python SDK and REST API server.

## Features

- **🔌 Drop-in OpenAI Replacement**: Use the same interface as OpenAI's Python SDK
- **🚀 FastAPI Server**: REST API with OpenAI-compatible endpoints
- **📡 Streaming Support**: Both SDK and API support streaming responses
- **🧹 Clean Responses**: Automatically filters out thought process and debug info from Gradio responses
- **🔐 Authentication**: Bearer token authentication for API server
- **📊 Token Estimation**: Automatic token counting for usage tracking

## Installation

```bash
cd bharatgen-param-17b
uv sync
```

## Quick Start

### Using the Python SDK

```python
from bharatgen_openai import BharatGenOpenAI

# Initialize client
client = BharatGenOpenAI()

# Non-streaming
response = client.chat.completions.create(
    messages=[
        {"role": "user", "content": "What is the capital of India?"}
    ],
    temperature=0.7
)
print(response.choices[0].message.content)

# Streaming
stream = client.chat.completions.create(
    messages=[
        {"role": "user", "content": "Count from 1 to 5"}
    ],
    stream=True
)
for chunk in stream:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="")
```

### Using the API Server

**Start the server:**

```bash
python -m bharatgen_openai.server
```

**Make requests:**

```bash
curl http://localhost:8000/v1/chat/completions \
  -H "Authorization: Bearer sk-test-key" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "bharatgen-param-17b",
    "messages": [
      {"role": "user", "content": "Hello!"}
    ]
  }'
```

### Drop-in OpenAI Replacement

```python
# Instead of:
# from openai import OpenAI
# client = OpenAI(api_key="...")

# Use:
from bharatgen_openai import BharatGenOpenAI
client = BharatGenOpenAI()

# Same interface works!
response = client.chat.completions.create(
    messages=[{"role": "user", "content": "Hello!"}]
)
```

**Or point OpenAI SDK to local server:**

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8000/v1",
    api_key="sk-test-key"
)

# Existing OpenAI code works without modifications!
```

## Configuration

### Environment Variables

- `BHARATGEN_BASE_URL` - Gradio API base URL
  - Default: `https://1df79b03590242911b.gradio.live/gradio_api`
- `BHARATGEN_API_KEYS` - Comma-separated API keys for server authentication
  - Default: `sk-test-key`
- `BHARATGEN_PORT` - Server port
  - Default: `8000`
- `BHARATGEN_HOST` - Server host
  - Default: `0.0.0.0`

**Example:**

```bash
export BHARATGEN_BASE_URL="https://your-gradio-instance.com/gradio_api"
export BHARATGEN_API_KEYS="sk-prod-key1,sk-prod-key2"
export BHARATGEN_PORT="8000"
python -m bharatgen_openai.server
```

## Examples

See the `examples/` directory for more examples:

- `basic_chat.py` - SDK usage examples
- `server_usage.sh` - API server usage examples

Run the examples:

```bash
python examples/basic_chat.py
```

## Troubleshooting

### "Invalid API key" error

Make sure you're using the correct API key. Default is `sk-test-key`.

### "Connection refused" error

Make sure the server is running:

```bash
python -m bharatgen_openai.server
```

### Empty responses

Check that the Gradio API is accessible. If the URL has changed, update `BHARATGEN_BASE_URL`:

```bash
export BHARATGEN_BASE_URL="https://new-url.gradio.live/gradio_api"
```

## Documentation

For detailed API reference and architecture information, see the inline documentation in the source code.

## License

MIT
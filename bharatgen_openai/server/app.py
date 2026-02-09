"""FastAPI server for OpenAI-compatible API."""

import os
import json
from typing import Optional
from fastapi import FastAPI, HTTPException, Security, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import ValidationError

from ..models import (
    ChatCompletionRequest,
    ChatCompletion,
    ModelList,
    Model,
    ErrorResponse,
)
from ..client import BharatGenOpenAI


# Configuration
API_KEYS = set(
    os.getenv("BHARATGEN_API_KEYS", "sk-test-key").split(",")
)
BASE_URL = os.getenv(
    "BHARATGEN_BASE_URL",
    "https://1df79b03590242911b.gradio.live/gradio_api"
)
MODEL_NAME = "bharatgen-param-17b"

# Initialize FastAPI app
app = FastAPI(
    title="BharatGen OpenAI-Compatible API",
    description="OpenAI-compatible API wrapper for BharatGen",
    version="0.1.0",
)

# Security
security = HTTPBearer()


def verify_api_key(credentials: HTTPAuthorizationCredentials = Security(security)) -> str:
    """Verify API key.

    Args:
        credentials: HTTP authorization credentials

    Returns:
        API key if valid

    Raises:
        HTTPException: If API key is invalid
    """
    api_key = credentials.credentials
    if api_key not in API_KEYS:
        raise HTTPException(
            status_code=401,
            detail="Invalid API key",
        )
    return api_key


# Initialize client
client = BharatGenOpenAI(base_url=BASE_URL, model=MODEL_NAME)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}


@app.get("/v1/models")
async def list_models(api_key: str = Depends(verify_api_key)):
    """List available models.

    Returns:
        List of available models
    """
    return ModelList(
        data=[
            Model(
                id=MODEL_NAME,
                created=1706745600,
                owned_by="bharatgen",
            )
        ]
    )


@app.post("/v1/chat/completions")
async def create_chat_completion(
    request: ChatCompletionRequest,
    api_key: str = Depends(verify_api_key),
):
    """Create a chat completion.

    Args:
        request: Chat completion request
        api_key: Verified API key

    Returns:
        Chat completion response (JSON or SSE stream)
    """
    try:
        # Convert Pydantic models to dicts for client
        messages = [msg.model_dump() for msg in request.messages]

        # Call client
        response = client.chat.completions.create(
            messages=messages,
            model=request.model,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            top_p=request.top_p,
            stream=request.stream,
        )

        # Handle streaming
        if request.stream:
            return StreamingResponse(
                stream_completion(response),
                media_type="text/event-stream",
            )
        else:
            # Non-streaming response
            return response

    except ValidationError as e:
        return JSONResponse(
            status_code=400,
            content=ErrorResponse.create(
                message=f"Validation error: {str(e)}",
                type="invalid_request_error",
            ).model_dump(),
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content=ErrorResponse.create(
                message=f"Internal server error: {str(e)}",
                type="internal_error",
            ).model_dump(),
        )


async def stream_completion(completion_iterator):
    """Stream completion chunks in SSE format.

    Args:
        completion_iterator: Iterator of ChatCompletionChunk objects

    Yields:
        SSE formatted data
    """
    try:
        for chunk in completion_iterator:
            # Convert Pydantic model to dict, then to JSON
            chunk_json = json.dumps(chunk.model_dump())
            yield f"data: {chunk_json}\n\n"

        # Send [DONE] message
        yield "data: [DONE]\n\n"

    except Exception as e:
        # Send error in SSE format
        error = ErrorResponse.create(
            message=f"Streaming error: {str(e)}",
            type="internal_error",
        )
        error_json = json.dumps(error.model_dump())
        yield f"data: {error_json}\n\n"


def main():
    """Run the server."""
    import uvicorn

    port = int(os.getenv("BHARATGEN_PORT", "8000"))
    host = os.getenv("BHARATGEN_HOST", "0.0.0.0")

    print(f"Starting BharatGen OpenAI-Compatible API server on {host}:{port}")
    print(f"Base URL: {BASE_URL}")
    print(f"Model: {MODEL_NAME}")
    print(f"API Keys: {len(API_KEYS)} configured")
    print("\nEndpoints:")
    print(f"  POST http://{host}:{port}/v1/chat/completions")
    print(f"  GET  http://{host}:{port}/v1/models")
    print(f"  GET  http://{host}:{port}/health")

    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    main()

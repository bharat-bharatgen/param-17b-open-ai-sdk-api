"""OpenAI-compatible data models."""

from typing import Optional, List, Literal
from pydantic import BaseModel, Field
import time


class ChatCompletionMessage(BaseModel):
    """A chat completion message."""
    role: Literal["system", "user", "assistant"]
    content: Optional[str] = None


class Usage(BaseModel):
    """Token usage information."""
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class Choice(BaseModel):
    """A chat completion choice."""
    index: int
    message: ChatCompletionMessage
    finish_reason: Optional[Literal["stop", "length", "content_filter"]] = None


class ChatCompletion(BaseModel):
    """A chat completion response."""
    id: str
    object: Literal["chat.completion"] = "chat.completion"
    created: int
    model: str
    choices: List[Choice]
    usage: Usage


class DeltaMessage(BaseModel):
    """A delta message for streaming."""
    role: Optional[Literal["system", "user", "assistant"]] = None
    content: Optional[str] = None


class ChoiceDelta(BaseModel):
    """A streaming choice delta."""
    index: int
    delta: DeltaMessage
    finish_reason: Optional[Literal["stop", "length", "content_filter"]] = None


class ChatCompletionChunk(BaseModel):
    """A streaming chat completion chunk."""
    id: str
    object: Literal["chat.completion.chunk"] = "chat.completion.chunk"
    created: int
    model: str
    choices: List[ChoiceDelta]


class Model(BaseModel):
    """A model description."""
    id: str
    object: Literal["model"] = "model"
    created: int
    owned_by: str


class ModelList(BaseModel):
    """List of available models."""
    object: Literal["list"] = "list"
    data: List[Model]


class ChatCompletionRequest(BaseModel):
    """Request for chat completion."""
    model: str
    messages: List[ChatCompletionMessage]
    temperature: Optional[float] = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(default=None, ge=1)
    stream: Optional[bool] = False
    top_p: Optional[float] = Field(default=1.0, ge=0.0, le=1.0)
    n: Optional[int] = Field(default=1, ge=1)
    stop: Optional[List[str]] = None


class ErrorResponse(BaseModel):
    """Error response."""
    error: dict

    @classmethod
    def create(cls, message: str, type: str = "invalid_request_error", code: Optional[str] = None):
        """Create an error response."""
        error_dict = {
            "message": message,
            "type": type,
        }
        if code:
            error_dict["code"] = code
        return cls(error=error_dict)


def create_chat_completion(
    completion_id: str,
    model: str,
    content: str,
    prompt_tokens: int,
    completion_tokens: int,
) -> ChatCompletion:
    """Create a ChatCompletion object.

    Args:
        completion_id: Unique completion ID
        model: Model name
        content: Assistant's response content
        prompt_tokens: Number of tokens in prompt
        completion_tokens: Number of tokens in completion

    Returns:
        ChatCompletion object
    """
    return ChatCompletion(
        id=completion_id,
        created=int(time.time()),
        model=model,
        choices=[
            Choice(
                index=0,
                message=ChatCompletionMessage(role="assistant", content=content),
                finish_reason="stop",
            )
        ],
        usage=Usage(
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=prompt_tokens + completion_tokens,
        ),
    )


def create_chat_completion_chunk(
    completion_id: str,
    model: str,
    content: Optional[str] = None,
    role: Optional[Literal["assistant"]] = None,
    finish_reason: Optional[Literal["stop", "length", "content_filter"]] = None,
) -> ChatCompletionChunk:
    """Create a ChatCompletionChunk object.

    Args:
        completion_id: Unique completion ID
        model: Model name
        content: Delta content (new text since last chunk)
        role: Role (only in first chunk)
        finish_reason: Finish reason (only in last chunk)

    Returns:
        ChatCompletionChunk object
    """
    return ChatCompletionChunk(
        id=completion_id,
        created=int(time.time()),
        model=model,
        choices=[
            ChoiceDelta(
                index=0,
                delta=DeltaMessage(role=role, content=content),
                finish_reason=finish_reason,
            )
        ],
    )

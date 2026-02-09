"""OpenAI-compatible client SDK for BharatGen."""

import os
import uuid
from typing import Optional, Iterator, Union, List
import requests

from .models import (
    ChatCompletion,
    ChatCompletionChunk,
    ChatCompletionMessage,
    create_chat_completion,
    create_chat_completion_chunk,
)
from .parser import GradioResponseParser
from .adapters.gradio_adapter import estimate_tokens, format_messages_for_gradio


class ChatCompletions:
    """Chat completions API."""

    def __init__(self, base_url: str, model: str):
        """Initialize chat completions.

        Args:
            base_url: Base URL of Gradio API
            model: Model name
        """
        self.base_url = base_url
        self.model = model
        self.parser = GradioResponseParser()

    def _call_gradio_api(
        self,
        message: str,
        chat_history: list,
        system_prompt: Optional[str],
        temperature: float,
        max_tokens: Optional[int],
        top_p: float,
        stream: bool,
    ) -> requests.Response:
        """Call the Gradio API.

        Args:
            message: Current user message
            chat_history: Previous conversation history
            system_prompt: System prompt
            temperature: Sampling temperature
            max_tokens: Max tokens in response
            top_p: Nucleus sampling parameter
            stream: Whether to stream response

        Returns:
            Response object
        """
        # Default values
        if system_prompt is None:
            system_prompt = "You are a helpful AI assistant. You think step-by-step."
        if max_tokens is None:
            max_tokens = 2048

        # Step 1: Get event ID
        payload = {
            "data": [
                message,
                chat_history,
                system_prompt,
                temperature,
                max_tokens,
                top_p,
                50,  # top_k parameter
            ]
        }

        response = requests.post(f"{self.base_url}/call/chat_fn_1", json=payload)
        event_id = response.json().get("event_id")

        # Step 2: Get streaming response
        # Note: Always use stream=True for HTTP request because Gradio returns SSE format
        stream_url = f"{self.base_url}/call/chat_fn_1/{event_id}"
        response = requests.get(stream_url, stream=True)

        return response

    def create(
        self,
        messages: List[dict],
        model: Optional[str] = None,
        temperature: Optional[float] = 0.7,
        max_tokens: Optional[int] = None,
        top_p: Optional[float] = 1.0,
        stream: Optional[bool] = False,
        **kwargs,
    ) -> Union[ChatCompletion, Iterator[ChatCompletionChunk]]:
        """Create a chat completion.

        Args:
            messages: List of message dicts with 'role' and 'content'
            model: Model name (uses instance model if not provided)
            temperature: Sampling temperature (0-2)
            max_tokens: Max tokens in response
            top_p: Nucleus sampling (0-1)
            stream: Whether to stream response
            **kwargs: Additional parameters (ignored)

        Returns:
            ChatCompletion for non-streaming, Iterator[ChatCompletionChunk] for streaming
        """
        if model is None:
            model = self.model

        # Convert OpenAI message format to Gradio format
        current_message, chat_history, system_prompt = format_messages_for_gradio(messages)

        # Generate unique completion ID
        completion_id = f"chatcmpl-{uuid.uuid4().hex[:24]}"

        # Call Gradio API
        response = self._call_gradio_api(
            message=current_message,
            chat_history=chat_history,
            system_prompt=system_prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
            stream=stream,
        )

        # Calculate prompt tokens
        prompt_text = system_prompt or ""
        for msg in messages:
            prompt_text += msg.get("content", "")
        prompt_tokens = estimate_tokens(prompt_text)

        if stream:
            return self._create_streaming_completion(
                response, completion_id, model, prompt_tokens
            )
        else:
            return self._create_completion(response, completion_id, model, prompt_tokens)

    def _create_completion(
        self, response: requests.Response, completion_id: str, model: str, prompt_tokens: int
    ) -> ChatCompletion:
        """Create a non-streaming completion.

        Args:
            response: Gradio API response
            completion_id: Unique completion ID
            model: Model name
            prompt_tokens: Number of prompt tokens

        Returns:
            ChatCompletion object
        """
        # Parse complete response
        content = self.parser.parse_complete_response(response)

        if content is None:
            content = ""

        # Estimate completion tokens
        completion_tokens = estimate_tokens(content)

        return create_chat_completion(
            completion_id=completion_id,
            model=model,
            content=content,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
        )

    def _create_streaming_completion(
        self, response: requests.Response, completion_id: str, model: str, prompt_tokens: int
    ) -> Iterator[ChatCompletionChunk]:
        """Create a streaming completion.

        Args:
            response: Gradio API response
            completion_id: Unique completion ID
            model: Model name
            prompt_tokens: Number of prompt tokens

        Yields:
            ChatCompletionChunk objects
        """
        # First chunk with role
        yield create_chat_completion_chunk(
            completion_id=completion_id,
            model=model,
            role="assistant",
        )

        # Stream content deltas
        for delta in self.parser.parse_streaming_response(response):
            yield create_chat_completion_chunk(
                completion_id=completion_id,
                model=model,
                content=delta,
            )

        # Final chunk with finish_reason
        yield create_chat_completion_chunk(
            completion_id=completion_id,
            model=model,
            finish_reason="stop",
        )


class Chat:
    """Chat API."""

    def __init__(self, base_url: str, model: str):
        """Initialize chat API.

        Args:
            base_url: Base URL of Gradio API
            model: Model name
        """
        self.completions = ChatCompletions(base_url, model)


class BharatGenOpenAI:
    """OpenAI-compatible client for BharatGen."""

    def __init__(
        self,
        base_url: Optional[str] = None,
        model: str = "bharatgen-param-17b",
        api_key: Optional[str] = None,
    ):
        """Initialize BharatGen OpenAI client.

        Args:
            base_url: Base URL of Gradio API (defaults to env var BHARATGEN_BASE_URL)
            model: Model name
            api_key: API key (not currently used, for compatibility)
        """
        if base_url is None:
            base_url = os.getenv(
                "BHARATGEN_BASE_URL",
                "https://1df79b03590242911b.gradio.live/gradio_api"
            )

        self.base_url = base_url
        self.model = model
        self.api_key = api_key
        self.chat = Chat(base_url, model)

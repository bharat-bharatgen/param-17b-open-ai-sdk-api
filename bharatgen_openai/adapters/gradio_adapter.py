"""Utilities for Gradio API format conversion."""

import re
from typing import Optional


def estimate_tokens(text: str) -> int:
    """Estimate token count using character-based approximation.

    OpenAI typically uses ~4 characters per token as a rough estimate.

    Args:
        text: Input text

    Returns:
        Estimated token count
    """
    if not text:
        return 0
    return max(1, len(text) // 4)


def extract_metadata(html: str) -> dict:
    """Extract metadata (latency, etc.) from Gradio HTML response.

    Args:
        html: HTML response from Gradio

    Returns:
        Dictionary with extracted metadata
    """
    metadata = {}

    # Extract latency information
    latency_pattern = r'Latency:\s*([\d.]+)\s*s'
    match = re.search(latency_pattern, html)
    if match:
        metadata['latency'] = float(match.group(1))

    # Extract processing time
    time_pattern = r'Processing time:\s*([\d.]+)\s*s'
    match = re.search(time_pattern, html)
    if match:
        metadata['processing_time'] = float(match.group(1))

    return metadata


def format_messages_for_gradio(messages: list) -> tuple[str, list, Optional[str]]:
    """Convert OpenAI message format to Gradio format.

    OpenAI format:
        [
            {"role": "system", "content": "You are helpful"},
            {"role": "user", "content": "Hi"},
            {"role": "assistant", "content": "Hello!"},
            {"role": "user", "content": "How are you?"}
        ]

    Gradio format:
        chat(
            message="How are you?",  # Last user message
            chat_history=[["Hi", "Hello!"]],  # Previous exchanges
            system_prompt="You are helpful"  # System message
        )

    Args:
        messages: List of message dicts in OpenAI format

    Returns:
        Tuple of (current_message, chat_history, system_prompt)
    """
    system_prompt = None
    chat_history = []
    current_message = ""

    # Extract system prompt (first system message)
    if messages and messages[0].get("role") == "system":
        system_prompt = messages[0].get("content")
        messages = messages[1:]

    # Build chat history and get current message
    user_msg = None
    for msg in messages:
        role = msg.get("role")
        content = msg.get("content", "")

        if role == "user":
            # If we have a pending user message, pair it with None
            if user_msg is not None:
                chat_history.append([user_msg, None])
            user_msg = content
        elif role == "assistant":
            # Pair with previous user message
            if user_msg is not None:
                chat_history.append([user_msg, content])
                user_msg = None
            else:
                # Assistant message without user message (shouldn't happen normally)
                chat_history.append([None, content])

    # The last user message becomes the current message
    if user_msg is not None:
        current_message = user_msg
    else:
        # No user message at end, use empty string
        current_message = ""

    return current_message, chat_history, system_prompt

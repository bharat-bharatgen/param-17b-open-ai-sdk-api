"""Basic chat examples using BharatGen OpenAI-compatible client."""

from bharatgen_openai import BharatGenOpenAI


def example_non_streaming():
    """Example: Non-streaming chat completion."""
    print("=" * 80)
    print("Example 1: Non-Streaming Chat")
    print("=" * 80)

    client = BharatGenOpenAI()

    response = client.chat.completions.create(
        messages=[
            {"role": "user", "content": "What is the capital of India?"}
        ],
        temperature=0.7,
    )

    print(f"Response ID: {response.id}")
    print(f"Model: {response.model}")
    print(f"Content: {response.choices[0].message.content}")
    print(f"Tokens - Prompt: {response.usage.prompt_tokens}, "
          f"Completion: {response.usage.completion_tokens}, "
          f"Total: {response.usage.total_tokens}")
    print()


def example_streaming():
    """Example: Streaming chat completion."""
    print("=" * 80)
    print("Example 2: Streaming Chat")
    print("=" * 80)

    client = BharatGenOpenAI()

    print("Assistant: ", end="", flush=True)

    stream = client.chat.completions.create(
        messages=[
            {"role": "user", "content": "Count from 1 to 5 and explain each number."}
        ],
        temperature=0.7,
        stream=True,
    )

    for chunk in stream:
        if chunk.choices[0].delta.content:
            print(chunk.choices[0].delta.content, end="", flush=True)

    print("\n")


def example_conversation():
    """Example: Multi-turn conversation."""
    print("=" * 80)
    print("Example 3: Multi-Turn Conversation")
    print("=" * 80)

    client = BharatGenOpenAI()

    messages = [
        {"role": "system", "content": "You are a helpful math tutor."},
        {"role": "user", "content": "What is 15 + 27?"},
    ]

    # First turn
    response = client.chat.completions.create(
        messages=messages,
        temperature=0.7,
    )

    assistant_response = response.choices[0].message.content
    print(f"User: {messages[-1]['content']}")
    print(f"Assistant: {assistant_response}")
    print()

    # Add to conversation history
    messages.append({"role": "assistant", "content": assistant_response})
    messages.append({"role": "user", "content": "Now multiply that result by 2."})

    # Second turn
    response = client.chat.completions.create(
        messages=messages,
        temperature=0.7,
    )

    print(f"User: {messages[-1]['content']}")
    print(f"Assistant: {response.choices[0].message.content}")
    print()


def example_custom_parameters():
    """Example: Custom parameters."""
    print("=" * 80)
    print("Example 4: Custom Parameters")
    print("=" * 80)

    client = BharatGenOpenAI()

    response = client.chat.completions.create(
        messages=[
            {"role": "user", "content": "Write a haiku about coding."}
        ],
        temperature=0.9,  # More creative
        max_tokens=100,   # Limit response length
        top_p=0.95,
    )

    print(f"Content: {response.choices[0].message.content}")
    print()


def example_openai_compatibility():
    """Example: Drop-in replacement for OpenAI SDK."""
    print("=" * 80)
    print("Example 5: OpenAI SDK Compatibility")
    print("=" * 80)
    print("This client can replace OpenAI SDK with minimal changes:")
    print()
    print("# Instead of:")
    print("# from openai import OpenAI")
    print("# client = OpenAI(api_key='...')")
    print()
    print("# Use:")
    print("# from bharatgen_openai import BharatGenOpenAI")
    print("# client = BharatGenOpenAI()")
    print()
    print("# The rest of the code remains the same!")
    print()


if __name__ == "__main__":
    # Run all examples
    try:
        example_non_streaming()
        example_streaming()
        example_conversation()
        example_custom_parameters()
        example_openai_compatibility()

        print("=" * 80)
        print("All examples completed successfully!")
        print("=" * 80)

    except Exception as e:
        print(f"\nError running examples: {e}")
        print("\nMake sure:")
        print("1. The Gradio API is accessible")
        print("2. BHARATGEN_BASE_URL is set correctly (if needed)")
        print("3. All dependencies are installed (uv sync)")

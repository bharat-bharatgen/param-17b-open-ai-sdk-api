import requests


def chat(base_url, message, chat_history=None, system_prompt=None,
         temperature=0.7, max_tokens=2048, top_p=0.9):
    """
    Send a chat message to the Gradio API and get raw response.

    Args:
        base_url: Base URL of the Gradio API
        message: The user message to send
        chat_history: List of previous messages (default: [])
        system_prompt: System prompt for the AI
        temperature: Sampling temperature (default: 0.7)
        max_tokens: Maximum tokens in response (default: 2048)
        top_p: Nucleus sampling parameter (default: 0.9)

    Returns:
        Raw response text from the API
    """
    if chat_history is None:
        chat_history = []
    if system_prompt is None:
        system_prompt = "You are a helpful AI assistant. You think step-by-step."

    # Step 1: Get event ID
    payload = {
        "data": [message, chat_history, system_prompt,
                temperature, max_tokens, top_p, 50]
    }

    response = requests.post(f"{base_url}/call/chat_fn_1", json=payload)
    event_id = response.json().get("event_id")

    # Step 2: Get streaming response
    stream_url = f"{base_url}/call/chat_fn_1/{event_id}"
    response = requests.get(stream_url, stream=False)

    return response.text


if __name__ == "__main__":
    base_url = "https://1df79b03590242911b.gradio.live/gradio_api"

    print("Raw API Response:")
    print("=" * 80)
    response = chat(base_url, "Hi")
    print(response)

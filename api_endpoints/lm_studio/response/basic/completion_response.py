def response(response, model, usage=None):
    if usage is None:
        usage = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
    return {
        "id": "chatcmpl-gg711phlqdwixyxif16bm",
        "object": "chat.completion",
        "created": 1722418755,
        "model": model,
        "choices": [
            {
                "index": 0,
                "message": {"role": "assistant", "content": response},
                "finish_reason": "stop",
            }
        ],
        "usage": usage,
    }

import json
import pprint
import time

from app import app, logging
from flask import request, jsonify, Response
from backend import list_model, prompt_completion
import uuid

logger = logging.getLogger(__name__)

def start_response(rid, model):
    return {
        "id": f"chatcmpl-{rid}",
        "object": "chat.completion.chunk",
        "created": 1716456766,
        "model": model,
        "choices": [
            {
                "index": 0,
                "delta": {
                    "role": "assistant",
                    "content": ""
                },
                "finish_reason": None
            }
        ]
    }

def end_response(rid, model):
    return {
        "id": f"chatcmpl-{rid}",
        "object": "chat.completion.chunk",
        "created": 1716456766,
        "model": model,
        "choices": [
            {
                "index": 0,
                "delta": {},
                "finish_reason": "stop"
            }
        ]
    }

def stream_data_response(msg):
    return "data: " + json.dumps(msg) + '\n\n'
def generate_json_data(response, model):
    request_id = str(uuid.uuid4())
    logger.debug(f"Response {response}")

    yield stream_data_response({
        "id": f"chatcmpl-{request_id}",
        "object": "chat.completion.chunk",
        "created": 1716456766,
        "model": model,
        "choices": [
            {
                "index": 0,
                "delta": {
                    "role": "assistant",
                    "content": response
                },
                "finish_reason": None
            }
        ]
    })

    yield stream_data_response(end_response(request_id, model))

    yield "data: [DONE]\n\n"

@app.route('/chat/completions', methods=['POST'])
@app.route('/v1/chat/completions', methods=['POST'])
def chat_completions():
    try:
        post_json_data = request.json
    except:
        post_json_data = json.loads(request.data.decode())

    msg = post_json_data["messages"]
    model = post_json_data.get("model") or "openai/gpt-3.5-turbo-0125"
    streaming = post_json_data.get("stream", True)
    response = prompt_completion(json.dumps(msg, indent=True), model)
    if streaming:
        return Response(generate_json_data(response,model), content_type='text/event-stream')
    else:
        return jsonify({
  "id": "chatcmpl-gg711phlqdwixyxif16bm",
  "object": "chat.completion",
  "created": 1722418755,
  "model": model,
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": response
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 426,
    "completion_tokens": 65,
    "total_tokens": 491
  }
}), 200

@app.route('/v1/completions', methods=['POST'])
def completions():
    msg = request.json["prompt"]
    model = request.json("model") or "openai/gpt-3.5-turbo-0125"
    logger.debug(msg)
    if request.method == 'POST':
        return Response(generate_json_data(msg,model), content_type='text/event-stream')
    else:
        return jsonify({"error": "Method not allowed"}), 405

@app.route('/api/models', methods=["GET"])
@app.route('/v1/api/models', methods=["GET"])
@app.route('/v1/models', methods=["GET"])
@app.route('/models', methods=["GET"])
def lmstudio_list_models():
    """
    {'name': 'Anthropic: Claude 3 Haiku',
   'model': 'anthropic/claude-3-haiku:beta',
   'pricing': {'coins': 1, 'words': 100}}
    """
    models = list_model().get("data")
    if models is None:
        return jsonify({"models": []})

    if "chat" in models:
        models = models["chat"]

    models = [{
                "id": model["model"],
                "object": "model",
                "owned_by": model["name"].split(":")[0],
                "permission": [
                    {}
                ]
            } for model in models]
    response = {
        "data": models,
        "object": "list"
    }
    return jsonify(response)


@app.route('/v1/images/generations', methods=["POST"])
def generate_image():
    try:
        post_json_data = request.json
    except:
        post_json_data = json.loads(request.data.decode())
    pprint.pprint((post_json_data))
    import base64
    with open("./test.png","rb") as reader:
        bin_image = reader.read(-1)
        data = base64.encodebytes(bin_image).decode()

    #  1024x1024, 1024x1792 or 1792x1024
    # {'model': 'dall-e-2',
    #  'n': 1,
    #  'prompt': 'Hello! How can I assist you today?',
    #  'response_format': 'b64_json',
    #  'size': '512x512'}

    # output
    # {
    #     "created": 1589478378,
    #     "data": [
    #         {
    #             "url": "https://..."
    #         },
    #         {
    #             "url": "https://..."
    #         }
    #     ]
    # }
    return {
        "created": 1589478378,
        "data": [
            {
                "b64_json": data
            }
        ]
    }, 200




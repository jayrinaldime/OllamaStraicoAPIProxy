import json

from httpx import AsyncClient

from app import app, logging, TIMEOUT
from fastapi import Request
from fastapi.responses import JSONResponse, StreamingResponse
from backend import prompt_completion
from aio_straico.utils.tracing import observe, tracing_context
from .response.stream.completion_response import generate_ollama_stream, response_stream
from api_endpoints.response_utils import (
    fix_escaped_characters,
    load_json_with_fixed_escape,
)
from enum import Enum
from asyncio import create_task, sleep

logger = logging.getLogger(__name__)


@app.post("/api/generate")
@observe
async def ollamagenerate(request: Request):
    try:
        msg = await request.json()
    except:
        msg = json.loads((await request.body()).decode())

    request_msg = msg["prompt"]
    model = msg.get("model")

    tracing_context.update_current_observation(input=dict(msg))

    settings = {}
    if "options" in msg:
        options = msg["options"]
        settings["temperature"] = options.get("temperature")
        settings["max_tokens"] = options.get("max_tokens")

    if msg.get("stream") == False:
        response, thinking_text, _ = await prompt_completion(
            msg["prompt"], model=model, **settings
        )
        return JSONResponse(
            content={
                "model": model,
                "created_at": "2023-08-04T19:22:45.499127Z",
                "response": response,
                "done": True,
                "total_duration": 10706818083,
                "load_duration": 6338219291,
                "prompt_eval_count": 26,
                "prompt_eval_duration": 130079000,
                "eval_count": 259,
                "eval_duration": 4232710000,
            }
        )
    response, thinking_text, _ = await prompt_completion(request_msg, model=model)
    response = fix_escaped_characters(response)
    return StreamingResponse(
        generate_ollama_stream(response, model), media_type="application/x-ndjson"
    )


class ResponseType(Enum):
    Tool = "tool"
    Stream = "stream"
    Basic = "basic"


async def process_chat(msg, timeout=TIMEOUT):
    model = msg["model"]
    tools = msg.get("tools")
    messages = msg["messages"]
    format = msg.get("format")
    expected_json_response = False
    settings = {}
    if "options" in msg:
        options = msg["options"]
        settings["temperature"] = options.get("temperature")
        settings["max_tokens"] = options.get("max_tokens")

    tracing_context.update_current_observation(input=dict(msg))

    if format is not None and isinstance(format, dict):
        expected_json_response = True
        parent_format = [
            {
                "role": "system",
                "content": f"""
# OUTPUT: 
- Be sure that all outputs are JSON-compatible. 
- Output ONLY the JSON. 
- Do not include any preface or any other comments. 
- Do NOT use markup. 
- The output MUST be plain JSON with no other formatting or markup. 
- Include every part of the JSON FORMAT, even if a response is missing. 
- The Output MUST begin with {{ and the Output MUST end with }}

# JSON FORMAT:
``` json
{json.dumps(format, indent=True, ensure_ascii=False)}       
``` 
""".strip(),
            }
        ]
        messages = parent_format + messages
    # elif isinstance(messages, list) and isinstance(messages[-1], dict) and "role" in messages[-1] and messages[-1]["role"] == "tool":
    #     # dont add the tool
    #     expected_json_response = False
    elif tools and len(tools) != 0:
        expected_json_response = True
        parent_tool = [
            {
                "role": "system",
                "tools": tools,
                "content": """
If you need to use a tool to answer please use the defined tools. 
Assuming the function is 
```
{"tools":[{"type":"function","function":{"name":"get_current_weather","description":"Get the current weather for a location","parameters":{"type":"object","properties":{"location":{"type":"string","description":"The location to get the weather for, e.g. San Francisco, CA"},"format":{"type":"string","description":"The format to return the weather in, e.g. 'celsius' or 'fahrenheit'","enum":["celsius","fahrenheit"]}},"required":["location","format"]}}}]}
```
When you do use a function your output should be like
``` 
{"tool_calls":[{"function":{"name":"get_current_weather","arguments":{"format":"celsius","location":"Paris, FR"}}}]}
``` 
You must answer by exactly following the provided instructions. Do not add any additional comments or explanations.
Do not add "Here is..." or anything like that.

Act like a script, you are given an optional input and the instructions to perform, you answer with the output of the requested task.

You must respond in valid JSON when using a function. Don't wrap the response in a markdown code.
                    """.strip(),
            }
        ]
        messages = parent_tool + messages

    if "stream" in msg:
        streaming = msg.get("stream")
    else:
        streaming = True

    images = None
    if isinstance(messages, list) and len(messages) >= 1 and type(messages[0]) == dict:
        images = []
        new_messages = []
        for message in messages:
            if "images" in message:
                img = message["images"]
                if len(img) > 0:
                    images += img
                del message["images"]
            new_messages.append(message)
        messages = new_messages

    request_msg = json.dumps(messages, indent=True, ensure_ascii=False)
    response, thinking_text, _ = await prompt_completion(
        request_msg, images, model, timeout=timeout, **settings
    )
    if not msg.get("think", False):
        thinking_text = None
    try:
        response = load_json_with_fixed_escape(response)
        response_type = type(response)
        if response_type == dict and "content" in response:
            response = response["content"]
        elif (
            response_type == list
            and len(response) > 0
            and type(response[0]) == dict
            and "content" in response[0]
        ):
            response = response[0]["content"]
    except:
        pass
    response_type = type(response)

    original_response = response
    if expected_json_response:
        if response_type == str:
            response = response.strip()
            if response.startswith("```json") and response.endswith("```"):
                response = response[7:-3].strip()
                response = load_json_with_fixed_escape(response)
            elif response.startswith("```") and response.endswith("```"):
                response = response[3:-3].strip()
                try:
                    response = load_json_with_fixed_escape(response)
                except:
                    first_space_index = min(response.find("\n"), response.find(" "))
                    response = response[first_space_index:-3].strip()
            else:
                try:
                    response = load_json_with_fixed_escape(response)
                except:
                    pass
        if isinstance(response, list) and len(response) > 0:
            response = response[0]

        if isinstance(response, dict) and len(tools) > 0:
            if "tool_calls" not in response:
                logger.warning(f"tool_calling response has incorrect format {response}")
                first_function_name = tools[0]["function"]["name"]
                response = {
                    "tool_calls": [
                        {
                            "function": {
                                "name": first_function_name,
                                "arguments": response,
                            }
                        }
                    ]
                }

            return ResponseType.Tool, model, response["tool_calls"], thinking_text

    response_type = type(response)
    if len(messages) > 1 and response_type == str:
        response = response.strip()
        if response.startswith("```json") and response.endswith("```"):
            response = response[7:-3].strip()
            original_response = load_json_with_fixed_escape(response)
        elif response.startswith("```") and response.endswith("```"):
            response = response[3:-3].strip()
            original_response = load_json_with_fixed_escape(response)
        else:
            try:
                original_response = load_json_with_fixed_escape(response)

            except:
                pass

            if (
                isinstance(original_response, dict)
                and "role" in original_response
                and original_response["role"] == "assistant"
                and "content" in original_response
            ):
                original_response = original_response["content"]

    if type(original_response) in [dict, list]:
        original_response = json.dumps(original_response, ensure_ascii=False)

    elif type(response) in [dict, list]:
        original_response = json.dumps(response, ensure_ascii=False)
    else:
        try:
            original_response = fix_escaped_characters(original_response)
        except:
            pass

    if streaming:
        return ResponseType.Stream, model, original_response, thinking_text
    else:
        return ResponseType.Basic, model, original_response, thinking_text


async def background_processed_chat(msg):
    webhook_url = msg["webhook_url"]
    webhook_headers = msg.get("webhook_headers", {})
    del msg["webhook_url"]
    if "webhook_headers" in msg:
        del msg["webhook_headers"]

    response_type, model, response = await process_chat(
        msg, timeout=None
    )  # timeout none means no timeout wait forever

    if response_type == ResponseType.Tool:
        response_json = {
            "model": model,
            "created_at": "2024-07-22T20:33:28.123648Z",
            "message": {
                "role": "assistant",
                "content": "",
                "tool_calls": response,
            },
            "done_reason": "stop",
            "done": True,
            "total_duration": 885095291,
            "load_duration": 3753500,
            "prompt_eval_count": 122,
            "prompt_eval_duration": 328493000,
            "eval_count": 33,
            "eval_duration": 552222000,
        }
    else:
        response_json = {
            "model": model,
            "created_at": "2023-12-12T14:13:43.416799Z",
            "message": {"role": "assistant", "content": response},
            "done": True,
            "total_duration": 5191566416,
            "load_duration": 2154458,
            "prompt_eval_count": 26,
            "prompt_eval_duration": 383809000,
            "eval_count": 298,
            "eval_duration": 4799921000,
        }
    async with AsyncClient(timeout=60) as session:
        r = await session.post(webhook_url, json=response_json, headers=webhook_headers)
        logger.debug(f"Called Webhook: {webhook_url} status code: {r.status_code}")


@app.post("/api/chat")
@observe
async def ollamachat(request: Request):
    try:
        msg = await request.json()
    except:
        msg = json.loads((await request.body()).decode())

    if msg.get("webhook_url") is not None:
        create_task(background_processed_chat(msg))
        return JSONResponse(content={"status": "processing"})

    response_type, model, response, thinking_text = await process_chat(msg)
    if response_type == ResponseType.Tool:
        return JSONResponse(
            content={
                "model": model,
                "created_at": "2024-07-22T20:33:28.123648Z",
                "message": {
                    "role": "assistant",
                    "content": "",
                    "thinking": thinking_text,
                    "tool_calls": response,
                },
                "done_reason": "stop",
                "done": True,
                "total_duration": 885095291,
                "load_duration": 3753500,
                "prompt_eval_count": 122,
                "prompt_eval_duration": 328493000,
                "eval_count": 33,
                "eval_duration": 552222000,
            }
        )
    elif response_type == ResponseType.Stream:
        return StreamingResponse(
            response_stream(model, response, thinking_text, is_tool=False),
            media_type="application/x-ndjson",
        )
    elif response_type == ResponseType.Basic:
        return JSONResponse(
            content={
                "model": model,
                "created_at": "2023-12-12T14:13:43.416799Z",
                "message": {
                    "role": "assistant",
                    "content": response,
                    "thinking": thinking_text,
                },
                "done": True,
                "total_duration": 5191566416,
                "load_duration": 2154458,
                "prompt_eval_count": 26,
                "prompt_eval_duration": 383809000,
                "eval_count": 298,
                "eval_duration": 4799921000,
            }
        )

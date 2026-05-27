import json
from fastapi import Request
from fastapi.responses import JSONResponse, StreamingResponse
from app import app, logging
from backend import prompt_completion
from .response.stream.completion_response import (
    streamed_response,
    streamed_response_toolcall,
)
from .response.basic.completion_response import response as basic_response
from random import randint
from aio_straico.utils.tracing import observe, tracing_context
from api_endpoints.response_utils import (
    fix_escaped_characters,
    load_json_with_fixed_escape,
)

import re

logger = logging.getLogger(__name__)


def extract_images_from_messages(msgs):
    images = []
    for msg in msgs:
        if "content" not in msg or not isinstance(msg["content"], list):
            continue
        to_remove_index = []
        for index, content in enumerate(msg["content"]):
            if isinstance(content, dict) and content.get("type") == "image_url":
                data = content["image_url"]["url"]
                starting_index = data.find(",")
                images.append(data[starting_index + 1 :])
                to_remove_index.append(index)
        to_remove_index.reverse()
        for remove_index in to_remove_index:
            del msg["content"][remove_index]
    return images, msgs


@app.post("/chat/completions")
@app.post("/v1/chat/completions")
@app.post("/lazybird/v1/chat/completions")
@app.post("/openai/v1/chat/completions")
@app.post("/elevenlabs/v1/chat/completions")
@observe
async def chat_completions(request: Request):
    try:
        post_json_data = await request.json()
    except:
        post_json_data = json.loads((await request.body()).decode())

    api_key = request.headers.get("authorization")
    if api_key is not None:
        api_key = api_key[7:]

    tracing_context.update_current_observation(input=dict(post_json_data))
    model = post_json_data.get("model") or "openai/gpt-3.5-turbo-0125"
    msg = post_json_data["messages"]
    tools = post_json_data.get("tools")
    structured_output = post_json_data.get("response_format")
    settings = {
        "temperature": post_json_data.get("temperature"),
        "max_tokens": post_json_data.get("max_tokens"),
    }

    if type(msg) == list:
        last_request = msg[-1]
        if last_request["role"] == "tool":
            tools = None
            msg.append(
                {
                    "role": "system",
                    "content": "Please interpret the answer on behalf of the user.",
                }
            )
    if structured_output is not None and len(structured_output) != 0:
        streaming = False
        parent_tool = [
            {
                "role": "system",
                "content": f"""
## OUTPUT FORMAT: 
- Be sure that all outputs are JSON-compatible. 
- Output in JSON format and ensure that the JSON Schema is followed. 
- Do not include any preface or any other comments. 
- Do NOT use markup. 
- The output MUST be plain JSON with no other formatting or markup. 
- Include every part of the JSON FORMAT, even if a response is missing. 
- The Output MUST begin with {{ and the Output MUST end with }}

### JSON Schema:
``` json
{json.dumps(structured_output.get("json_schema",{}), indent=True, ensure_ascii=False)}       
``` 
""".strip(),
            }
        ]
        msg = parent_tool + msg
    elif tools is not None and len(tools) != 0:
        streaming = False
        parent_tool = [
            {
                "role": "system",
                "tools": tools,
                "content": """
If you need to use a tool to answer please use the defined tools. 
## Example tool definition 
```
{"tools":[
{
      "type": "function",
      "function": {
        "name": "get_current_weather",
        "description": "Get the current weather in a given location.",
        "parameters": {
          "type": "object",
          "properties": {
            "location": {
              "type": "string",
              "description":"The city and state, e.g. San Francisco, CA"
            },
            "unit":{"type":"string","enum":["celsius","fahrenheit"]}
          },
          "required": [
            "location"
          ],
          "additionalProperties": false,
          "$schema": "http://json-schema.org/draft-07/schema#"
        }
      }
    }
]}
```

### When you do use a tool your output should be like

``` 
{"tool_calls": [
                    {"function": {"arguments": "{\"location\":\"Paris, France\"}",
                                        "name": "get_current_weather"},
                                          "type": "function"}
                ]
}
``` 
Notes: 
  - You must answer by exactly following the provided instructions.
  - Do not add any additional comments or explanations.
  - Follow the data type format listed in the parameters. 
  - Function arguments is not a plain string it should **always** be a string of objects  properties names and values.
    - Incorrect: `"arguments": "a b c d"`
    - Correct: `"arguments": "{\"location\":\"Paris, France\"}"
  - In the given example the argument string parameter name is `location` as defined in the tool definition parameters.properties.
  - Always set the function name! 
  - Do not add "Here is..." or anything like that.

Act like a script, you are given an optional input and the instructions to perform, you answer with the output of the requested task.

Please only output valid json when using tools and wrap the output json in a markdown code. 
Example: 
```json 
...
```
            """.strip(),
            }
        ]
        msg = parent_tool + msg
    else:
        streaming = post_json_data.get("stream", False)

    # extract images from all msgs
    if isinstance(msg, list):
        images, msg = extract_images_from_messages(msg)
        if images is None or len(images) == 0:
            response, thinking_text, usage = await prompt_completion(
                json.dumps(msg, indent=True, ensure_ascii=False),
                model=model,
                api_key=api_key,
                **settings,
            )
        else:
            response, thinking_text, usage = await prompt_completion(
                json.dumps(msg, indent=True, ensure_ascii=False),
                images=images,
                model=model,
                api_key=api_key,
                **settings,
            )
    else:
        response, thinking_text, usage = await prompt_completion(
            json.dumps(msg, indent=True, ensure_ascii=False),
            model=model,
            api_key=api_key,
            **settings,
        )

    response_type = type(response)
    original_response = response
    if tools is not None and len(tools) != 0:

        if response_type == str:
            response = response.strip()
            if response.startswith("```json") and response.endswith("```"):
                response = response[7:-3].strip()
                response = load_json_with_fixed_escape(response)
            elif response.startswith("```") and response.endswith("```"):
                response = response[3:-3].strip()
                response = load_json_with_fixed_escape(response)
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
                            "type": "function",
                            "function": {
                                "name": first_function_name,
                                "arguments": json.dumps(response),
                            },
                        }
                    ]
                }

            if "tool_calls" in response:
                if len(response["tool_calls"]) == 0:
                    response = ""
                    original_response = ""
                else:
                    new_tool = []
                    for f in response["tool_calls"]:
                        i = randint(10000000, 999999999)
                        f["id"] = f"{i:}"
                        new_tool.append(
                            {
                                "id": f"{i:}",
                                "type": "function",
                                "function": {
                                    "name": f["function"]["name"],
                                    "arguments": f["function"]["arguments"],
                                },
                            }
                        )
                    response["tool_calls"] = new_tool
                    # f["function"]["arguments"] = f["function"]["arguments"].replace("\"", "\\\"")
                    # f["call_id"] = f"call_{i:}"
                    print("Tool:", response["tool_calls"])
                    if post_json_data.get("stream", False):
                        return StreamingResponse(
                            streamed_response_toolcall(response, model),
                            media_type="text/event-stream",
                        )
                    else:
                        return JSONResponse(
                            content={
                                "id": "chatcmpl-abc123",
                                "object": "chat.completion",
                                "created": 1699896916,
                                "model": model,
                                "choices": [
                                    {
                                        "index": 0,
                                        "message": {
                                            "role": "assistant",
                                            "tool_calls": response["tool_calls"],
                                            "content": "",
                                        },
                                        "logprobs": None,
                                        "finish_reason": "tool_calls",
                                    }
                                ],
                                "usage": {
                                    "prompt_tokens": 82,
                                    "completion_tokens": 17,
                                    "total_tokens": 99,
                                    "completion_tokens_details": {
                                        "reasoning_tokens": 0
                                    },
                                },
                            }
                        )
        if type(response) == str and "tool_calls" in response:
            pattern = r"\{\s*\"tool_calls\":\s*\["
            match = re.search(pattern, response, re.DOTALL)
            if match:
                msg = response[0 : match.start()].strip()
                tool_call = response[match.start() :].strip()
                try:
                    tool_call = load_json_with_fixed_escape(tool_call)
                    return JSONResponse(
                        content={
                            "id": "chatcmpl-abc123",
                            "object": "chat.completion",
                            "created": 1699896916,
                            "model": model,
                            "choices": [
                                {
                                    "index": 0,
                                    "message": {
                                        "role": "assistant",
                                        "tool_calls": tool_call["tool_calls"],
                                        "content": msg,
                                    },
                                    "logprobs": None,
                                    "finish_reason": "tool_calls",
                                }
                            ],
                            "usage": {
                                "prompt_tokens": 82,
                                "completion_tokens": 17,
                                "total_tokens": 99,
                                "completion_tokens_details": {"reasoning_tokens": 0},
                            },
                        }
                    )
                except:
                    pass

    if type(response) == dict:
        original_response = response

    elif len(msg) > 1 and response_type == str:
        response = response.strip()
        if response.startswith("```json") and response.endswith("```"):
            response = response[7:-3].strip()
            original_response = load_json_with_fixed_escape(response)
        elif response.startswith("```") and response.endswith("```"):
            response = response[3:-3].strip()
            try:
                original_response = load_json_with_fixed_escape(response)
            except:
                first_space_index = min(response.find("\n"), response.find(" "))
                original_response = response[first_space_index:-3].strip()
        else:
            try:
                original_response = load_json_with_fixed_escape(response)
            except:
                pass

            if (
                type(original_response) == dict
                and "role" in original_response
                and original_response["role"] == "assistant"
                and "content" in original_response
            ):
                original_response = original_response["content"]

    if type(original_response) in [dict, list]:
        original_response = json.dumps(original_response, ensure_ascii=False)

    original_response = fix_escaped_characters(original_response)

    if streaming or post_json_data.get("stream"):
        # generate_json_data
        return StreamingResponse(
            streamed_response(original_response, model), media_type="text/event-stream"
        )

    return JSONResponse(content=basic_response(original_response, model, usage=usage))


@app.post("/v1/completions")
@observe
async def completions(request: Request):
    try:
        post_json_data = await request.json()
    except:
        post_json_data = json.loads((await request.body()).decode())
    api_key = request.headers.get("authorization")
    if api_key is not None:
        api_key = api_key[7:]
    tracing_context.update_current_observation(input=dict(post_json_data))
    msg = post_json_data["prompt"]
    model = post_json_data.get("model") or "openai/gpt-3.5-turbo-0125"
    response, thinking_text, _ = await prompt_completion(msg, model=model, api_key=api_key)
    response = fix_escaped_characters(response)
    return StreamingResponse(
        streamed_response(response, model), content_type="text/event-stream"
    )

import base64
import json
import os
from os import environ
from typing import List

from app import logging, TIMEOUT
from const import VERSION, PROJECT_NAME
import platform
from datetime import datetime, timedelta
from aio_straico import aio_straico_client, ModelSelector
from aio_straico.utils.tracing import observe
from aio_straico.api.v0 import ImageSize
from aio_straico.api.smartllmselector import _PricingMethod

from .straico_platform import autoerase_chat, autoerase_upload_image
from .straico_platform import models as platform_models
from datetime import timezone, datetime
from data.agent_data import chat_settings_read
from pathlib import Path
from tempfile import TemporaryDirectory
from aio_straico import StraicoRequest
from dataclasses import dataclass

logger = logging.getLogger(__name__)

model_result = None
model_last_update_dt = None

# CLIENT_USER_AGENT = f"{PROJECT_NAME}/{VERSION} ({platform.system()}; {platform.processor()};) py/{platform.python_version()}"
# logger.debug(f"Straico Client User Agent = {CLIENT_USER_AGENT}")

CACHE_MODEL_LIST = int(environ.get("STRAICO_CACHE_MODEL_LIST", "60"))


@dataclass
class ErrorDetail:
    timestamp: datetime
    request_type: StraicoRequest
    error_message: str
    status_code: int

    def to_json(self):
        return {
            "http_status_code": self.status_code,
            "error_message": self.error_message.replace("\n", "<br/>"),
            "request_type": self.request_type.value.replace("_", " "),
        }


_errors: [ErrorDetail] = []


def refresh_errors():
    global _errors
    now = datetime.now()
    errors = [
        error for error in _errors if now - error.timestamp < timedelta(minutes=10)
    ]
    _errors = errors


def on_error(request_type: StraicoRequest, response):
    global _errors

    if isinstance(response.json()["error"], str):
        error_body = response.json()["error"]
    else:
        error_body = json.dumps(response.json()["error"], indent=True)
    now = datetime.now()
    error = ErrorDetail(now, request_type, error_body, response.status_code)
    refresh_errors()
    _errors.append(error)


def get_errors() -> [ErrorDetail]:
    global _errors
    refresh_errors()
    return _errors


async def get_model_mapping(api_key=None):
    if environ.get("STRAICO_API_KEY", "PER_REQUEST").strip() != "PER_REQUEST":
        api_key = None
    global model_last_update_dt, model_result
    if (
        model_last_update_dt is None
        or (model_last_update_dt + timedelta(minutes=CACHE_MODEL_LIST))
        <= datetime.now()
    ):
        model_result = await list_model(api_key)
        model_last_update_dt = datetime.now()

    models = model_result
    if models is None:
        return {}

    if "chat" in models:
        models = models["chat"]
    return models


def _extract_usage(response):
    """Map a Straico prompt-completion response to OpenAI-style usage fields.

    Straico returns word counts under ``words`` (v0) or ``overall_words`` (v1).
    We surface them via ``prompt_tokens`` / ``completion_tokens`` / ``total_tokens``
    so existing OpenAI-compat clients see real numbers instead of the legacy
    hardcoded placeholder. NOTE: the underlying unit is words, not tokenizer
    tokens — this is an approximation Straico's API does not currently improve on.

    When Straico's response also carries ``price`` (v0) or ``overall_price``
    (v1), the coin debit is surfaced as a vendor-extension subfield
    ``usage["straico_coins"]`` with the same ``{input, output, total}`` shape.
    Coins are Straico's billing currency and the only field that maps 1:1
    with the user's account ledger (distinct from upstream API USD pricing).
    Price extraction is independent fail-soft: a missing or malformed
    ``price`` never invalidates word-count usage.

    Returns ``None`` if the response shape does not carry usage info.
    """
    if not isinstance(response, dict):
        return None
    words = response.get("overall_words") or response.get("words")
    if not isinstance(words, dict):
        return None
    try:
        usage = {
            "prompt_tokens": int(words.get("input", 0)),
            "completion_tokens": int(words.get("output", 0)),
            "total_tokens": int(words.get("total", 0)),
        }
    except (TypeError, ValueError):
        return None
    price = response.get("overall_price") or response.get("price")
    if isinstance(price, dict):
        try:
            usage["straico_coins"] = {
                "input": float(price.get("input", 0)),
                "output": float(price.get("output", 0)),
                "total": float(price.get("total", 0)),
            }
        except (TypeError, ValueError):
            pass
    return usage


async def agent_promp_completion(agent_id, msg, api_key=None):
    async with aio_straico_client(
        API_KEY=api_key, timeout=TIMEOUT, on_request_failure_callback=on_error
    ) as client:
        settings = chat_settings_read(agent_id)

        response = await client.agent_prompt_completion(agent_id, msg, **settings)
        return response["answer"], "", None


@observe
async def prompt_completion(
    msg: str,
    images=None,
    model: str = "openai/gpt-3.5-turbo-0125",
    temperature: float = None,
    max_tokens: float = None,
    timeout: [int | None] = TIMEOUT,
    api_key=None,
) -> str:
    if environ.get("STRAICO_API_KEY", "PER_REQUEST").strip() != "PER_REQUEST":
        api_key = None

    # some  clients add :latest
    if model.startswith("Auto Select: "):
        m = model.replace("Auto Select: ", "").lower().strip()
        price = _PricingMethod(m)
        model = ModelSelector(price)
        is_model_found = True
    elif model.startswith("auto_select_model/"):
        m = (
            model.replace("auto_select_model/", "")
            .replace(":latest", "")
            .lower()
            .strip()
        )
        price = _PricingMethod(m)
        model = ModelSelector(price)
        is_model_found = True
    else:
        models = await get_model_mapping(api_key)
        model_values = [m["model"] for m in models]

        is_model_found = model in model_values

    if not is_model_found:
        if model.startswith("agent/"):  # lmstudio agent request
            model = model.split(":")[-1]
            return await agent_promp_completion(model, msg, api_key=api_key)
        elif model.startswith("Agent: "):  # Ollama agent request
            model = model.split("(")[-1][:-1]
            return await agent_promp_completion(model, msg, api_key=api_key)
        elif model.endswith(":latest"):
            model = model.replace(":latest", "")
            is_model_found = model in model_values

        if not is_model_found:
            model_name_mapping = dict(((m["name"], m["model"]) for m in models))
            if model in model_name_mapping:
                model = model_name_mapping[model]
                is_model_found = model in model_values

        if not is_model_found:
            model_alias = "ALIAS_" + model.upper().strip().replace("-", "_").replace(
                "/", "_"
            ).replace("  ", " ").replace(" ", "_").replace("__", "_")
            new_model = environ.get(model_alias)

            if new_model is not None:
                model = new_model.strip()
            else:
                logger.debug(
                    f"Unknown model {model}. Looking for alias model {model_alias}."
                )
                raise Exception(f"Unknown Model {model}")

    image_url = []
    if images is not None and len(images) > 0:
        with TemporaryDirectory() as tmpdirname:
            for index, image in enumerate(images):
                utc_now = datetime.now(timezone.utc)
                str_now = (
                    utc_now.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + f"{index:03}Z.png"
                )
                pathfile = Path(tmpdirname) / str_now
                with pathfile.open("wb") as fp:
                    data = base64.urlsafe_b64decode(
                        image
                    )  # .standard_b64decode(images[0])
                    fp.write(data)
                async with aio_straico_client(
                    API_KEY=api_key,
                    timeout=timeout,
                    on_request_failure_callback=on_error,
                ) as client:
                    file_url = await client.upload_file(pathfile)
                    image_url.append(file_url)

    post_request_data = {
        "model": model,
        "message": msg,
    }
    logger.debug(f"Request Post Data: {post_request_data}")
    settings = {}
    if temperature is not None:
        settings["temperature"] = temperature
    if max_tokens is not None:
        settings["max_tokens"] = max_tokens
    if len(image_url) > 0:
        settings["images"] = image_url
        # adding an image will trigger the aio straico to use the v1 api
        async with aio_straico_client(
            API_KEY=api_key, timeout=timeout, on_request_failure_callback=on_error
        ) as client:
            response = await client.prompt_completion(model, msg, **settings)
            logger.debug(f"response body: {response}")
            if response is None:
                return None, None, None
            model = list(response["completions"].keys())[0]
            message_last = response["completions"][model]["completion"]["choices"][-1][
                "message"
            ]
            content = message_last.get("content", "")
            reasoning = message_last.get("reasoning", "")
            return content, reasoning, _extract_usage(response)

    async with aio_straico_client(
        API_KEY=api_key, timeout=timeout, on_request_failure_callback=on_error
    ) as client:
        response = await client.prompt_completion(model, msg, **settings)
        logger.debug(f"response body: {response}")
        if response is None:
            return None, None, None
        message_last = response["completion"]["choices"][-1]["message"]
        content = message_last.get("content", "")
        reasoning = message_last.get("reasoning", "")
        return content, reasoning, _extract_usage(response)


async def list_model(api_key=None):
    if environ.get("STRAICO_API_KEY", "PER_REQUEST").strip() != "PER_REQUEST":
        api_key = None
    async with aio_straico_client(
        API_KEY=api_key, timeout=TIMEOUT, on_request_failure_callback=on_error
    ) as client:
        return await client.models(v=1)


async def elevenlabs_voices(api_key=None):
    if environ.get("STRAICO_API_KEY", "PER_REQUEST").strip() != "PER_REQUEST":
        api_key = None
    async with aio_straico_client(
        API_KEY=api_key, timeout=TIMEOUT, on_request_failure_callback=on_error
    ) as client:
        return await client.elevenlabs_voices()


async def tts_openai(model, text, api_key=None):
    if environ.get("STRAICO_API_KEY", "PER_REQUEST").strip() != "PER_REQUEST":
        api_key = None
    async with aio_straico_client(
        API_KEY=api_key, timeout=TIMEOUT, on_request_failure_callback=on_error
    ) as client:
        tts = await client.tts("tts-1", model, text=text)
        return tts


async def tts_elevenlabs(model, text, api_key=None):
    if environ.get("STRAICO_API_KEY", "PER_REQUEST").strip() != "PER_REQUEST":
        api_key = None
    async with aio_straico_client(
        API_KEY=api_key, timeout=TIMEOUT, on_request_failure_callback=on_error
    ) as client:
        tts = await client.tts("eleven_multilingual_v2", model, text=text)
        return tts


async def list_rags():
    async with aio_straico_client(
        timeout=TIMEOUT, on_request_failure_callback=on_error
    ) as client:
        return await client.rags()


async def delete_rag(rag_id: str):
    try:
        async with aio_straico_client(
            timeout=TIMEOUT, on_request_failure_callback=on_error
        ) as client:
            # Assuming the method to delete a RAG is `client.delete_rag(rag_id)`
            result = await client.rag_delete(rag_id)
            return result
    except Exception as e:
        logger.error(f"Failed to delete RAG: {e}")
        raise


async def create_rag(
    name: str,
    description: str,
    file_to_uploads: List[Path],
    chunking_method: str = "fixed_size",
    chunk_size: int = 1000,
    chunk_overlap: int = 50,
    breakpoint_threshold_type: str = None,
    buffer_size: int = 500,
):
    try:
        async with aio_straico_client(
            timeout=TIMEOUT, on_request_failure_callback=on_error
        ) as client:
            # Prepare RAG creation parameters
            kwargs = {
                "breakpoint_threshold_type": breakpoint_threshold_type,
                "buffer_size": buffer_size,
                "chunking_method": chunking_method,
                "chunk_size": chunk_size,
                "chunk_overlap": chunk_overlap,
            }

            # Call RAG creation method
            result = await client.create_rag(
                name, description, *file_to_uploads, **kwargs
            )

            return result.get("_id")  # Return the created RAG's ID

    except Exception as e:
        logger.error(f"Failed to create RAG: {e}")
        raise


async def list_agents(api_key=None):
    if environ.get("STRAICO_API_KEY", "PER_REQUEST").strip() != "PER_REQUEST":
        api_key = None

    async with aio_straico_client(
        API_KEY=api_key, timeout=TIMEOUT, on_request_failure_callback=on_error
    ) as client:
        return await client.agents()


async def delete_agent(agent_id):
    async with aio_straico_client(
        timeout=TIMEOUT, on_request_failure_callback=on_error
    ) as client:
        agent = await client.agent_object(agent_id)
        r = await agent.delete()
        return r


async def create_agent(name, description, custom_prompt, model, rag_id, tags):
    async with aio_straico_client(
        timeout=TIMEOUT, on_request_failure_callback=on_error
    ) as client:
        rags = {}
        if rag_id is not None and len(rag_id.strip()) > 0:
            rags["rag"] = rag_id
        result = await client.create_agent(
            name, description, model, custom_prompt, tags, **rags
        )

        return result.get("_id")  # Return the created RAG's ID


async def update_agent(agent_id, name, description, custom_prompt, model, rag_id, tags):
    async with aio_straico_client(
        timeout=TIMEOUT, on_request_failure_callback=on_error
    ) as client:
        rags = {}
        if rag_id is not None and len(rag_id.strip()) > 0:
            rags["rag"] = rag_id

        result = await client.agent_update(
            agent_id,
            name=name,
            description=description,
            model=model,
            system_prompt=custom_prompt,
            tags=tags,
            **rags,
        )
        return result


async def user_detail():
    async with aio_straico_client(
        timeout=TIMEOUT, on_request_failure_callback=on_error
    ) as client:
        return await client.user()


async def image_generation(
    model: str, n: int, prompt: str, size: ImageSize, api_key=None
):
    if environ.get("STRAICO_API_KEY", "PER_REQUEST").strip() != "PER_REQUEST":
        api_key = None

    async with aio_straico_client(
        API_KEY=api_key, timeout=TIMEOUT, on_request_failure_callback=on_error
    ) as client:
        images = await client.image_generation(
            model=model,
            description=prompt,
            size=size,
            variations=n,
        )
        return images


async def update_agent_chat_settings(agent_id, chat_settings):
    async with aio_straico_client(
        timeout=TIMEOUT, on_request_failure_callback=on_error
    ) as client:
        # Validate chat settings
        valid_search_types = {"similarity", "mmr", "similarity_score_threshold"}
        if chat_settings.get("search_type") not in valid_search_types:
            raise Exception(f"Invalid search type {chat_settings.get('search_type')}")

        # Ensure required fields are present
        if (
            chat_settings["search_type"] == "similarity"
            and chat_settings.get("k") is None
        ):
            raise Exception(
                "Number of documents (k) is required for similarity search."
            )
        elif chat_settings["search_type"] == "mmr" and (
            chat_settings.get("fetch_k") is None
            or chat_settings.get("lambda_mult") is None
        ):
            raise Exception(
                "Fetch K and Lambda Multiplier are required for MMR search."
            )
        elif (
            chat_settings["search_type"] == "similarity_score_threshold"
            and chat_settings.get("score_threshold") is None
        ):
            raise Exception(
                "Score Threshold is required for similarity score threshold search."
            )

        result = await client.agent_update(agent_id, chat_settings=chat_settings)
        return result

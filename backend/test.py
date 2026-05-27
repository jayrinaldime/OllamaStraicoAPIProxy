from app import logging
from pathlib import Path
from typing import List

logger = logging.getLogger(__name__)


def get_errors():
    return []


async def prompt_completion(
    msg: str,
    images=None,
    model: str = "openai/gpt-3.5-turbo-0125",
    temperature: float = None,
    max_tokens: float = None,
    **kwargs,
) -> str:
    # some  clients add :latest
    if model.endswith(":latest"):
        model = model.replace(":latest", "")
    post_request_data = {"model": model, "message": msg}
    logger.debug(f"Request Post Data: {post_request_data}")

    content = """
Lorem ipsum dolor sit amet, consectetur adipiscing elit. Quisque nec felis eu lacus finibus laoreet non non arcu. Mauris et lorem at ligula aliquam sodales sit amet suscipit justo. Pellentesque habitant morbi tristique senectus et netus et malesuada fames ac turpis egestas. In lectus libero, commodo quis finibus imperdiet, lobortis vitae ex. Cras commodo elit vel erat lobortis pretium. Nunc sagittis elementum ligula a aliquam. Nunc mollis est sodales enim feugiat dignissim. Nam et commodo orci. Quisque id semper nunc. Duis vel convallis elit. Donec dignissim eros in sapien consectetur sagittis. Donec est tortor, convallis non elit id, viverra luctus est. Nullam elementum, tortor eu mattis accumsan, diam lacus tristique elit, placerat viverra lacus urna in massa.

Nunc ac arcu ex. Proin ultrices ultricies semper. Ut id mauris eget tortor tincidunt scelerisque. Sed eget urna at ipsum interdum dapibus ut non ipsum. Nam luctus, arcu posuere iaculis volutpat, est erat finibus ligula, eget iaculis diam leo elementum nisl. Integer congue nec turpis euismod consequat. Duis at sem vitae dolor ornare tristique. Duis dapibus nisi massa, sit amet tristique tortor tempus sit amet. Nunc ac mollis tortor. Cras at elit enim. Sed egestas eget ipsum cursus molestie. Aliquam et finibus nisi, at viverra mi. Sed mattis non magna a semper.
"""
    return content, "", None


async def list_agents(**kwargs):
    return [
        {
            "__v": 0,
            "_id": "674d1a4e15da8e236c286096",
            "createdAt": "2024-12-02T02:24:14.890Z",
            "custom_prompt": "Help",
            "default_llm": "qwen/qwen-2.5-72b-instruct",
            "description": "Clean Code",
            "interaction_count": 0,
            "last_interaction": None,
            "name": "RobertMartin",
            "rag": "674d19adb09dbbbf63c810b0",
            "status": "active",
            "tags": ["clean_code", "programming"],
            "updatedAt": "2024-12-02T09:19:48.351Z",
            "user_id": "USERID123456",
            "uuidv4": "1946a783-2b27-4fa6-aeab-746da7a9750e",
            "visibility": "private",
        },
        {
            "__v": 0,
            "_id": "674d77b55962c57393ed249e",
            "createdAt": "2024-12-02T09:02:45.893Z",
            "custom_prompt": "Please help in python coding using Langchain and context "
            "provided. ",
            "default_llm": "qwen/qwen-2.5-72b-instruct",
            "description": "Expert in using langchain library",
            "interaction_count": 0,
            "last_interaction": None,
            "name": "LangChain",
            "rag": "674d773567a25d01d07c91fe",
            "status": "active",
            "tags": ["langchain", "python", "coding"],
            "updatedAt": "2024-12-02T09:19:35.905Z",
            "user_id": "USERID123456",
            "uuidv4": "4040de50-deef-4b41-94d6-b1190a20596e",
            "visibility": "private",
        },
        {
            "__v": 0,
            "_id": "674f3b1fb09dbbbf63c868d6",
            "createdAt": "2024-12-03T17:08:47.322Z",
            "custom_prompt": "Please help in python coding using the context provided. ",
            "default_llm": "openai/gpt-4o-mini",
            "description": "Knows about Time Series Forecasting in Python",
            "interaction_count": 0,
            "last_interaction": None,
            "name": "TimeSeriesForecasting",
            "rag": "674f3abffcbd9899f44375df",
            "status": "active",
            "tags": ["TimeSeriesForecasting"],
            "updatedAt": "2024-12-03T17:09:30.951Z",
            "user_id": "USERID123456",
            "uuidv4": "d8c8b607-42f3-4824-b47a-4127db97edc2",
            "visibility": "private",
        },
    ]


async def list_model(**kwargs):
    return {
        "chat": [
            {
                "max_output": 4096,
                "metadata": {
                    "applications": ["Coding", "Tutoring", "Math and logic"],
                    "capabilities": [],
                    "cons": [
                        "Potential for biased or inconsistent outputs "
                        "due to training data limitations",
                        "Potential for hallucination or generation of "
                        "factually incorrect information",
                    ],
                    "editors_choice_level": -1,
                    "editors_link": "",
                    "features": [],
                    "icon": "https://prompt-rack.s3.us-east-1.amazonaws.com/model-icons/claude-3-haiku.png",
                    "other": [],
                    "pros": [
                        "Strong reasoning and logical skills",
                        "Proficient in coding and problem-solving",
                        "Capable of tutoring and providing "
                        "explanations on various subjects",
                    ],
                },
                "model": "anthropic/claude-3-haiku:beta",
                "name": "Anthropic: Claude 3 Haiku",
                "pricing": {"coins": 1, "words": 100},
                "word_limit": 150000,
            },
            {
                "max_output": 4096,
                "metadata": {
                    "applications": ["Social chat", "Reasoning", "Content"],
                    "capabilities": [],
                    "cons": ["Refuses to interact with some copywritten " "work"],
                    "editors_choice_level": -1,
                    "editors_link": "",
                    "features": [],
                    "icon": "https://prompt-rack.s3.us-east-1.amazonaws.com/model-icons/claude-3-opus.png",
                    "other": [],
                    "pros": [
                        "Concise humor",
                        "Strong understanding of creativity",
                        "Outputs longer than previous generations",
                    ],
                },
                "model": "anthropic/claude-3-opus",
                "name": "Anthropic: Claude 3 Opus",
                "pricing": {"coins": 24, "words": 100},
                "word_limit": 150000,
            },
            {
                "max_output": 4096,
                "metadata": {
                    "applications": ["Writing", "Translation", "Tutoring", "Reasoning"],
                    "capabilities": [],
                    "cons": [
                        "Ethical concerns around misuse or deception",
                        "Potential for biased or inconsistent " "outputs",
                    ],
                    "editors_choice_level": -1,
                    "editors_link": "",
                    "features": [],
                    "icon": "https://prompt-rack.s3.us-east-1.amazonaws.com/model-icons/claude-3-sonnet.png",
                    "other": [],
                    "pros": [
                        "Quick response times",
                        "Can handle a wide variety of tasks",
                        "Vast knowledge base spanning numerous " "topics",
                    ],
                },
                "model": "anthropic/claude-3-sonnet",
                "name": "Anthropic: Claude 3 Sonnet",
                "pricing": {"coins": 5, "words": 100},
                "word_limit": 150000,
            },
            {
                "max_output": 8192,
                "metadata": {
                    "applications": ["Social chat", "Coding", "Reasoning", "Content"],
                    "capabilities": [],
                    "cons": [
                        "Tends to format responses in bullet points, "
                        "which may not suit all use cases"
                    ],
                    "editors_choice_level": -1,
                    "editors_link": "",
                    "features": [],
                    "icon": "https://prompt-rack.s3.us-east-1.amazonaws.com/model-icons/claude-3.5-haiku.png",
                    "other": [],
                    "pros": [
                        "Optimized for speed, coding accuracy, and "
                        "versatile tool integration",
                        "Excels in data extraction, labeling, and "
                        "real-time content moderation",
                        "Delivers quick code completions and "
                        "streamlined development workflows",
                    ],
                },
                "model": "anthropic/claude-3-5-haiku-20241022",
                "name": "Anthropic: Claude 3.5 Haiku",
                "pricing": {"coins": 1.6, "words": 100},
                "word_limit": 150000,
            },
            {
                "max_output": 8192,
                "metadata": {
                    "applications": ["Writing", "Social chat", "Content"],
                    "capabilities": [],
                    "cons": [
                        "Code Hallucinations and Refactoring",
                        "Overzealous Refusals and Ignored " "Instructions",
                        "Difficulty with Complex Reasoning",
                    ],
                    "editors_choice_level": 3,
                    "editors_link": "",
                    "features": ["Image input"],
                    "icon": "https://prompt-rack.s3.us-east-1.amazonaws.com/model-icons/claude-3.5-sonnet.png",
                    "other": [],
                    "pros": [
                        "Creativity in Responses",
                        "Helping users understand new concepts",
                        "Engaging conversations",
                        "Coding Games",
                        "Converting units of measurement",
                    ],
                },
                "model": "anthropic/claude-3.5-sonnet",
                "name": "Anthropic: Claude 3.5 Sonnet",
                "pricing": {"coins": 4.8, "words": 100},
                "word_limit": 150000,
            },
            {
                "max_output": 4000,
                "metadata": {
                    "applications": [
                        "Writing",
                        "Translation",
                        "Math and logic",
                        "Coding",
                        "Tutoring",
                    ],
                    "capabilities": [],
                    "cons": [
                        "Context and Instruction Sensitivity",
                        "Ethical and Bias Considerations",
                    ],
                    "editors_choice_level": -1,
                    "editors_link": "",
                    "features": [],
                    "icon": "https://prompt-rack.s3.us-east-1.amazonaws.com/model-icons/command-r-(08-2024).png",
                    "other": [],
                    "pros": [
                        "Capable of generating human-like text, "
                        "allowing for engaging and contextually "
                        "relevant conversations",
                        "Adaptable to various user preferences, "
                        "offering tailored assistance for individual "
                        "needs",
                    ],
                },
                "model": "cohere/command-r-08-2024",
                "name": "Cohere: Command R (08-2024)",
                "pricing": {"coins": 0.2, "words": 100},
                "word_limit": 96000,
            },
            {
                "max_output": 4000,
                "metadata": {
                    "applications": ["Writing", "Tutoring", "Math and logic"],
                    "capabilities": [],
                    "cons": [
                        "Potential for bias and ethical concerns, "
                        "requiring human oversight",
                        "Difficulty in handling ambiguous or unclear " "prompts",
                    ],
                    "editors_choice_level": -1,
                    "editors_link": "",
                    "features": [],
                    "icon": "https://prompt-rack.s3.us-east-1.amazonaws.com/model-icons/command-r%2B-(08-2024).png",
                    "other": [],
                    "pros": [
                        "Ability to generate human-like text with a "
                        "vast knowledge base",
                        "Efficient at handling large amounts of data "
                        "for training and contextual understanding",
                        "Versatility in assisting with various tasks " "and domains",
                    ],
                },
                "model": "cohere/command-r-plus-08-2024",
                "name": "Cohere: Command R+ (08-2024)",
                "pricing": {"coins": 3.4, "words": 100},
                "word_limit": 96000,
            },
            {
                "max_output": 32768,
                "metadata": {
                    "applications": ["Writing", "Translation", "Content"],
                    "capabilities": [],
                    "cons": [
                        "Tutoring may lack depth in some subjects",
                        "Roleplay may lack creativity",
                        "Content generation can sometimes be generic",
                    ],
                    "editors_choice_level": -1,
                    "editors_link": "",
                    "features": [],
                    "icon": "https://prompt-rack.s3.us-east-1.amazonaws.com/model-icons/dolphin-2.6-mixtral-8x7b.png",
                    "other": ["Uncensored"],
                    "pros": [
                        "Strong writing skills",
                        "Proficient in social chat",
                        "Reasonable math and logic skills",
                    ],
                },
                "model": "cognitivecomputations/dolphin-mixtral-8x7b",
                "name": "Dolphin 2.6 Mixtral 8x7B",
                "pricing": {"coins": 1, "words": 100},
                "word_limit": 24000,
            },
            {
                "max_output": 32768,
                "metadata": {
                    "applications": ["Writing", "Content", "Roleplay"],
                    "capabilities": [],
                    "cons": [
                        "Not ideal for coding or complex technical " "tasks",
                        "Struggles occasionally with handling special " "characters",
                    ],
                    "editors_choice_level": -1,
                    "editors_link": "",
                    "features": [],
                    "icon": "https://prompt-rack.s3.us-east-1.amazonaws.com/model-icons/eva-qwen2.5-14b.png",
                    "other": [],
                    "pros": [
                        "Excels in creative writing and role-play " "scenarios",
                        "Immersive narrative production with "
                        "character-driven storytelling",
                    ],
                },
                "model": "eva-unit-01/eva-qwen-2.5-14b",
                "name": "EVA Qwen2.5 14B",
                "pricing": {"coins": 0.2, "words": 100},
                "word_limit": 24576,
            },
            {
                "max_output": 400,
                "metadata": {
                    "applications": ["Writing", "Content", "Translation"],
                    "capabilities": [],
                    "cons": [
                        "Limited Explainability (Black Box reasoning)",
                        "Data Privacy Concerns",
                        "Difficulty in Fine-Tuning",
                    ],
                    "editors_choice_level": -1,
                    "editors_link": "",
                    "features": [],
                    "icon": "https://prompt-rack.s3.us-east-1.amazonaws.com/model-icons/goliath-120b.png",
                    "other": [],
                    "pros": [
                        "High Multilingual Fluency",
                        "Advanced Contextual Understanding",
                        "Rich Knowledge Base",
                    ],
                },
                "model": "alpindale/goliath-120b",
                "name": "Goliath 120B",
                "pricing": {"coins": 5, "words": 100},
                "word_limit": 4608,
            },
            {
                "max_output": 8192,
                "metadata": {
                    "applications": ["Writing", "Translation", "Content"],
                    "capabilities": [],
                    "cons": [
                        "Can reflect biases present in the training " "data",
                        "Sometimes struggles with conciseness and " "originality",
                    ],
                    "editors_choice_level": 3,
                    "editors_link": "",
                    "features": ["Image input"],
                    "icon": "https://prompt-rack.s3.us-east-1.amazonaws.com/model-icons/gemini-pro-1.5.png",
                    "other": [],
                    "pros": [
                        "Can generate text, translate languages, and "
                        "answer questions quickly",
                        "Accesses and processes information from a " "massive dataset",
                        "Capable of performing various tasks, from "
                        "writing different creative text formats to "
                        "translating languages, summarizing factual "
                        "topics, to coding",
                    ],
                },
                "model": "google/gemini-pro-1.5",
                "name": "Google: Gemini Pro 1.5",
                "pricing": {"coins": 3.7, "words": 100},
                "word_limit": 1500000,
            },
            {
                "max_output": 8192,
                "metadata": {
                    "applications": ["Content", "Translation"],
                    "capabilities": [],
                    "cons": ["Training data may contain biases"],
                    "editors_choice_level": -1,
                    "editors_link": "",
                    "features": [],
                    "icon": "https://prompt-rack.s3.us-east-1.amazonaws.com/model-icons/gemma-2-27b.png",
                    "other": ["Open source"],
                    "pros": [
                        "Can process information and retrieve "
                        "relevant facts quickly",
                        "Translate and understand text in different " "languages",
                    ],
                },
                "model": "google/gemma-2-27b-it",
                "name": "Google: Gemma 2 27B",
                "pricing": {"coins": 0.4, "words": 100},
                "word_limit": 3072,
            },
            {
                "max_output": 4096,
                "metadata": {
                    "applications": ["Writing", "Translation", "Content"],
                    "capabilities": [],
                    "cons": [
                        "May struggle with tasks that require a high "
                        "level of creativity or original thought",
                        "Limited understanding of human emotions and "
                        "social cues in social chat settings",
                        "May require additional time to complete "
                        "assignments due to language processing",
                    ],
                    "editors_choice_level": 2,
                    "editors_link": "https://straico.com/gryphe-mythomax-l2-13b-8k-beta/",
                    "features": [],
                    "icon": "https://prompt-rack.s3.us-east-1.amazonaws.com/model-icons/mythomax-l2-13b-8k.png",
                    "other": [],
                    "pros": [
                        "Excellent language skills and ability to "
                        "understand complex text",
                        "Strong communication skills, both written " "and verbal",
                        "Adaptable to different writing styles and " "formats",
                    ],
                },
                "model": "gryphe/mythomax-l2-13b",
                "name": "Gryphe: MythoMax L2 13B 8k",
                "pricing": {"coins": 1, "words": 100},
                "word_limit": 6144,
            },
            {
                "max_output": 8192,
                "metadata": {
                    "applications": ["Tutoring", "Content"],
                    "capabilities": [],
                    "cons": [
                        "Specific tuning needed to fully utilize in " "distinct fields",
                        "Dependence on Input Quality",
                    ],
                    "editors_choice_level": -1,
                    "editors_link": "",
                    "features": [],
                    "icon": "https://prompt-rack.s3.us-east-1.amazonaws.com/model-icons/llama-3-70b-instruct-(nitro).png",
                    "other": [],
                    "pros": [
                        "Produces coherent and contextually relevant " "responses",
                        "Improved Instruction Following",
                        "Enhanced Language Understanding",
                    ],
                },
                "model": "meta-llama/llama-3-70b-instruct:nitro",
                "name": "Meta: Llama 3 70B Instruct (nitro)",
                "pricing": {"coins": 1, "words": 100},
                "word_limit": 6144,
            },
            {
                "max_output": 8192,
                "metadata": {
                    "applications": ["Writing", "Social chat", "Content"],
                    "capabilities": [],
                    "cons": [
                        "Limited Depth in Specialized Knowledge",
                        "Specific tuning needed to fully utilize in " "distinct fields",
                        "Dependence on Input Quality",
                    ],
                    "editors_choice_level": -1,
                    "editors_link": "",
                    "features": [],
                    "icon": "https://prompt-rack.s3.us-east-1.amazonaws.com/model-icons/llama-3-8b-instruct.png",
                    "other": ["Uncensored"],
                    "pros": [
                        "Enhanced dialogue capabilities due to " "instruct-tuning",
                        "Improved Instruction Following",
                        "Enhanced Language Understanding",
                    ],
                },
                "model": "meta-llama/llama-3-8b-instruct",
                "name": "Meta: Llama 3 8B Instruct",
                "pricing": {"coins": 0.5, "words": 100},
                "word_limit": 6144,
            },
            {
                "max_output": 32768,
                "metadata": {
                    "applications": ["Social chat", "Reasoning", "Content"],
                    "capabilities": [],
                    "cons": ["Fails at self referencial tasks"],
                    "editors_choice_level": 2,
                    "editors_link": "",
                    "features": [],
                    "icon": "https://prompt-rack.s3.us-east-1.amazonaws.com/model-icons/llama-3.1-405b.png",
                    "other": ["Open source"],
                    "pros": ["Basic mathmatics", "Can solve logic puzzles"],
                },
                "model": "meta-llama/llama-3.1-405b-instruct",
                "name": "Meta: Llama 3.1 405B Instruct",
                "pricing": {"coins": 1.6, "words": 100},
                "word_limit": 98000,
            },
            {
                "max_output": 32768,
                "metadata": {
                    "applications": ["Tutoring", "Content"],
                    "capabilities": [],
                    "cons": [
                        "May struggle with reasoning",
                        "Specific tuning needed to fully utilize in " "distinct fields",
                        "Dependence on Input Quality or Instructions",
                    ],
                    "editors_choice_level": -1,
                    "editors_link": "",
                    "features": [],
                    "icon": "https://prompt-rack.s3.us-east-1.amazonaws.com/model-icons/llama-3.1-70b-instruct.png",
                    "other": [],
                    "pros": [
                        "High-Quality Outputs",
                        "Improved Instruction Following",
                        "Multilingual capabilities",
                    ],
                },
                "model": "meta-llama/llama-3.1-70b-instruct",
                "name": "Meta: Llama 3.1 70B Instruct",
                "pricing": {"coins": 0.7, "words": 100},
                "word_limit": 98000,
            },
            {
                "max_output": 256000,
                "metadata": {
                    "applications": ["Coding"],
                    "capabilities": [],
                    "cons": [
                        "Limited Creative Problem Solving",
                        "May generate syntactically correct but "
                        "functionally incorrect code",
                    ],
                    "editors_choice_level": -1,
                    "editors_link": "",
                    "features": [],
                    "icon": "https://prompt-rack.s3.us-east-1.amazonaws.com/model-icons/codestral-mamba.png",
                    "other": [],
                    "pros": [
                        "High Coding Proficiency",
                        "Multilingual capabilities",
                        "Advanced Natural Language Understanding",
                    ],
                },
                "model": "mistralai/codestral-mamba",
                "name": "Mistral: Codestral Mamba",
                "pricing": {"coins": 0.2, "words": 100},
                "word_limit": 192000,
            },
            {
                "max_output": 128000,
                "metadata": {
                    "applications": ["Writing", "Content", "Translation"],
                    "capabilities": [],
                    "cons": ["Limited Understanding of Abstract Concepts"],
                    "editors_choice_level": -1,
                    "editors_link": "",
                    "features": [],
                    "icon": "https://prompt-rack.s3.us-east-1.amazonaws.com/model-icons/default.png",
                    "other": [],
                    "pros": [
                        "High Capacity for Understanding Context",
                        "Multi-Language Capability",
                        "Enhanced Creativity in Content Generation",
                    ],
                },
                "model": "mistralai/mistral-large",
                "name": "Mistral: Large",
                "pricing": {"coins": 3, "words": 100},
                "word_limit": 96000,
            },
            {
                "max_output": 32768,
                "metadata": {
                    "applications": ["Content"],
                    "capabilities": [],
                    "cons": [
                        "May tend to overfit on niche data without "
                        "careful handling and tuning",
                        "Lacks true comprehension of context and " "nuance",
                        "Less effective on complex tasks",
                    ],
                    "editors_choice_level": -1,
                    "editors_link": "https://straico.com/mistral-mixtral-8x7b/",
                    "features": [],
                    "icon": "https://prompt-rack.s3.us-east-1.amazonaws.com/model-icons/mixtral-8x7b-instruct.png",
                    "other": [],
                    "pros": [
                        "Produces coherent and contextually relevant " "text outputs",
                        "Fine-tuning Flexibility",
                        "Strong language understanding capabilities",
                    ],
                },
                "model": "mistralai/mixtral-8x7b-instruct",
                "name": "Mistral: Mixtral 8x7B",
                "pricing": {"coins": 1, "words": 100},
                "word_limit": 24576,
            },
            {
                "max_output": 131072,
                "metadata": {
                    "applications": [
                        "Coding",
                        "Tutoring",
                        "Math and logic",
                        "Reasoning",
                        "Content",
                    ],
                    "capabilities": [],
                    "cons": [
                        "Could improve in specialized domains for " "deeper expertise"
                    ],
                    "editors_choice_level": 3,
                    "editors_link": "",
                    "features": [],
                    "icon": "https://prompt-rack.s3.us-east-1.amazonaws.com/model-icons/llama-3.1-nemotron-70b-instruct.png",
                    "other": [],
                    "pros": [
                        "Highly precise responses with excellent "
                        "formatting capabilities",
                        "Strong performance",
                    ],
                },
                "model": "nvidia/llama-3.1-nemotron-70b-instruct",
                "name": "NVIDIA: Llama 3.1 Nemotron 70B Instruct",
                "pricing": {"coins": 0.5, "words": 100},
                "word_limit": 98304,
            },
            {
                "max_output": 12000,
                "metadata": {
                    "applications": ["Tutoring", "Content"],
                    "capabilities": [],
                    "cons": [
                        "Sometimes misinterprets nuanced prompts, "
                        "leading to irrelevant or off-topic output",
                        "Produces text that may feel impersonal or "
                        "lack emotional depth",
                    ],
                    "editors_choice_level": -1,
                    "editors_link": "",
                    "features": [],
                    "icon": "https://prompt-rack.s3.us-east-1.amazonaws.com/model-icons/hermes-3-405b-instruct.png",
                    "other": [],
                    "pros": [
                        "Provides clear and precise instructions",
                        "Capable of using different writing styles",
                        "Effective Instruction Following",
                    ],
                },
                "model": "nousresearch/hermes-3-llama-3.1-405b",
                "name": "Nous: Hermes 3 405B Instruct",
                "pricing": {"coins": 0.5, "words": 100},
                "word_limit": 9000,
            },
            {
                "max_output": 4096,
                "metadata": {
                    "applications": ["Content"],
                    "capabilities": ["Browsing"],
                    "cons": [
                        "Limited Understanding",
                        "Over-reliance on Training Data",
                        "May generate plausible but factually "
                        "incorrect or nonsensical answers",
                    ],
                    "editors_choice_level": -1,
                    "editors_link": "",
                    "features": [],
                    "icon": "https://prompt-rack.s3.us-east-1.amazonaws.com/model-icons/gpt-3.5-turbo-16k.png",
                    "other": [],
                    "pros": [
                        "Cost-Efficient",
                        "Provides flexible options for tailoring "
                        "responses to specific needs or "
                        "applications",
                    ],
                },
                "model": "openai/gpt-3.5-turbo-0125",
                "name": "OpenAI: GPT-3.5 Turbo 16k",
                "pricing": {"coins": 1, "words": 100},
                "word_limit": 12000,
            },
            {
                "max_output": 4096,
                "metadata": {
                    "applications": ["Writing", "Reasoning", "Math and logic"],
                    "capabilities": ["Browsing"],
                    "cons": [
                        "Algorithmic Limitations",
                        "Narrow Specialization (coding)",
                        "Content Accuracy and Consistency",
                        "Issue where specialized knowledge needed " "(medical)",
                    ],
                    "editors_choice_level": -1,
                    "editors_link": "",
                    "features": [],
                    "icon": "https://prompt-rack.s3.us-east-1.amazonaws.com/model-icons/gpt-4.png",
                    "other": [],
                    "pros": [
                        "Multlilingual capabilities",
                        "Trained across various subjects allows for "
                        "informed answers, beneficial in tutoring and "
                        "educational applications",
                        "Enhanced Creativity and Coherence compared "
                        "to previous models",
                    ],
                },
                "model": "openai/gpt-4",
                "name": "OpenAI: GPT-4",
                "pricing": {"coins": 20, "words": 100},
                "word_limit": 6000,
            },
            {
                "max_output": 4096,
                "metadata": {
                    "applications": ["Writing"],
                    "capabilities": [],
                    "cons": [
                        "Potential for Overcomplexity",
                        "Generates repetitive information if prompts "
                        "are not well-structured",
                        "Gaps in knowledge or relevance in niche or " "emerging topics",
                    ],
                    "editors_choice_level": -1,
                    "editors_link": "https://straico.com/open-ai-gpt-4-turbo-128k/",
                    "features": [],
                    "icon": "https://prompt-rack.s3.us-east-1.amazonaws.com/model-icons/gpt-4-turbo-128k-new.png",
                    "other": [],
                    "pros": [
                        "Advanced fine-tuning results in more "
                        "relevant and accurate outputs",
                        "Supports complex tasks in a single pass",
                        "Maintains context over lengthy " "interactions",
                    ],
                },
                "model": "openai/gpt-4-turbo-2024-04-09",
                "name": "OpenAI: GPT-4 Turbo 128k",
                "pricing": {"coins": 8, "words": 100},
                "word_limit": 96000,
            },
            {
                "max_output": 4096,
                "metadata": {
                    "applications": ["Content"],
                    "capabilities": [],
                    "cons": [
                        "Performance heavily reliant on input "
                        "quality, potentially skewing results",
                        "Difficulty in accurately interpreting "
                        "complex or abstract images",
                        "Struggles with up-to-date real-world " "context",
                    ],
                    "editors_choice_level": -1,
                    "editors_link": "",
                    "features": ["Image input"],
                    "icon": "https://prompt-rack.s3.us-east-1.amazonaws.com/model-icons/gpt-4v.png",
                    "other": ["Deprecated"],
                    "pros": [
                        "Can analyze and explain visual data like "
                        "graphs, charts, or diagrams",
                        "Can produce coherent and contextually " "relevant outputs",
                    ],
                },
                "model": "openai/gpt-4-vision-preview",
                "name": "OpenAI: GPT-4 Vision",
                "pricing": {"coins": 10, "words": 100},
                "word_limit": 75000,
            },
            {
                "max_output": 16384,
                "metadata": {
                    "applications": [
                        "Coding",
                        "Math and logic",
                        "Reasoning",
                        "Roleplay",
                        "Content",
                    ],
                    "capabilities": ["Browsing"],
                    "cons": [
                        "Can struggle with tasks requiring everyday "
                        "reasoning or understanding of real-world "
                        "physical interactions",
                        "Struggles with understanding subtle context, "
                        "humor, or sarcasm",
                    ],
                    "editors_choice_level": 3,
                    "editors_link": "",
                    "features": ["Image input"],
                    "icon": "https://prompt-rack.s3.us-east-1.amazonaws.com/model-icons/gpt-4o-(aug-06).png",
                    "other": [],
                    "pros": [
                        "Ability for idea generation, storytelling, "
                        "and crafting engaging narratives",
                        "Multi-model infrastructure",
                        "Real-time roleplaying",
                    ],
                },
                "model": "openai/gpt-4o-2024-08-06",
                "name": "OpenAI: GPT-4o - (Aug-06)",
                "pricing": {"coins": 3, "words": 100},
                "word_limit": 96000,
            },
            {
                "max_output": 16000,
                "metadata": {
                    "applications": ["Writing", "Tutoring", "Coding", "Math and logic"],
                    "capabilities": ["Browsing"],
                    "cons": [
                        "Performance may degrade with vague or " "unclear inputs",
                        "While great overall, it might still "
                        "underperform in niche tasks compared to "
                        "specialized models",
                    ],
                    "editors_choice_level": 1,
                    "editors_link": "",
                    "features": ["Image input"],
                    "icon": "https://prompt-rack.s3.us-east-1.amazonaws.com/model-icons/gpt-4o-(nov-20).png",
                    "other": [],
                    "pros": [
                        "Delivers more natural, engaging, and "
                        "tailored content with improved relevance and "
                        "readability",
                        "Shows better performance in processing "
                        "non-English languages with improved "
                        "understanding of visual content",
                    ],
                },
                "model": "openai/gpt-4o-2024-11-20",
                "name": "OpenAI: GPT-4o - (Nov-20)",
                "pricing": {"coins": 3.3, "words": 100},
                "word_limit": 96000,
            },
            {
                "max_output": 16384,
                "metadata": {
                    "applications": ["Coding", "Math and logic", "Content"],
                    "capabilities": ["Browsing"],
                    "cons": ["Knowledge Compression Limits (Limited " "knowledge)"],
                    "editors_choice_level": 2,
                    "editors_link": "",
                    "features": ["Image input"],
                    "icon": "https://prompt-rack.s3.us-east-1.amazonaws.com/model-icons/gpt-4o-mini.png",
                    "other": [],
                    "pros": ["Good at tasks where it has to manipulate " "data"],
                },
                "model": "openai/gpt-4o-mini",
                "name": "OpenAI: GPT-4o mini",
                "pricing": {"coins": 0.4, "words": 100},
                "word_limit": 96000,
            },
            {
                "max_output": 65536,
                "metadata": {
                    "applications": ["Coding", "Math and logic", "Reasoning"],
                    "capabilities": [],
                    "cons": [
                        "May lack the expansive power and "
                        "functionality of its larger counterpart"
                    ],
                    "editors_choice_level": -1,
                    "editors_link": "",
                    "features": [],
                    "icon": "https://prompt-rack.s3.us-east-1.amazonaws.com/model-icons/o1-mini.png",
                    "other": [],
                    "pros": [
                        "Offers significant capabilities in a smaller "
                        "package for accessibility"
                    ],
                },
                "model": "openai/o1-mini",
                "name": "OpenAI: o1-mini (Beta)",
                "pricing": {"coins": 4, "words": 100},
                "word_limit": 96000,
            },
            {
                "max_output": 32768,
                "metadata": {
                    "applications": [
                        "Coding",
                        "Tutoring",
                        "Math and logic",
                        "Reasoning",
                    ],
                    "capabilities": [],
                    "cons": [
                        "Information is limited; specific "
                        "applications and limitations are not "
                        "detailed"
                    ],
                    "editors_choice_level": 3,
                    "editors_link": "",
                    "features": [],
                    "icon": "https://prompt-rack.s3.us-east-1.amazonaws.com/model-icons/o1-preview.png",
                    "other": [],
                    "pros": ["Most powerful problem-solving AI developed " "to date"],
                },
                "model": "openai/o1-preview",
                "name": "OpenAI: o1-preview (Beta)",
                "pricing": {"coins": 20, "words": 100},
                "word_limit": 96000,
            },
            {
                "max_output": 127072,
                "metadata": {
                    "applications": ["Writing", "Coding", "Content"],
                    "capabilities": [],
                    "cons": [
                        "Sometimes misinterprets nuanced prompts "
                        "related with social topics, leading to "
                        "irrelevant or off-topic output"
                    ],
                    "editors_choice_level": 1,
                    "editors_link": "",
                    "features": ["Web search"],
                    "icon": "https://prompt-rack.s3.us-east-1.amazonaws.com/model-icons/llama-3.1-sonar-405b-online.png",
                    "other": [],
                    "pros": ["Impressively solves complex tasks", "Coding tasks"],
                },
                "model": "perplexity/llama-3.1-sonar-huge-128k-online",
                "name": "Perplexity: Llama 3.1 Sonar 405B Online",
                "pricing": {"coins": 2.7, "words": 100},
                "word_limit": 95304,
            },
            {
                "max_output": 127072,
                "metadata": {
                    "applications": ["Tutoring", "Content"],
                    "capabilities": [],
                    "cons": ["Sometimes lacks information on niche topics"],
                    "editors_choice_level": -1,
                    "editors_link": "",
                    "features": ["Web search"],
                    "icon": "https://prompt-rack.s3.us-east-1.amazonaws.com/model-icons/llama-3.1-sonar-70b-online.png",
                    "other": [],
                    "pros": [
                        "Capable of handling real-time requests " "effectively",
                        "Capable of solving complex problems and "
                        "providing thoughtful answers",
                    ],
                },
                "model": "perplexity/llama-3.1-sonar-large-128k-online",
                "name": "Perplexity: Llama 3.1 Sonar 70B Online",
                "pricing": {"coins": 0.6, "words": 100},
                "word_limit": 95000,
            },
            {
                "max_output": 127072,
                "metadata": {
                    "applications": ["Content"],
                    "capabilities": [],
                    "cons": [
                        "Smaller models may not capture as much "
                        "information as larger counterparts"
                    ],
                    "editors_choice_level": -1,
                    "editors_link": "",
                    "features": ["Web search"],
                    "icon": "https://prompt-rack.s3.us-east-1.amazonaws.com/model-icons/llama-3.1-sonar-8b-online.png",
                    "other": [],
                    "pros": [
                        "Advanced Language Understanding",
                        "Good for creative brainstorming and idea " "generation",
                        "Multilingual capabilities",
                    ],
                },
                "model": "perplexity/llama-3.1-sonar-small-128k-online",
                "name": "Perplexity: Llama 3.1 Sonar 8B Online",
                "pricing": {"coins": 0.2, "words": 100},
                "word_limit": 95000,
            },
            {
                "max_output": 32768,
                "metadata": {
                    "applications": ["Social chat", "Translation"],
                    "capabilities": [],
                    "cons": [
                        "Limited world and popular knowledge",
                        "Lack of depth for expert knowledge or niche",
                    ],
                    "editors_choice_level": -1,
                    "editors_link": "",
                    "features": [],
                    "icon": "https://prompt-rack.s3.us-east-1.amazonaws.com/model-icons/default.png",
                    "other": [],
                    "pros": [
                        "Wide Domain Expertise",
                        "Multilingual capabilities",
                        "Structured data understanding (good on " "Tables and JSON)",
                    ],
                },
                "model": "qwen/qwen-2-72b-instruct",
                "name": "Qwen 2 72B Instruct",
                "pricing": {"coins": 0.5, "words": 100},
                "word_limit": 24576,
            },
            {
                "max_output": 4096,
                "metadata": {
                    "applications": ["Social chat", "Translation", "Content"],
                    "capabilities": [],
                    "cons": [
                        "Requires more development for non-visual "
                        "language-specific tasks"
                    ],
                    "editors_choice_level": -1,
                    "editors_link": "",
                    "features": ["Image input"],
                    "icon": "https://prompt-rack.s3.us-east-1.amazonaws.com/model-icons/qwen2-vl-72b.png",
                    "other": [],
                    "pros": [
                        "State-of-the-art performance in image "
                        "understanding and content creation"
                    ],
                },
                "model": "qwen/qwen-2-vl-72b-instruct",
                "name": "Qwen2-VL 72B Instruct",
                "pricing": {"coins": 0.2, "words": 100},
                "word_limit": 24576,
            },
            {
                "max_output": 32768,
                "metadata": {
                    "applications": ["Coding", "Tutoring"],
                    "capabilities": [],
                    "cons": [
                        "Primarily focused on text, limiting " "multimodal applications"
                    ],
                    "editors_choice_level": 1,
                    "editors_link": "",
                    "features": [],
                    "icon": "https://prompt-rack.s3.us-east-1.amazonaws.com/model-icons/qwen2.5-72b.png",
                    "other": [],
                    "pros": [
                        "Enhanced capabilities in coding and complex "
                        "mathematical reasoning",
                        "Excellent instruction-following and "
                        "long-form content generation",
                    ],
                },
                "model": "qwen/qwen-2.5-72b-instruct",
                "name": "Qwen2.5 72B Instruct",
                "pricing": {"coins": 0.2, "words": 100},
                "word_limit": 98304,
            },
            {
                "max_output": 4000,
                "metadata": {
                    "applications": ["Coding", "Math and logic", "Reasoning"],
                    "capabilities": [],
                    "cons": [
                        "Sometimes blends previous prompts with the "
                        "current one, affecting response clarity"
                    ],
                    "editors_choice_level": 1,
                    "editors_link": "",
                    "features": [],
                    "icon": "https://prompt-rack.s3.us-east-1.amazonaws.com/model-icons/qwen2.5-coder-32b.png",
                    "other": [],
                    "pros": [
                        "Excels in general knowledge and math",
                        "Powerful and Versatile Coding Skills",
                        "Benchmark Leader",
                    ],
                },
                "model": "qwen/qwen-2.5-coder-32b-instruct",
                "name": "Qwen2.5 Coder 32B Instruct",
                "pricing": {"coins": 0.5, "words": 100},
                "word_limit": 24576,
            },
            {
                "max_output": 16000,
                "metadata": {
                    "applications": ["Social chat", "Coding", "Reasoning", "Content"],
                    "capabilities": [],
                    "cons": [
                        "Tends to format responses in bullet points, "
                        "which may not suit all use cases"
                    ],
                    "editors_choice_level": -1,
                    "editors_link": "",
                    "features": [],
                    "icon": "https://prompt-rack.s3.us-east-1.amazonaws.com/model-icons/sorcererlm-8x22b.png",
                    "other": [],
                    "pros": [
                        "Optimized for speed, coding accuracy, and "
                        "versatile tool integration",
                        "Excels in data extraction, labeling, and "
                        "real-time content moderation",
                        "Delivers quick code completions and "
                        "streamlined development workflows",
                    ],
                },
                "model": "raifle/sorcererlm-8x22b",
                "name": "SorcererLM 8x22B",
                "pricing": {"coins": 2.4, "words": 100},
                "word_limit": 12000,
            },
            {
                "max_output": 32000,
                "metadata": {
                    "applications": ["Writing", "Roleplay", "Content"],
                    "capabilities": [],
                    "cons": [
                        "Performs adequately but not exceptionally "
                        "outside of role-playing"
                    ],
                    "editors_choice_level": -1,
                    "editors_link": "",
                    "features": [],
                    "icon": "https://prompt-rack.s3.us-east-1.amazonaws.com/model-icons/unslopnemo-12b.png",
                    "other": [],
                    "pros": [
                        "Engages seriously with role-playing prompts",
                        "Expert in Adventure Writing",
                    ],
                },
                "model": "thedrummer/unslopnemo-12b",
                "name": "Unslopnemo 12b",
                "pricing": {"coins": 0.3, "words": 100},
                "word_limit": 24000,
            },
            {
                "max_output": 32768,
                "metadata": {
                    "applications": ["Coding", "Social chat", "Reasoning", "Content"],
                    "capabilities": [],
                    "cons": [
                        "Content moderation may limit certain "
                        "freedoms in interactions"
                    ],
                    "editors_choice_level": -1,
                    "editors_link": "",
                    "features": [],
                    "icon": "https://prompt-rack.s3.us-east-1.amazonaws.com/model-icons/grok-beta.png",
                    "other": [],
                    "pros": [
                        "Strong performance in chat, coding, and " "reasoning",
                        "Excels in graduate-level science, general "
                        "knowledge, and complex mathematics",
                        "Enhanced capabilities from predecessor " "models",
                    ],
                },
                "model": "x-ai/grok-beta",
                "name": "xAI: Grok Beta",
                "pricing": {"coins": 5.3, "words": 100},
                "word_limit": 98304,
            },
        ],
        "image": [
            {
                "model": "openai/dall-e-3",
                "name": "OpenAI: Dall-E 3",
                "pricing": {
                    "landscape": {"coins": 120, "size": "1792x1024"},
                    "portrait": {"coins": 120, "size": "1024x1792"},
                    "square": {"coins": 90, "size": "1024x1024"},
                },
            }
        ],
    }


async def user_detail():
    return {
        "first_name": "Demo",
        "last_name": "User",
        "coins": 9999999.99,
        "plan": "Emerald Pack",
    }


async def delete_agent(agent_id):
    return {}


async def create_agent(name, description, custom_prompt, model, rag_id, tags):
    return "674f3b1fb09dbbbf63c868d6"


async def update_agent(agent_id, name, description, custom_prompt, model, rag_id, tags):
    return {
        "__v": 0,
        "_id": "674f3b1fb09dbbbf63c868d6",
        "createdAt": "2024-12-03T17:08:47.322Z",
        "custom_prompt": "Please help in python coding using the context provided. ",
        "default_llm": "openai/gpt-4o-mini",
        "description": "Knows about Time Series Forecasting in Python",
        "interaction_count": 0,
        "last_interaction": None,
        "name": "TimeSeriesForecasting",
        "rag": "674f3abffcbd9899f44375df",
        "status": "active",
        "tags": ["TimeSeriesForecasting"],
        "updatedAt": "2024-12-03T17:09:30.951Z",
        "user_id": "USERID123456",
        "uuidv4": "d8c8b607-42f3-4824-b47a-4127db97edc2",
        "visibility": "private",
    }


async def list_rags():
    return [
        {
            "__v": 0,
            "_id": "674d19adb09dbbbf63c810b0",
            "breakpoint_threshold_type": "percentile",
            "buffer_size": 100,
            "chunk_overlap": 100,
            "chunk_size": 1000,
            "chunking_method": "fixed_size",
            "createdAt": "2024-12-02T02:21:33.167Z",
            "description": "Books about clean code, clean architecture and software "
            "structures",
            "name": "Clean Code ",
            "original_filename": "Clean_Architecture_A_Craftsman_Guide_to_Software_Structure_and_Design.pdf, "
            "Clean_Mobile_Architecture_2022.pdf, "
            "The_Clean_Coder__A_Code_of_Conduct_For_Pro_-_Robert_C._Martin.pdf",
            "rag_url": "https://prompt-rack.s3.amazonaws.com/api/rag/USERID123456/6fc87e4c-1c37-4b71-a7d2-f10488c01699/index.faiss",
            "separator": "\n",
            "separators": ["\n\n", "\n", " ", ""],
            "updatedAt": "2024-12-02T02:21:33.167Z",
            "user_id": "USERID123456",
        },
        {
            "__v": 0,
            "_id": "674d773567a25d01d07c91fe",
            "breakpoint_threshold_type": "percentile",
            "buffer_size": 100,
            "chunk_overlap": 100,
            "chunk_size": 2000,
            "chunking_method": "fixed_size",
            "createdAt": "2024-12-02T09:00:37.943Z",
            "description": "Langchain Python Coding ",
            "name": "LangChain",
            "original_filename": "9781835083468-GENERATIVE_AI_WITH_LANGCHAIN.pdf",
            "rag_url": "https://prompt-rack.s3.amazonaws.com/api/rag/USERID123456/b8aca3e7-bc1a-4cdc-8ed7-7e609b5109db/index.faiss",
            "separator": "\n",
            "separators": ["\n\n", "\n", " ", ""],
            "updatedAt": "2024-12-02T09:00:37.943Z",
            "user_id": "USERID123456",
        },
        {
            "__v": 0,
            "_id": "674f3abffcbd9899f44375df",
            "breakpoint_threshold_type": "percentile",
            "buffer_size": 100,
            "chunk_overlap": 200,
            "chunk_size": 2000,
            "chunking_method": "fixed_size",
            "createdAt": "2024-12-03T17:07:11.271Z",
            "description": "Time Series Forecasting in Python",
            "name": "Time Series Forecasting in Python",
            "original_filename": "Time_Series_Forecasting_in_Python.pdf",
            "rag_url": "https://prompt-rack.s3.amazonaws.com/api/rag/USERID123456/53a1d900-8d25-445a-adab-5fbf8db649c0/index.faiss",
            "separator": "\n",
            "separators": ["\n\n", "\n", " ", ""],
            "updatedAt": "2024-12-03T17:07:11.271Z",
            "user_id": "USERID123456",
        },
    ]


async def delete_rag(rag_id: str):
    return {}


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

    return "674d19adb09dbbbf63c810b0"  # Return the created RAG's ID

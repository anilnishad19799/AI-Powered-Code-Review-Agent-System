import json
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)
from openai import AsyncOpenAI, APIConnectionError, RateLimitError
from app.services.llm.base import BaseLLMService
from app.core.config import get_settings
from app.core.exception import LLMResponseParseException
from app.core.logger import logger

settings = get_settings()


class OpenAIService(BaseLLMService):

    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model          # e.g. "gpt-4o"
        self.max_tokens = settings.anthropic_max_tokens  # reuse same limit
        logger.info(f"OpenAIService initialized | model={self.model}")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((APIConnectionError, RateLimitError)),
        reraise=True,
    )
    async def complete(self, system_prompt: str, user_message: str) -> str:
        """
        Calls OpenAI API with retry logic.
        Uses same interface as ClaudeService — fully interchangeable.
        """
        logger.debug(f"Calling OpenAI | model={self.model} | prompt_chars={len(user_message)}")

        response = await self.client.chat.completions.create(
            model=self.model,
            max_tokens=self.max_tokens,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user",   "content": user_message},
            ],
        )

        result = response.choices[0].message.content
        finish_reason = response.choices[0].finish_reason
        logger.debug(f"OpenAI response received | chars={len(result)} | finish_reason={finish_reason}")
        return result

    async def complete_json(self, system_prompt: str, user_message: str) -> dict:
        """
        Calls OpenAI and parses response as JSON.
        Uses json_object mode for guaranteed valid JSON — no fence stripping needed.
        """
        logger.debug(f"Calling OpenAI JSON mode | model={self.model}")

        # OpenAI has a native JSON mode — much more reliable than Claude's
        response = await self.client.chat.completions.create(
            model=self.model,
            max_tokens=self.max_tokens,
            response_format={"type": "json_object"},   # ← forces valid JSON always
            messages=[
                {"role": "system", "content": system_prompt + "\nRespond only in JSON."},
                {"role": "user",   "content": user_message},
            ],
        )

        raw = response.choices[0].message.content

        try:
            parsed = json.loads(raw)
            logger.debug(f"OpenAI JSON parsed | keys={list(parsed.keys())}")
            return parsed
        except json.JSONDecodeError as e:
            logger.error(f"OpenAI JSON parse failed | error={e} | raw={raw[:300]}")
            raise LLMResponseParseException(
                agent_name="openai",
                raw_response=raw,
            ) from e
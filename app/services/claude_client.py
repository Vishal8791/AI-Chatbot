# import logging
# import anthropic

# from app.config import get_settings
# from app.core.exceptions import ClaudeAPIError

# logger = logging.getLogger(__name__)


# class ClaudeClient:
#     """Thin async wrapper around the Anthropic SDK.

#     Keeping the SDK call isolated here means you can swap providers
#     (OpenAI, Gemini, etc.) by only touching this file.
#     """

#     def __init__(self) -> None:
#         s = get_settings()
#         self._client = anthropic.AsyncAnthropic(api_key=s.anthropic_api_key)
#         self._model = s.claude_model
#         self._max_tokens = s.max_tokens

#     async def complete(
#         self,
#         messages: list[dict],
#         system: str | None = None,
#     ) -> tuple[str, int, int]:
#         """
#         Returns:
#             (reply_text, input_tokens, output_tokens)
#         """
#         kwargs: dict = {
#             "model": self._model,
#             "max_tokens": self._max_tokens,
#             "messages": messages,
#         }
#         if system:
#             kwargs["system"] = system

#         try:
#             response = await self._client.messages.create(**kwargs)
#         except anthropic.APIStatusError as exc:
#             logger.error("Anthropic API error: status=%d body=%s", exc.status_code, exc.message)
#             raise ClaudeAPIError(f"Anthropic returned {exc.status_code}: {exc.message}") from exc
#         except anthropic.APIConnectionError as exc:
#             logger.error("Anthropic connection error: %s", exc)
#             raise ClaudeAPIError("Could not reach Anthropic API") from exc

#         reply = response.content[0].text
#         return reply, response.usage.input_tokens, response.usage.output_tokens


import logging
import urllib.request
import urllib.error
import json

from app.config import get_settings
from app.core.exceptions import ClaudeAPIError

logger = logging.getLogger(__name__)


class ClaudeClient:
    """Gemini API wrapper — drop-in replacement for the Anthropic client."""

    def __init__(self) -> None:
        s = get_settings()
        self._api_key = s.gemini_api_key
        self._model = s.gemini_model
        self._max_tokens = s.max_tokens

    async def complete(
        self,
        messages: list[dict],
        system: str | None = None,
    ) -> tuple[str, int, int]:
        """
        Returns:
            (reply_text, input_tokens, output_tokens)
        """
        # Convert messages to Gemini format
        contents = []
        for m in messages:
            role = "user" if m["role"] == "user" else "model"
            contents.append({
                "role": role,
                "parts": [{"text": m["content"]}]
            })

        payload = {
            "contents": contents,
            "generationConfig": {
                "maxOutputTokens": self._max_tokens,
            }
        }

        # Add system prompt if provided
        if system:
            payload["systemInstruction"] = {
                "parts": [{"text": system}]
            }

        url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/"
            f"{self._model}:generateContent?key={self._api_key}"
        )

        try:
            data = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(
                url,
                data=data,
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=30) as resp:
                result = json.loads(resp.read().decode("utf-8"))

        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8")
            logger.error("Gemini API error: status=%d body=%s", exc.code, body)
            raise ClaudeAPIError(f"Gemini returned {exc.code}: {body}") from exc
        except Exception as exc:
            logger.error("Gemini connection error: %s", exc)
            raise ClaudeAPIError(f"Could not reach Gemini API: {exc}") from exc

        try:
            reply = result["candidates"][0]["content"]["parts"][0]["text"]
            in_tokens = result.get("usageMetadata", {}).get("promptTokenCount", 0)
            out_tokens = result.get("usageMetadata", {}).get("candidatesTokenCount", 0)
        except (KeyError, IndexError) as exc:
            raise ClaudeAPIError(f"Unexpected Gemini response format: {result}") from exc

        return reply, in_tokens, out_tokens
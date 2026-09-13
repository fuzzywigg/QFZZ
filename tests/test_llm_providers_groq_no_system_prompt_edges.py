"""GroqProvider.generate with system_prompt=None sends a single user message."""

import json
from unittest.mock import MagicMock, patch

from qfzz.llm.providers.groq_provider import GroqProvider


def test_groq_generate_without_system_prompt_single_user_message():
    provider = GroqProvider(api_key="gsk-test")
    body = json.dumps({"choices": [{"message": {"content": "plain"}}]}).encode()
    resp = MagicMock()
    resp.read.return_value = body
    resp.status = 200
    resp.__enter__.return_value = resp
    resp.__exit__.return_value = False

    with patch(
        "qfzz.llm.providers.groq_provider.urllib.request.urlopen",
        return_value=resp,
    ) as urlopen:
        text = provider.generate("user only", system_prompt=None, max_tokens=8)

    assert text == "plain"
    payload = json.loads(urlopen.call_args[0][0].data.decode("utf-8"))
    assert len(payload["messages"]) == 1
    assert payload["messages"][0] == {"role": "user", "content": "user only"}

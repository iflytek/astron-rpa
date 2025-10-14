"""Client for xcAgent flow execution (Xingchen API streaming wrapper)."""

import http.client
import json


class xcAgent:  # pylint: disable=invalid-name
    """Minimal client for Xingchen flow execution.

    NOTE: Class name kept for backward compatibility; consider renaming to `XcAgent`.
    """

    def __init__(self, api_key: str, api_secret: str):
        """Store credentials and prepare headers."""
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "text/event-stream",
            "Authorization": "Bearer {}:{}".format(api_key, api_secret),
        }

    def run_flow(self, flow_id: str, content: str, is_stream: bool = False):
        """Execute a remote flow and optionally stream results.

        Args:
            flow_id: remote flow identifier
            content: user input content
            is_stream: request streaming mode
        Returns:
            First chunk delta content string.
        """
        data = {
            "flow_id": flow_id,
            "parameters": {"AGENT_USER_INPUT": content},
            "stream": is_stream,
        }
        payload = json.dumps(data)

        conn = http.client.HTTPSConnection("xingchen-api.xf-yun.com", timeout=120)
        conn.request(
            "POST",
            "/workflow/v1/chat/completions",
            payload,
            self.headers,
            encode_chunked=True,
        )
        res = conn.getresponse()

        data = res.readline().decode("utf-8")
        response_json = json.loads(data)
        return response_json["choices"][0]["delta"]["content"]

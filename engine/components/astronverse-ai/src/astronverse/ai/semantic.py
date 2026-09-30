"""Constrained semantic decisions through the authenticated local gateway."""

import math

import requests
from astronverse.actionlib.atomic import atomicMg


class SemanticAI:
    @staticmethod
    @atomicMg.atomic("SemanticAI", outputList=[atomicMg.param("semantic_result", types="Dict")])
    def choose(instruction: str, text: str, options: list) -> dict:
        """Choose a supplied option or abstain; transport failures remain errors."""
        if not isinstance(instruction, str) or not instruction.strip():
            raise ValueError("instruction must be a non-empty string")
        if not isinstance(text, str) or not text.strip():
            raise ValueError("text must be a non-empty string")
        if not isinstance(options, list) or not 1 <= len(options) <= 254:
            raise ValueError("options must contain between 1 and 254 choices")
        option_ids = set()
        normalized_options = []
        for option in options:
            if not isinstance(option, dict) or set(option) != {"id", "label"}:
                raise ValueError("Each option must contain id and label")
            option_id, label = option["id"], option["label"]
            if isinstance(option_id, str):
                option_id = option_id.strip()
            if isinstance(label, str):
                label = label.strip()
            if (
                not isinstance(option_id, str)
                or not option_id.strip()
                or option_id == "__abstain__"
                or option_id in option_ids
                or not isinstance(label, str)
                or not label.strip()
            ):
                raise ValueError("Options require unique non-reserved IDs and non-empty labels")
            option_ids.add(option_id)
            normalized_options.append({"id": option_id, "label": label})

        port = atomicMg.cfg().get("GATEWAY_PORT") or "13159"
        response = requests.post(
            f"http://127.0.0.1:{port}/api/rpa-ai-service/v1/decision/choice",
            json={"instruction": instruction.strip(), "text": text.strip(), "options": normalized_options},
            timeout=(5, 35),
        )
        try:
            response.raise_for_status()
            result = response.json()
        finally:
            response.close()
        if not isinstance(result, dict) or set(result) != {"status", "selected_id", "confidence"}:
            raise ValueError("Invalid semantic choice response")
        confidence = result["confidence"]
        selected_id = result["selected_id"]
        if (
            type(confidence) not in (int, float)
            or not math.isfinite(confidence)
            or not 0 <= confidence <= 1
            or not (
                (result["status"] == "matched" and isinstance(selected_id, str) and selected_id in option_ids)
                or (result["status"] == "abstain" and selected_id is None)
            )
        ):
            raise ValueError("Invalid semantic choice response")
        return result

"""Local Strands model provider used when AWS Bedrock is not configured.

This is a real Strands `Model` subclass. It drives the same agent loop and
tools. Swap to `strands.models.BedrockModel` when AWS credentials exist.
"""
from __future__ import annotations

import json
import threading
from collections.abc import AsyncGenerator, AsyncIterable
from typing import Any

from pydantic import BaseModel
from strands.models.model import Model
from strands.types.content import Messages, SystemContentBlock
from strands.types.streaming import StreamEvent
from strands.types.tools import ToolChoice, ToolSpec


class DemoOpsModel(Model):
    """Deterministic tool-calling model for the refund clerk demo."""

    def __init__(self):
        super().__init__()
        self._config = {"model_id": "hiop-demo-ops-model", "context_window_limit": 32000}

    def update_config(self, **model_config: Any) -> None:
        self._config.update(model_config)

    def get_config(self) -> Any:
        return self._config

    async def structured_output(
        self, output_model: type[BaseModel], prompt: Messages, system_prompt: str | None = None, **kwargs: Any
    ) -> AsyncGenerator[dict[str, Any], None]:
        yield {"output": output_model()}

    async def stream(
        self,
        messages: Messages,
        tool_specs: list[ToolSpec] | None = None,
        system_prompt: str | None = None,
        *,
        tool_choice: ToolChoice | None = None,
        system_prompt_content: list[SystemContentBlock] | None = None,
        invocation_state: dict[str, Any] | None = None,
        cancel_signal: threading.Event | None = None,
        **kwargs: Any,
    ) -> AsyncIterable[StreamEvent]:
        names = {t.get("name") for t in (tool_specs or []) if isinstance(t, dict)}
        last_user = ""
        tool_results: list[dict[str, Any]] = []
        for m in messages:
            if m.get("role") == "user":
                for b in m.get("content", []):
                    if "text" in b:
                        last_user = b["text"]
                    if "toolResult" in b:
                        tool_results.append(b["toolResult"])

        next_tool, payload = self._next(last_user, tool_results, names)

        yield {"messageStart": {"role": "assistant"}}
        if next_tool:
            tid = f"tool_{len(tool_results)+1}"
            yield {"contentBlockStart": {"start": {"toolUse": {"toolUseId": tid, "name": next_tool}}}}
            yield {"contentBlockDelta": {"delta": {"toolUse": {"input": json.dumps(payload)}}}}
            yield {"contentBlockStop": {}}
            yield {"messageStop": {"stopReason": "tool_use"}}
        else:
            text = payload.get("text", "Done.")
            yield {"contentBlockDelta": {"delta": {"text": text}}}
            yield {"contentBlockStop": {}}
            yield {"messageStop": {"stopReason": "end_turn"}}
        yield {
            "metadata": {
                "usage": {"inputTokens": 8, "outputTokens": 8, "totalTokens": 16},
                "metrics": {"latencyMs": 5},
            }
        }

    def _next(
        self, user: str, results: list[dict[str, Any]], names: set[str]
    ) -> tuple[str | None, dict[str, Any]]:
        parsed = []
        for r in results:
            body = r.get("content", [{}])[0]
            raw = body.get("json") or body.get("text") or {}
            if isinstance(raw, str):
                try:
                    raw = json.loads(raw)
                except json.JSONDecodeError:
                    raw = {"text": raw}
            parsed.append(raw)

        used = []
        for m_idx, m in enumerate(results):
            # names inferred from order
            used.append(m.get("name"))

        has_invest = any(isinstance(p, dict) and (p.get("application_id") or p.get("customer_id")) for p in parsed)
        has_auth = any(isinstance(p, dict) and p.get("decision") for p in parsed)
        last = parsed[-1] if parsed else {}

        if not has_invest and "investigate_permit_application" in names:
            return "investigate_permit_application", {"request_text": user}

        if has_invest and not has_auth and "request_permit_authority" in names:
            inv = next(p for p in parsed if p.get("application_id") or p.get("customer_id"))
            return "request_permit_authority", {
                "application_id": inv.get("application_id") or "",
                "amount_cents": int(inv.get("fee_cents") or inv.get("suggested_refund_cents") or 0),
                "reason": inv.get("permit_type") or "permit",
            }

        if has_auth:
            decision = last.get("decision") if isinstance(last, dict) else None
            if not decision:
                for p in reversed(parsed):
                    if isinstance(p, dict) and p.get("decision"):
                        decision = p["decision"]
                        break
            outcome = (decision or {}).get("outcome")
            token = (decision or {}).get("permit_token")
            if outcome == "PERMIT" and token and "execute_issue_permit" in names:
                already_exec = any(isinstance(p, dict) and p.get("dispatched") for p in parsed)
                if not already_exec:
                    return "execute_issue_permit", {"permit_token": token, "application_id": "", "amount_cents": 0}
            if outcome == "PERMIT_WITH_APPROVAL":
                return None, {
                    "text": "CRUSHIA returned PERMIT_WITH_APPROVAL. Commercial building permit not issued. Waiting for building official, then a fresh CRUSHIA decision."
                }
            if outcome == "DENY":
                return None, {"text": "CRUSHIA DENY. No refund will be issued."}

        return None, {"text": "HIOP governed run complete. Permission delta remains 0."}

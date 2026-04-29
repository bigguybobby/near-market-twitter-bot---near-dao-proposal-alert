"""NEAR DAO proposal alert core logic."""
from __future__ import annotations

import base64
import json
import urllib.request
from dataclasses import dataclass
from typing import Any, Iterable

DEFAULT_RPC_URL = "https://rpc.mainnet.near.org"


@dataclass(frozen=True)
class Proposal:
    dao: str
    proposal_id: int
    proposer: str
    description: str
    status: str | None = None
    kind: str | None = None


def encode_args(args: dict[str, Any]) -> str:
    return base64.b64encode(json.dumps(args).encode("utf-8")).decode("ascii")


def decode_result(result: dict[str, Any]) -> Any:
    raw = bytes(result.get("result", []))
    if not raw:
        return None
    text = raw.decode("utf-8")
    return json.loads(text)


class NearRpc:
    def __init__(self, rpc_url: str = DEFAULT_RPC_URL):
        self.rpc_url = rpc_url

    def call(self, method: str, params: dict[str, Any]) -> dict[str, Any]:
        payload = {"jsonrpc": "2.0", "id": "near-dao-alert", "method": method, "params": params}
        req = urllib.request.Request(self.rpc_url, data=json.dumps(payload).encode(), headers={"content-type": "application/json", "user-agent": "near-dao-alert/1.0"}, method="POST")
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        if data.get("error"):
            raise RuntimeError(data["error"].get("message", "NEAR RPC error"))
        return data["result"]

    def view_function(self, account_id: str, method_name: str, args: dict[str, Any] | None = None) -> Any:
        result = self.call("query", {
            "request_type": "call_function",
            "finality": "final",
            "account_id": account_id,
            "method_name": method_name,
            "args_base64": encode_args(args or {}),
        })
        return decode_result(result)


def normalize_proposal(dao: str, proposal_id: int, payload: dict[str, Any]) -> Proposal:
    kind = payload.get("kind")
    if isinstance(kind, dict):
        kind = next(iter(kind.keys()), "Unknown")
    return Proposal(
        dao=dao,
        proposal_id=proposal_id,
        proposer=payload.get("proposer") or payload.get("proposer_id") or "unknown",
        description=(payload.get("description") or "").strip(),
        status=payload.get("status"),
        kind=kind,
    )


def fetch_recent_proposals(dao_contract: str, rpc: NearRpc, limit: int = 5) -> list[Proposal]:
    last_id = int(rpc.view_function(dao_contract, "get_last_proposal_id") or 0)
    proposals: list[Proposal] = []
    start = max(0, last_id - limit)
    for proposal_id in range(last_id - 1, start - 1, -1):
        payload = rpc.view_function(dao_contract, "get_proposal", {"id": proposal_id})
        if payload:
            proposals.append(normalize_proposal(dao_contract, proposal_id, payload))
    return proposals


def proposal_key(proposal: Proposal) -> str:
    return f"{proposal.dao}:{proposal.proposal_id}"


def format_proposal_tweet(proposal: Proposal) -> str:
    description = " ".join(proposal.description.split()) or "No description provided"
    if len(description) > 130:
        description = description[:127].rstrip() + "…"
    return (
        f"🗳️ New NEAR DAO proposal #{proposal.proposal_id} on {proposal.dao}\n"
        f"Type: {proposal.kind or 'Proposal'} | Status: {proposal.status or 'unknown'}\n"
        f"By: {proposal.proposer}\n"
        f"{description}\n"
        "#NEAR #DAO"
    )[:280]


def load_state(path: str) -> dict[str, Any]:
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except FileNotFoundError:
        return {"seen": []}


def save_state(path: str, state: dict[str, Any]) -> None:
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(state, fh, indent=2, sort_keys=True)


def unseen(proposals: Iterable[Proposal], seen: set[str]) -> list[Proposal]:
    return [proposal for proposal in proposals if proposal_key(proposal) not in seen]

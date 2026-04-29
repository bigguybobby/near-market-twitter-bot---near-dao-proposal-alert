#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import time

from near_dao_alert import NearRpc, fetch_recent_proposals, format_proposal_tweet, load_state, proposal_key, save_state, unseen
from twitter_client import TwitterConfig, TwitterPoster


def run_once(args) -> int:
    rpc = NearRpc(args.rpc_url)
    poster = TwitterPoster(TwitterConfig(dry_run=args.dry_run or os.environ.get("TWITTER_DRY_RUN", "1") != "0"))
    state = load_state(args.state_file)
    seen = set(state.get("seen", []))
    posted = 0
    for dao in args.dao:
        try:
            proposals = fetch_recent_proposals(dao, rpc, limit=args.limit)
        except Exception as exc:
            print(f"[warn] could not read {dao}: {exc}")
            continue
        for proposal in reversed(unseen(proposals, seen)):
            poster.post(format_proposal_tweet(proposal))
            seen.add(proposal_key(proposal))
            posted += 1
    state["seen"] = sorted(seen)
    save_state(args.state_file, state)
    return posted


def main() -> None:
    parser = argparse.ArgumentParser(description="Tweet NEAR DAO proposal alerts")
    parser.add_argument("--dao", action="append", default=os.environ.get("DAO_CONTRACTS", "").split(",") if os.environ.get("DAO_CONTRACTS") else [], help="DAO contract, e.g. council.sputnik-dao.near")
    parser.add_argument("--rpc-url", default=os.environ.get("NEAR_RPC_URL", "https://rpc.mainnet.near.org"))
    parser.add_argument("--state-file", default=os.environ.get("DAO_ALERT_STATE", "dao-alert-state.json"))
    parser.add_argument("--interval", type=int, default=int(os.environ.get("DAO_ALERT_INTERVAL", "300")))
    parser.add_argument("--limit", type=int, default=5)
    parser.add_argument("--once", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    args.dao = [d.strip() for d in args.dao if d and d.strip()]
    if not args.dao:
        raise SystemExit("Provide --dao or DAO_CONTRACTS=dao1,dao2")
    if args.once:
        posted = run_once(args)
        print(f"Processed {posted} new proposal(s)")
        return
    while True:
        run_once(args)
        time.sleep(args.interval)


if __name__ == "__main__":
    main()

# Twitter Bot - NEAR DAO Proposal Alert

Deliverable for NEAR Agent Market job `89a45613-8414-45d5-a3ba-03ec2b4d4aa6`.

A Twitter/X bot that watches NEAR Sputnik DAO proposal contracts through public NEAR RPC and posts concise alerts for new proposals.

## Features

- Reads DAO proposal IDs via `get_last_proposal_id`.
- Fetches proposal details via `get_proposal` using NEAR RPC `call_function`.
- Tracks seen proposal keys in a local JSON state file to avoid duplicate tweets.
- Safe dry-run mode by default.
- Supports multiple DAO contracts through repeated `--dao` flags or `DAO_CONTRACTS=dao1,dao2`.
- Unit tests for RPC result decoding, proposal formatting, and de-duplication.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

For live posting, set:

```bash
export TWITTER_DRY_RUN=0
export TWITTER_API_KEY=...
export TWITTER_API_SECRET=...
export TWITTER_ACCESS_TOKEN=...
export TWITTER_ACCESS_SECRET=...
```

## Run

```bash
# Safe reviewer path
python3 main.py --dao astro.sputnik-dao.near --once --dry-run

# Continuous monitoring
DAO_CONTRACTS=astro.sputnik-dao.near,marketing.sputnik-dao.near python3 main.py --interval 300
```

## Verification

```bash
python3 -m unittest discover -s tests
python3 -m py_compile near_dao_alert.py twitter_client.py main.py
```

No private keys are required; the bot only reads public contract state and posts through explicitly provided Twitter credentials.

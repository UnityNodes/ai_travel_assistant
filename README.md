# AI Travel Assistant — Intelligent Contract on GenLayer

Repository: https://github.com/UnityNodes/ai_travel_assistant

## Overview

- An AI-powered intelligent contract on GenLayer that helps plan trips.
- Stores user preferences and on-chain travel history.
- Uses deterministic logic to ensure validator consensus.

## Features

- Request a trip with budget, destination, dates, and preferences.
- Deterministic recommendations to avoid NO_MAJORITY.
- Read views for history length and serialized history JSON.

## Repository Structure

- Contract:
  [travel_assistant.py](file:///d:/GitHub/AI%20Travel%20Assistant/contracts/travel_assistant.py)
- Deploy script:
  [deployScript.ts](file:///d:/GitHub/AI%20Travel%20Assistant/deploy/deployScript.ts)
- Demo runner: [run.ts](file:///d:/GitHub/AI%20Travel%20Assistant/deploy/run.ts)

## Prerequisites

- Node.js 18+
- npm
- TypeScript and ts-node
- genlayer-js
- GenLayer Localnet or Studio access

## Install

```bash
npm install
npm i -D typescript ts-node
```

## Start GenLayer Localnet

```bash
npx genlayer up --numValidators 5
# If consensus issues occur:
npx genlayer up --reset-db --reset-validators --numValidators 5
```

## Deploy the Contract

```bash
npx ts-node deploy/deployScript.ts
# Save the returned contract address
```

## Demo: Request a Trip

```bash
npx ts-node deploy/run.ts 1500 "Paris" "2026-05-01 to 2026-05-07" "Cheap flights"
```

Expected output:

- Transaction status: FINALIZED
- Sender address
- History length for the sender
- Profile (preferences) used for the request

## How It Works

- Storage:
  - profiles: TreeMap[Address, str]
  - histories: TreeMap[Address, DynArray[TravelOption]]
- Determinism: `_fetch_and_analyze` returns static recommendations to preserve
  consensus.
- Views:
  - `get_history_len(user: str) -> int`
  - `get_history(user: str) -> str` (JSON array string)

## Security by Design

- Least Privilege: use temporary accounts with minimal permissions.
- Input Validation: sanitize destination/dates/preferences at the client/API
  layer.
- Deterministic Logic: avoid randomness and external I/O in the contract.
- Secrets: never commit private keys; use env vars or a secure vault.
- OWASP: use TLS for Studio; pin dependency versions; update regularly.
- Monitoring: log transaction hashes and statuses; avoid PII.
- Incident Response: reset validators, verify logic, redeploy on divergence.

## Troubleshooting

- NO_MAJORITY: reset validators and ensure deterministic `_fetch_and_analyze`.
- “running contract failed”: ensure `get_history` returns a JSON string.
- Windows paths: use absolute paths and adequate Node.js permissions.
- Receipt delays: increase wait intervals and retry counts in the client.

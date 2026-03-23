# AI Travel Assistant — Intelligent Contract on GenLayer

Repository: https://github.com/UnityNodes/ai_travel_assistant

## Overview

An AI-powered Intelligent Contract on GenLayer that helps users plan trips by combining **live web data** with **non-deterministic AI reasoning** and **on-chain consensus**.

Each trip request triggers real web fetches for destination data and currency exchange rates, feeds that context into an LLM prompt, and lets GenLayer validators reach consensus on the AI-generated recommendations through the equivalence principle.

## GenLayer Capabilities Used

| Capability | How it is used |
|---|---|
| **`gl.nondet.web.get()`** — Web Fetch | Fetches live destination info from the REST Countries API and current USD exchange rates from open.er-api.com. Each validator fetches independently. |
| **`gl.nondet.exec_prompt()`** — Non-deterministic AI | Generates 3 personalized travel options (economy / standard / premium) using the fetched real-world data as grounding context. |
| **`gl.eq_principle.prompt_comparative()`** — Comparative Consensus | Every validator independently runs web fetches + AI generation, then outputs are compared semantically to reach consensus. |

### Why these capabilities matter

- **Web Fetch** grounds the AI in real data — actual currencies, regions, languages, and live exchange rates — instead of relying on stale training data.
- **Non-deterministic execution** means each validator produces its own AI output independently, preventing single-point-of-failure answers.
- **Comparative equivalence principle** compares validator outputs semantically ("do they cover similar budget tiers and match user preferences?") rather than requiring exact string equality, which is essential for AI-generated text.

## Features

- Request a personalized trip with budget, destination, dates, and preferences.
- Two independent web fetches per request inject real-world context into AI reasoning.
- Non-deterministic validators independently generate options; consensus via comparative principle.
- On-chain storage of user profiles and full trip history.
- View functions for querying history, profile, and aggregate stats.

## Repository Structure

```
contracts/
  travel_assistant.py    # Intelligent Contract (Python)
deploy/
  deployScript.ts        # Deploys the contract via genlayer-js
  run.ts                 # End-to-end demo: deploy + request trip + read state
scripts/
  init_validators.py     # (Optional) Recreate validators with Gemini config
package.json
```

## Prerequisites

- Node.js 18+ (tested with Node 23)
- npm
- Docker Desktop (for GenLayer Localnet)
- GenLayer CLI (`npx genlayer`)
- GenLayer Localnet or Studio access

## Install

```bash
npm install
```

## Start GenLayer Localnet

```bash
npx genlayer init
```

Follow the interactive prompts to select an LLM provider (e.g., Heurist AI) and enter your API key. This starts all Docker containers and configures validators.

If you need a clean restart:

```bash
npx genlayer init
# or manually:
npx genlayer up --reset-db --reset-validators --numValidators 5
```

## Deploy and Run the Demo

```bash
npx tsx deploy/run.ts 1500 "France" "2026-05-01 to 2026-05-07" "Cheap flights, cultural tours"
```

Expected output:

- Transaction status: `FINALIZED`
- Consensus result: `MAJORITY_AGREE`
- AI-generated travel recommendation stored in on-chain history
- User profile updated with preferences

## How It Works (Step by Step)

1. User calls `request_trip(budget, destination, dates, preferences)`.
2. Inside the equivalence principle block, **each validator independently**:
   - **Web Fetch 1**: calls `gl.nondet.web.get()` to fetch destination data (capital, currencies, languages, region) from the REST Countries API.
   - **Web Fetch 2**: calls `gl.nondet.web.get()` to fetch live USD exchange rates from open.er-api.com.
   - **AI Prompt**: calls `gl.nondet.exec_prompt()` with all fetched data injected into the prompt context, generating 3 travel options (economy / standard / premium).
3. `gl.eq_principle.prompt_comparative()` compares all validator outputs and reaches consensus: outputs are equivalent if they cover similar budget tiers, prices are in a comparable range, and the best option matches user preferences.
4. The winning recommendation is parsed and stored as a `TravelOption` in the user's on-chain history.

## Contract API

### Write Methods

| Method | Description |
|---|---|
| `request_trip(budget, destination, dates, preferences)` | Runs web fetch + AI analysis and stores the result |
| `update_preferences(preferences)` | Updates the caller's stored preferences |

### View Methods

| Method | Returns |
|---|---|
| `get_history(user)` | JSON array of the user's past trip recommendations |
| `get_history_len(user)` | Number of trips in the user's history |
| `get_profile(user)` | The user's stored preferences string |
| `get_all_histories()` | Map of all addresses to their trip count |

## Storage

- `profiles: TreeMap[Address, str]` — user preference strings
- `histories: TreeMap[Address, DynArray[TravelOption]]` — trip history per user

Each `TravelOption` stores: `destination`, `description`, `price`, `duration`, `rating`, `is_booked`.

## Troubleshooting

- **`NO_MAJORITY`**: try a different LLM model (DeepSeek V3 via Heurist works well), reduce prompt size, or increase validator count.
- **`type is not supported: i32`**: use `int` instead of `i32` for contract method parameters.
- **Web fetch errors**: verify the REST Countries and exchange rate APIs are reachable from the GenLayer node (`docker exec genlayer-jsonrpc-1 curl -I https://restcountries.com`).
- **`running contract failed`**: check that the AI returns valid JSON; the contract strips markdown wrappers automatically.
- **Receipt delays**: increase `retries` and `interval` in the client script.
- **Validator LLM errors**: check `docker logs genlayer-jsonrpc-1` for provider errors; some models have low `max_tokens` defaults.

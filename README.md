# AI DeFi Risk Analyzer — Intelligent Contract on GenLayer Bradbury

Repository: https://github.com/UnityNodes/ai_defi_risk_analyzer

## Overview

An AI-powered Intelligent Contract on GenLayer Bradbury Testnet that analyzes DeFi protocol risk by combining **live on-chain data** with **non-deterministic AI reasoning** and **decentralized validator consensus**.

Each analysis request triggers two real web fetches from DeFiLlama, feeds the live data into an LLM prompt, and lets GenLayer validators reach consensus on the AI-generated risk report through the equivalence principle. The result — risk score, audit status, TVL trend, warnings, and suggested allocation — is stored permanently on-chain.

## GenLayer Capabilities Used

| Capability | How it is used |
|---|---|
| **`gl.nondet.web.get()`** — Web Fetch | Fetches live protocol data from DeFiLlama (`/protocol/{slug}`) and global TVL context (`/v2/globalCharts`). Each validator fetches independently. |
| **`gl.nondet.exec_prompt()`** — Non-deterministic AI | Generates a structured risk report (risk score, audit status, TVL trend, warnings, allocation) using the live DeFiLlama data as grounding context. |
| **`gl.eq_principle.prompt_comparative()`** — Comparative Consensus | Every validator independently runs web fetches + AI analysis; outputs are compared semantically to reach consensus. |

### Why these capabilities matter

- **Web Fetch** grounds the AI in real-time protocol data — actual TVL, trends, and ecosystem context — instead of relying on stale training data.
- **Non-deterministic execution** means each validator produces its own AI analysis independently, preventing a single point of failure.
- **Comparative equivalence principle** compares validator outputs semantically ("do `risk_level`, `audit_status`, and `tvl_trend` match?") rather than requiring exact string equality — essential for AI-generated text.

## How It Works

1. **Fetch** — Each validator independently calls DeFiLlama to get live TVL, trend, and protocol metadata.
2. **AI** — The fetched data is injected into an LLM prompt that returns a structured JSON risk report.
3. **Consensus** — `gl.eq_principle.prompt_comparative()` compares all validator outputs; if `risk_level`, `audit_status`, and `tvl_trend` match, consensus is reached and the report is stored on-chain.

## Contract API

### Write Methods

| Method | Description |
|---|---|
| `analyze_protocol(protocol, amount, risk_tolerance)` | Fetches live data + runs AI risk analysis and stores the result on-chain |

### View Methods

| Method | Returns |
|---|---|
| `get_reports(user)` | JSON array of all risk reports for a given address |
| `get_reports_len(user)` | Number of reports stored for a given address |
| `get_profile(user)` | The user's stored risk tolerance string |
| `get_all_reports()` | Map of all addresses to their report count |

## Prerequisites

- Node.js 18+ (tested with Node 23)
- GenLayer CLI (`npm install -g genlayer` or `npx genlayer`)
- GEN testnet tokens from the faucet

## Setup

### 1. Install dependencies

```bash
npm install
```

### 2. Switch to Bradbury Testnet

```bash
genlayer network testnet-bradbury
```

### 3. Create or show your account

```bash
# Show existing account
genlayer account show

# Or create a new one
genlayer account create
```

### 4. Get free GEN tokens

Go to the faucet and request tokens for your address:

```
https://testnet-faucet.genlayer.foundation/
```

### 5. Verify connection

```bash
genlayer config get network
```

## Deploy and Run

### Option A — GenLayer CLI

```bash
# Deploy the contract
genlayer deploy --contract contracts/defi_risk_analyzer.py

# Analyze a protocol (replace CONTRACT_ADDRESS with the deployed address)
genlayer write <CONTRACT_ADDRESS> analyze_protocol --args "Aave" 1000 "low"

# Read the risk report (replace YOUR_ADDRESS with your wallet address)
genlayer call <CONTRACT_ADDRESS> get_reports --args <YOUR_ADDRESS>
```

### Option B — TypeScript runner

```bash
# Set your funded private key (recommended for testnet)
export PRIVATE_KEY=0xyour_private_key_here

# Run: deploy + analyze + read results
npx tsx deploy/run.ts "Aave" 1000 "low"
```

### CLI argument order

```
npx tsx deploy/run.ts <protocol> <amount> <risk_tolerance>
```

| Argument | Default | Example |
|---|---|---|
| `protocol` | `Aave` | `"Uniswap"`, `"Curve"` |
| `amount` | `1000` | `5000` |
| `risk_tolerance` | `low` | `"medium"`, `"high"` |

### Expected output

```json
{
  "risk_score": 3,
  "risk_level": "low",
  "tvl_usd": "$12.1B",
  "tvl_trend": "stable",
  "audit_status": "audited",
  "audit_firms": ["OpenZeppelin", "Trail of Bits"],
  "incident_risk": "low",
  "recommendation": "Aave is one of the most battle-tested protocols. Suitable for low risk tolerance.",
  "warnings": [],
  "suggested_allocation": 20
}
```

## Repository Structure

```
contracts/
  defi_risk_analyzer.py  # Intelligent Contract (Python / GenLayer)
deploy/
  deployScript.ts        # Deploys the contract via genlayer-js
  run.ts                 # End-to-end demo: deploy + analyze + read state
scripts/
  init_validators.py     # For Localnet only — not needed on Bradbury
package.json
```

## Important Notes About Bradbury

- **Do NOT** run `genlayer init` or `genlayer up` — those are for Localnet only.
- **Do NOT** create validators manually — Bradbury has real decentralized validators.
- **GEN tokens are required** before deploying — get them from the faucet first.
- **Transactions take 1–3 minutes** on Bradbury — this is normal; the runner waits automatically.

## Troubleshooting

- **`NO_MAJORITY`**: The validators could not reach consensus. Try again — occasional disagreement is normal on a live testnet with real LLM variance.
- **Insufficient funds**: Get GEN tokens from `https://testnet-faucet.genlayer.foundation/` before deploying.
- **`testnetBradbury` not found**: Update `genlayer-js` to the latest version (`npm install genlayer-js@latest`).
- **Web fetch errors**: DeFiLlama endpoints are public — verify they are reachable and the protocol slug is correct (e.g., `aave`, not `AAVE`).
- **`running contract failed`**: Check that the AI returns valid JSON; the contract strips markdown wrappers automatically.
- **Receipt timeout**: On Bradbury, `retries: 60` with `interval: 5000` gives 5 minutes. If the network is slow, increase `retries` in `deploy/run.ts`.
- **`type is not supported: i32`**: Use `int` instead of `i32` for contract method parameters — already handled in this contract.

# AI DeFi Risk Analyzer

An **Intelligent Contract** on GenLayer Bradbury Testnet that analyzes DeFi protocol risk using live on-chain data, non-deterministic AI reasoning, and decentralized validator consensus — all enforced at the protocol level.

**Deployed contract:** [`0xC138cC96061e9F160C94da33e2B7085ff45100ba`](https://explorer-bradbury.genlayer.com/address/0xC138cC96061e9F160C94da33e2B7085ff45100ba)

---

## The Problem

DeFi investors have no reliable, trustless way to assess protocol risk. Existing tools are centralized, static, or rely on stale data. A smart contract that fetches live TVL, runs AI analysis, and reaches decentralized consensus on the result — without trusting a single oracle or API — doesn't exist yet.

GenLayer makes this possible.

---

## How It Works

When a user calls `analyze_protocol("Aave", 1000, "low")`, the contract:

1. **Fetches live data** — pulls real-time TVL and protocol metrics from DeFiLlama API via `gl.nondet.web.get()`
2. **Runs AI analysis** — each of 5 independent validators independently executes an LLM prompt to generate a structured risk report via `gl.nondet.exec_prompt()`
3. **Reaches consensus** — validator outputs are compared via `gl.eq_principle.prompt_comparative()`; if `risk_level`, `audit_status`, and `tvl_trend` match, the result is finalized
4. **Stores on-chain** — the risk report is permanently written to contract storage and readable by anyone

### Example output

```json
{
  "risk_score": 3,
  "risk_level": "low",
  "tvl_usd": "$12.1B",
  "tvl_trend": "stable",
  "audit_status": "audited",
  "audit_firms": ["OpenZeppelin", "Trail of Bits"],
  "incident_risk": "low",
  "recommendation": "Aave is one of the most battle-tested DeFi protocols with deep liquidity and a proven security track record.",
  "warnings": [],
  "suggested_allocation": 20
}
```

---

## GenLayer Capabilities Used

| Capability | What it does in this contract |
|---|---|
| `gl.nondet.web.get()` | Fetches live protocol TVL and metrics from DeFiLlama API — each validator independently |
| `gl.nondet.exec_prompt()` | Runs LLM risk analysis on each validator independently — non-deterministic by design |
| `gl.eq_principle.prompt_comparative()` | Reaches consensus across validators by comparing risk assessments semantically, not by exact string match |

This combination is what makes the contract trustless: no single entity controls the data fetch, the AI reasoning, or the consensus decision.

---

## Architecture

```
User → analyze_protocol(protocol, amount, risk_tolerance)
         │
         ├─ [Validator 1] web.get(DeFiLlama) → exec_prompt → risk JSON
         ├─ [Validator 2] web.get(DeFiLlama) → exec_prompt → risk JSON
         ├─ [Validator 3] web.get(DeFiLlama) → exec_prompt → risk JSON
         ├─ [Validator 4] web.get(DeFiLlama) → exec_prompt → risk JSON
         └─ [Validator 5] web.get(DeFiLlama) → exec_prompt → risk JSON
                  │
         eq_principle.prompt_comparative()
         "Equivalent if risk_level, audit_status, tvl_trend match"
                  │
         MAJORITY_AGREE → store RiskReport on-chain
```

---

## Repository Structure

```
contracts/
  defi_risk_analyzer.py   # Intelligent Contract (GenLayer Python)
deploy/
  deployScript.ts         # Deploys the contract to Bradbury Testnet
  run.ts                  # Deploy + call analyze_protocol + read results
  read.ts                 # Read stored reports from an existing contract
```

---

## Prerequisites

- Node.js 18+
- GEN tokens on Bradbury — [get from faucet](https://testnet-faucet.genlayer.foundation/)
- Any Ethereum wallet private key (MetaMask, or generate one)

---

## Setup

```bash
git clone https://github.com/UnityNodes/defi_risk_analyzer
cd defi_risk_analyzer
npm install
```

---

## Deploy and Run

```bash
# Set your funded private key
export PRIVATE_KEY="your_private_key_here"

# Deploy a new contract and run analysis
npx tsx deploy/run.ts "Aave" 1000 "low"

# Or use the already-deployed contract
export CONTRACT_ADDRESS="0xC138cC96061e9F160C94da33e2B7085ff45100ba"
npx tsx deploy/run.ts "Uniswap" 5000 "medium"
```

**Supported arguments:**

| Argument | Description | Examples |
|---|---|---|
| `protocol` | DeFi protocol name | `"Aave"`, `"Uniswap"`, `"Curve"`, `"Lido"` |
| `amount` | Investment amount in USD | `1000`, `5000`, `50000` |
| `risk_tolerance` | Your risk profile | `"low"`, `"medium"`, `"high"` |

---

## Read Stored Reports

```bash
export CONTRACT_ADDRESS="0xC138cC96061e9F160C94da33e2B7085ff45100ba"
npx tsx deploy/read.ts
```

---

## Contract API

### Write Methods

| Method | Description |
|---|---|
| `analyze_protocol(protocol, amount, risk_tolerance)` | Fetches live data, runs AI analysis across validators, stores result on-chain |

### Read Methods

| Method | Returns |
|---|---|
| `get_reports(user)` | JSON array of all risk reports for an address |
| `get_reports_len(user)` | Number of stored reports |
| `get_profile(user)` | Stored risk tolerance for an address |
| `get_all_reports()` | Map of all addresses to their report count |

---

## Why This Matters

Traditional risk tools:
- Are run by centralized teams (trust required)
- Use static or manually-updated data
- Produce results that can be manipulated

This contract:
- Fetches data live at execution time from a public API
- Has no single AI model — 5 validators reason independently
- Reaches consensus via protocol-enforced equivalence, not a trusted aggregator
- Stores results permanently on a public blockchain

The result is a risk assessment that is **verifiable, reproducible, and trustless**.

---

## Troubleshooting

| Issue | Fix |
|---|---|
| `LEADER TIMEOUT` | Bradbury testnet instability — resubmit the transaction |
| `ACCEPTED (ERROR)` | Check contract logs in the [Bradbury explorer](https://explorer-bradbury.genlayer.com) |
| Transaction not finalizing | Increase `retries` in `run.ts` — Bradbury can take 5–10 min under load |
| `No PRIVATE_KEY` | Set `export PRIVATE_KEY=...` before running |
| `readContract` hanging | Known Bradbury RPC limitation — `read.ts` has a 15s timeout built in |

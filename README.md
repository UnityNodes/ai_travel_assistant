# AI DeFi Risk Analyzer

An Intelligent Contract on **GenLayer Bradbury Testnet** that analyzes DeFi protocol risk using live blockchain data, non-deterministic AI, and decentralized validator consensus.

**Deployed contract:** [`0xC138cC96061e9F160C94da33e2B7085ff45100ba`](https://explorer-bradbury.genlayer.com/address/0xC138cC96061e9F160C94da33e2B7085ff45100ba)

---

## What it does

When a user calls `analyze_protocol("Aave", 1000, "low")`, the contract:

1. **Fetches live data** — pulls real-time TVL and protocol metrics from DeFiLlama
2. **Runs AI analysis** — each of 5 independent validators executes an LLM prompt to generate a structured risk report
3. **Reaches consensus** — validator outputs are compared via the Equivalence Principle; if `risk_level`, `audit_status`, and `tvl_trend` match, the result is finalized
4. **Stores on-chain** — the risk report is permanently written to contract storage

```json
{
  "risk_score": 3,
  "risk_level": "low",
  "tvl_usd": "$12.1B",
  "tvl_trend": "stable",
  "audit_status": "audited",
  "audit_firms": ["OpenZeppelin", "Trail of Bits"],
  "incident_risk": "low",
  "recommendation": "Aave is one of the most battle-tested DeFi protocols.",
  "warnings": [],
  "suggested_allocation": 20
}
```

---

## GenLayer capabilities

| Capability | Usage |
|---|---|
| `gl.nondet.web.get()` | Fetches live protocol data from DeFiLlama API |
| `gl.nondet.exec_prompt()` | Runs LLM risk analysis on each validator independently |
| `gl.eq_principle.prompt_comparative()` | Reaches consensus across validators by comparing AI outputs |

---

## Repository structure

```
contracts/
  defi_risk_analyzer.py   # Intelligent Contract
deploy/
  deployScript.ts         # Deploys the contract to Bradbury
  run.ts                  # Deploy + call analyze_protocol + read results
  read.ts                 # Read stored reports from an existing contract
```

---

## Prerequisites

- Node.js 18+
- GEN tokens on Bradbury — [get from faucet](https://testnet-faucet.genlayer.foundation/)
- MetaMask or any Ethereum wallet private key

---

## Setup

```bash
npm install
```

---

## Deploy and run

```bash
# Set your funded private key
$env:PRIVATE_KEY="your_private_key_here"

# Deploy a new contract and run analysis
npx tsx deploy/run.ts "Aave" 1000 "low"

# Or use the already-deployed contract
$env:CONTRACT_ADDRESS="0xC138cC96061e9F160C94da33e2B7085ff45100ba"
npx tsx deploy/run.ts "Uniswap" 5000 "medium"
```

**Supported arguments:**

| Argument | Description | Example |
|---|---|---|
| `protocol` | DeFi protocol name | `"Aave"`, `"Uniswap"`, `"Curve"` |
| `amount` | Investment amount in USD | `1000` |
| `risk_tolerance` | Risk profile | `"low"`, `"medium"`, `"high"` |

---

## Read stored reports

```bash
$env:CONTRACT_ADDRESS="0xC138cC96061e9F160C94da33e2B7085ff45100ba"
npx tsx deploy/read.ts
```

---

## Contract API

### Write

| Method | Description |
|---|---|
| `analyze_protocol(protocol, amount, risk_tolerance)` | Fetches live data, runs AI analysis, stores result on-chain |

### Read

| Method | Returns |
|---|---|
| `get_reports(user)` | JSON array of all risk reports for an address |
| `get_reports_len(user)` | Number of stored reports |
| `get_profile(user)` | Stored risk tolerance for an address |
| `get_all_reports()` | Map of all addresses to report count |

---

## Troubleshooting

| Issue | Fix |
|---|---|
| `LEADER TIMEOUT` | Bradbury testnet instability — resubmit the transaction |
| `ACCEPTED (ERROR)` | Check contract logs in the explorer |
| Transaction not finalizing | Increase `retries` in `run.ts` — Bradbury can take 5–10 min |
| `No PRIVATE_KEY` | Set `$env:PRIVATE_KEY` before running |

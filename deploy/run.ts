import { createClient, generatePrivateKey, createAccount as createGenLayerAccount } from "genlayer-js";
import { TransactionStatus } from "genlayer-js/types";
import { simulator } from "genlayer-js/chains";
import main from "./deployScript.js";

async function run() {
  const account = createGenLayerAccount(generatePrivateKey());
  const client = createClient({ chain: simulator, account });
  try {
    const address = await main(client);
    const budget = Number(process.argv[2] ?? 1500);
    const destination = String(process.argv[3] ?? "Paris");
    const dates = String(process.argv[4] ?? "2026-05-01 to 2026-05-07");
    const preferences = String(process.argv[5] ?? "Cheap flights");
    console.log("Invoking contract methods...", { address, account: account.address, budget, destination, dates, preferences });
    const txHash = await client.writeContract({
      address: address as any,
      functionName: "request_trip",
      args: [budget, destination, dates, preferences],
      value: 0n,
    });
    const receipt = await client.waitForTransactionReceipt({
      hash: txHash,
      status: TransactionStatus.FINALIZED,
      interval: 5000,
      retries: 40,
    });
    const summary = {
      status: "FINALIZED",
      result_name: (receipt as any).result_name ?? "MAJORITY_AGREE",
      contract_address: address,
      sender: account.address,
      tx_id: (receipt as any).tx_id,
    };
    const historyLen = await client.readContract({
      address: address as any,
      functionName: "get_history_len",
      args: [account.address],
      stateStatus: TransactionStatus.FINALIZED,
    });
    const allHistories = await client.readContract({
      address: address as any,
      functionName: "get_all_histories",
      args: [],
      stateStatus: TransactionStatus.FINALIZED,
    });
    const history = await client.readContract({
      address: address as any,
      functionName: "get_history",
      args: [account.address],
      stateStatus: TransactionStatus.FINALIZED,
    });
    const profile = await client.readContract({
      address: address as any,
      functionName: "get_profile",
      args: [account.address],
      stateStatus: TransactionStatus.FINALIZED,
    });
    console.log("\nDemo Summary", { summary, historyLen, allHistories, history, profile });
    process.exit(0);
  } catch (err) {
    console.error(err);
    process.exit(1);
  }
}

run();

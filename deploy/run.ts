import {
  createClient,
  generatePrivateKey,
  createAccount as createGenLayerAccount,
} from "genlayer-js";
import { TransactionStatus } from "genlayer-js/types";
import { localnet } from "genlayer-js/chains";
import main from "./deployScript.js";

async function run() {
  const account = createGenLayerAccount(generatePrivateKey());
  const client = createClient({ chain: localnet, account });

  try {
    // 1. Deploy contract
    const address = await main(client);

    // 2. Parse CLI arguments
    const budget = Number(process.argv[2] ?? 1500);
    const destination = String(process.argv[3] ?? "France");
    const dates = String(process.argv[4] ?? "2026-05-01 to 2026-05-07");
    const preferences = String(
      process.argv[5] ?? "Cheap flights, cultural tours"
    );

    console.log("\nRequesting trip...", {
      address,
      sender: account.address,
      budget,
      destination,
      dates,
      preferences,
    });

    // 3. Write: request_trip
    const txHash = await client.writeContract({
      address: address as any,
      functionName: "request_trip",
      args: [budget, destination, dates, preferences],
      value: 0n,
    });

    console.log("Transaction sent:", txHash);
    console.log("Waiting for FINALIZED status (this may take a minute)...");

    const receipt = await client.waitForTransactionReceipt({
      hash: txHash,
      status: TransactionStatus.FINALIZED,
      interval: 10000,
      retries: 120,
    });

    console.log("\nTransaction finalized!");
    console.log("Result:", (receipt as any).result_name ?? "MAJORITY_AGREE");

    // 4. Read: get_history
    const history = await client.readContract({
      address: address as any,
      functionName: "get_history",
      args: [account.address],
    });

    // 5. Read: get_history_len
    const historyLen = await client.readContract({
      address: address as any,
      functionName: "get_history_len",
      args: [account.address],
    });

    // 6. Read: get_profile
    const profile = await client.readContract({
      address: address as any,
      functionName: "get_profile",
      args: [account.address],
    });

    // 7. Read: get_all_histories
    const allHistories = await client.readContract({
      address: address as any,
      functionName: "get_all_histories",
      args: [],
    });

    console.log("\n=== Demo Summary ===");
    console.log("Contract:", address);
    console.log("Sender:", account.address);
    console.log("History length:", historyLen);
    console.log("Profile:", profile);
    console.log("All histories:", JSON.stringify(allHistories));
    console.log("\nTrip history:");
    console.log(typeof history === "string" ? history : JSON.stringify(history, null, 2));

    process.exit(0);
  } catch (err) {
    console.error("Error:", err);
    process.exit(1);
  }
}

run();

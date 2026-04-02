import { createClient, generatePrivateKey, createAccount as createGenLayerAccount, chains } from "genlayer-js";
import { TransactionStatus } from "genlayer-js/types";
import main from "./deployScript.js";

const testnetBradbury = chains.testnetBradbury;

async function run() {
  let rawKey = process.env.PRIVATE_KEY ?? "";
  if (rawKey.length > 0) {
    if (!rawKey.startsWith("0x")) rawKey = "0x" + rawKey;
  } else {
    rawKey = generatePrivateKey();
  }
  const account = createGenLayerAccount(rawKey as `0x${string}`);
  const client = createClient({ chain: testnetBradbury, account });

  try {
    const protocol = String(process.argv[2] ?? "Aave");
    const amount = Number(process.argv[3] ?? 1000);
    const riskTolerance = String(process.argv[4] ?? "low");
    const existingAddress = process.env.CONTRACT_ADDRESS ?? "";

    let address: string;
    if (existingAddress) {
      address = existingAddress;
      console.log("\nUsing existing contract:", address);
    } else {
      address = await main(client);
    }

    console.log("\nAnalyzing protocol...", { address, sender: account.address, protocol, amount, riskTolerance });

    const txHash = await client.writeContract({
      address: address as any,
      functionName: "analyze_protocol",
      args: [protocol, amount, riskTolerance],
      value: 0n,
    });

    console.log("Transaction sent:", txHash);
    console.log("Waiting for FINALIZED status (Bradbury may take 1-3 minutes)...");

    const receipt = await client.waitForTransactionReceipt({
      hash: txHash,
      status: TransactionStatus.FINALIZED,
      interval: 10000,
      retries: 120,
    });

    console.log("\nTransaction finalized!");
    console.log("Result:", (receipt as any).result_name ?? "MAJORITY_AGREE");

    const reports    = await client.readContract({ address: address as any, functionName: "get_reports",     args: [account.address] });
    const reportsLen = await client.readContract({ address: address as any, functionName: "get_reports_len", args: [account.address] });
    const profile    = await client.readContract({ address: address as any, functionName: "get_profile",     args: [account.address] });
    const allReports = await client.readContract({ address: address as any, functionName: "get_all_reports", args: [] });

    console.log("\n=== DeFi Risk Analysis Summary ===");
    console.log("Contract:", address);
    console.log("Sender:", account.address);
    console.log("Reports count:", reportsLen);
    console.log("Profile:", profile);
    console.log("All reports:", JSON.stringify(allReports));
    console.log("\nRisk report:");
    console.log(typeof reports === "string" ? reports : JSON.stringify(reports, null, 2));

    process.exit(0);
  } catch (err) {
    console.error("Error:", err);
    process.exit(1);
  }
}

run();

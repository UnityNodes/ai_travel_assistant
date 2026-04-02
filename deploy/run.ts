import {
  createClient,
  generatePrivateKey,
  createAccount as createGenLayerAccount,
} from "genlayer-js";
import { TransactionStatus } from "genlayer-js/types";
import { testnetBradbury } from "genlayer-js/chains";
import main from "./deployScript.js";

async function run() {
  // On Bradbury testnet use a persistent private key so the funded account is reused.
  // Set PRIVATE_KEY env var to your funded account, or a fresh key will be generated.
  const privateKey = (process.env.PRIVATE_KEY as `0x${string}`) ?? generatePrivateKey();
  const account = createGenLayerAccount(privateKey);
  const client = createClient({ chain: testnetBradbury, account });

  try {
    // 1. Deploy contract
    const address = await main(client);

    // 2. Parse CLI arguments
    const protocol = String(process.argv[2] ?? "Aave");
    const amount = Number(process.argv[3] ?? 1000);
    const riskTolerance = String(process.argv[4] ?? "low");

    console.log("\nAnalyzing protocol...", {
      address,
      sender: account.address,
      protocol,
      amount,
      riskTolerance,
    });

    // 3. Write: analyze_protocol
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
      interval: 5000,
      retries: 60,
    });

    console.log("\nTransaction finalized!");
    console.log("Result:", (receipt as any).result_name ?? "MAJORITY_AGREE");

    // 4. Read: get_reports
    const reports = await client.readContract({
      address: address as any,
      functionName: "get_reports",
      args: [account.address],
    });

    // 5. Read: get_reports_len
    const reportsLen = await client.readContract({
      address: address as any,
      functionName: "get_reports_len",
      args: [account.address],
    });

    // 6. Read: get_profile
    const profile = await client.readContract({
      address: address as any,
      functionName: "get_profile",
      args: [account.address],
    });

    // 7. Read: get_all_reports
    const allReports = await client.readContract({
      address: address as any,
      functionName: "get_all_reports",
      args: [],
    });

    console.log("\n=== DeFi Risk Analysis Summary ===");
    console.log("Contract:", address);
    console.log("Sender:", account.address);
    console.log("Reports count:", reportsLen);
    console.log("Risk tolerance profile:", profile);
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

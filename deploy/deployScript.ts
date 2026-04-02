import { readFileSync } from "fs";
import path from "path";
import type { TransactionHash, GenLayerClient } from "genlayer-js/types";
import { TransactionStatus } from "genlayer-js/types";

export default async function main(client: GenLayerClient<any>) {
  const contractCode = new Uint8Array(
    readFileSync(path.resolve(process.cwd(), "contracts/defi_risk_analyzer.py"))
  );

  const deployTransaction = await client.deployContract({ code: contractCode, args: [] });

  console.log("Deploy tx sent:", deployTransaction);
  console.log("Waiting for ACCEPTED (Bradbury ~1-3 min)...");

  let dots = 0;
  const ticker = setInterval(() => {
    dots++;
    process.stdout.write(`\r  waiting${".".repeat(dots % 4).padEnd(3)} ${dots * 5}s elapsed`);
  }, 5000);

  const receipt = await client.waitForTransactionReceipt({
    hash: deployTransaction as TransactionHash,
    status: TransactionStatus.ACCEPTED,
    interval: 5000,
    retries: 200,
  });

  clearInterval(ticker);
  process.stdout.write("\n");

  const r = receipt as any;
  const address =
    r?.data?.contract_address ??
    r?.txDataDecoded?.contractAddress ??
    r?.contractAddress ??
    null;

  if (!address) {
    const safe = JSON.stringify(receipt, (_k, v) => (typeof v === "bigint" ? v.toString() : v));
    throw new Error(`Deployment failed — no contract_address in receipt: ${safe}`);
  }

  console.log("\nContract deployed successfully.", {
    "Transaction Hash": deployTransaction,
    "Contract Address": address,
  });

  return address as string;
}

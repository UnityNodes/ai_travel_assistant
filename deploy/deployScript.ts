import { readFileSync } from "fs";
import path from "path";
import type { TransactionHash, GenLayerClient } from "genlayer-js/types";
import { TransactionStatus } from "genlayer-js/types";

export default async function main(client: GenLayerClient<any>) {
  const filePath = path.resolve(process.cwd(), "contracts/travel_assistant.py");

  const contractCode = new Uint8Array(readFileSync(filePath));

  const deployTransaction = await client.deployContract({
    code: contractCode,
    args: [],
  });

  const receipt = await client.waitForTransactionReceipt({
    hash: deployTransaction as TransactionHash,
    status: TransactionStatus.ACCEPTED,
    retries: 200,
  });

  const address = (receipt as any).data?.contract_address;

  if (!address) {
    throw new Error(
      `Deployment failed — no contract_address in receipt: ${JSON.stringify(receipt)}`
    );
  }

  console.log("\nContract deployed successfully.", {
    "Transaction Hash": deployTransaction,
    "Contract Address": address,
  });

  return address as string;
}

import { readFileSync } from "fs";
import path from "path";
import { TransactionHash, TransactionStatus, GenLayerClient } from "genlayer-js/types";


export default async function main(client: GenLayerClient<any>) {
  const filePath = path.resolve(process.cwd(), "contracts/travel_assistant.py");

  try {
    const contractCode = new Uint8Array(readFileSync(filePath));

    if ("initializeConsensusSmartContract" in client && typeof (client as any).initializeConsensusSmartContract === "function") {
      await (client as any).initializeConsensusSmartContract();
    }

    const deployTransaction = await client.deployContract({
      code: contractCode,
      args: [],
    });

    const receipt = await client.waitForTransactionReceipt({
      hash: deployTransaction as TransactionHash,
      status: TransactionStatus.ACCEPTED,
      retries: 200,
    });

    const exec = receipt.consensus_data?.leader_receipt?.[0]?.execution_result ?? (receipt as any)?.data?.status ?? "SUCCESS";
    if (exec !== "SUCCESS") {
      throw new Error(`Deployment failed. Receipt: ${JSON.stringify(receipt)}`);
    }

    const address = (receipt as any).data?.contract_address;
    console.log("\n Contract deployed successfully.", {
      "Transaction Hash": deployTransaction,
      "Contract Address": address,
    });
    return address as string;
  } catch (error) {
    if (error instanceof Error) {
      throw error;
    }
    throw new Error(`Error during deployment: ${String(error)}`);
  }
}

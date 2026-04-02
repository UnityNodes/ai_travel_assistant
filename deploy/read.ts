import { createClient, generatePrivateKey, createAccount as createGenLayerAccount, chains } from "genlayer-js";

const testnetBradbury = chains.testnetBradbury;

async function read() {
  let rawKey = process.env.PRIVATE_KEY ?? "";
  if (!rawKey.startsWith("0x")) rawKey = "0x" + rawKey;
  const privateKey = rawKey as `0x${string}`;
  const account = createGenLayerAccount(privateKey);
  const client = createClient({ chain: testnetBradbury, account });

  const address = process.env.CONTRACT_ADDRESS ?? process.argv[2];
  if (!address) { console.error("Set CONTRACT_ADDRESS or pass as argument"); process.exit(1); }

  console.log("\nReading contract:", address);
  console.log("Account:", account.address);

  const timeout = (ms: number) => new Promise((_, reject) =>
    setTimeout(() => reject(new Error(`Timeout after ${ms}ms`)), ms)
  );
  const read = (fn: string, args: any[]) =>
    Promise.race([
      client.readContract({ address: address as any, functionName: fn, args }),
      timeout(15000),
    ]);

  const reports    = await read("get_reports",     [account.address]);
  const reportsLen = await read("get_reports_len", [account.address]);
  const profile    = await read("get_profile",     [account.address]);
  const allReports = await read("get_all_reports", []);

  console.log("\n=== On-chain Data ===");
  console.log("Reports count:", reportsLen);
  console.log("Profile:", profile);
  console.log("All reports:", allReports);
  console.log("\nYour reports:");
  console.log(typeof reports === "string" ? reports : JSON.stringify(reports, null, 2));

  process.exit(0);
}

read().catch((err) => { console.error(err); process.exit(1); });

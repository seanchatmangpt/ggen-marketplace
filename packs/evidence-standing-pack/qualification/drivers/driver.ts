// Golden-vector driver (bun). Usage: bun driver.ts <golden.vec>; imports generated src/es/chain.ts.
import { readFileSync } from "node:fs";
import { append, seal, verify, type Chain } from "./src/es/chain.ts";

let chain: Chain = [];
for (const raw of readFileSync(process.argv[2], "utf8").split("\n")) {
  if (!raw || raw.startsWith("#")) continue;
  const p = raw.split("|");
  if (raw.startsWith("case ")) { chain = []; console.log("case", raw.slice(5)); }
  else if (p[0] === "append" || p[0] === "seal") {
    try {
      const e = p[0] === "append" ? append(chain, p[1], p[2], p[3], p[4], p[5]) : seal(chain, p[1], p[2], p[3]);
      console.log("ok", e.hash);
    } catch { console.log("err"); }
  } else if (p[0] === "verify") console.log("verify", verify(chain) ? "true" : "false");
  else if (p[0] === "tamper") { chain[0].subject = "tampered"; console.log("tampered"); }
}

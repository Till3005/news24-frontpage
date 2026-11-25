import { createHash } from "node:crypto";
import { copyFile, mkdir, readFile, rename, stat } from "node:fs/promises";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const PNG_SIGNATURE = [0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a];

const here = dirname(fileURLToPath(import.meta.url));
const sourcePath = join(here, "entry.png");
const outputDir = process.env.MAKEFUN_OUTPUT_DIR ?? "/output";
const copyPath = resolve(outputDir, "entry.png");

function sha256(data: Buffer): string {
  return createHash("sha256").update(data).digest("hex");
}

function startsWithPngSignature(data: Buffer): boolean {
  return (
    data.length >= PNG_SIGNATURE.length &&
    PNG_SIGNATURE.every((byte, i) => data[i] === byte)
  );
}

function die(message: string): never {
  console.error(`FAIL: ${message}`);
  process.exit(1);
}

async function main(): Promise<void> {
  let source: Buffer;
  try {
    source = await readFile(sourcePath);
  } catch {
    die(`cannot read ${sourcePath}`);
  }

  if (!startsWithPngSignature(source)) {
    die(`${sourcePath} lacks the PNG magic signature in its first 8 bytes`);
  }

  try {
    await mkdir(outputDir, { recursive: true });
    const tmpPath = `${copyPath}.tmp`;
    await copyFile(sourcePath, tmpPath);
    await rename(tmpPath, copyPath);
    const info = await stat(copyPath);
    if (!info.isFile()) {
      die(`${copyPath} is not a regular file`);
    }
  } catch (err) {
    die(`copy into ${outputDir} failed: ${err instanceof Error ? err.message : err}`);
  }

  let copied: Buffer;
  try {
    copied = await readFile(copyPath);
  } catch {
    die(`cannot re-read ${copyPath}`);
  }

  if (!startsWithPngSignature(copied)) {
    die(`${copyPath} lacks the PNG magic signature in its first 8 bytes`);
  }

  const sourceHash = sha256(source);
  const copyHash = sha256(copied);
  if (sourceHash !== copyHash) {
    die(`sha256 mismatch: source ${sourceHash} vs copy ${copyHash}`);
  }

  console.log(`OK entry.png: valid PNG, copied to ${copyPath}, sha256 ${sourceHash} (${copied.length} bytes)`);
}

await main();

#!/usr/bin/env node
// Prepare a candidate only. Service installation and activation are manual.
import { constants, accessSync, lstatSync, statSync, openSync, readFileSync, writeFileSync, closeSync } from "node:fs";
import { isAbsolute } from "node:path";
import { parseEnv } from "node:util";

const usage = `Usage: node t3-service-env.mjs --gh /absolute/path/to/gh --output NEW_FILE [--input EXISTING_COPY]

Prepare T3 Code v0.1.6 service.env with GitHub HTTPS transport and gh credentials.
Requires Node 22.16+. No packages, network access, credential lookup, or activation.
Reads only an explicit input; never overwrites a file. Output has mode 600.
Current shell indexed Git config is preserved before input-file entries.
`;
const gitVariable = /^GIT_CONFIG_(?:COUNT$|(?:KEY|VALUE)_)/;

function gitEntries(environment, label) {
  const variables = Object.keys(environment).filter((key) => gitVariable.test(key));
  if (variables.length === 0) return [];
  const count = environment.GIT_CONFIG_COUNT;
  if (!/^(0|[1-9][0-9]*)$/.test(count ?? "") || Number(count) > 10000) {
    throw new Error(`${label}: require GIT_CONFIG_COUNT between 0 and 10000.`);
  }
  const expected = new Set(["GIT_CONFIG_COUNT"]);
  const entries = [];
  for (let index = 0; index < Number(count); index++) {
    const key = `GIT_CONFIG_KEY_${index}`;
    const value = `GIT_CONFIG_VALUE_${index}`;
    if (!Object.hasOwn(environment, key) || !Object.hasOwn(environment, value) || !environment[key]) {
      throw new Error(`${label}: missing Git key/value pair at index ${index}.`);
    }
    entries.push([environment[key], environment[value]]);
    expected.add(key);
    expected.add(value);
  }
  if (variables.some((key) => !expected.has(key))) {
    throw new Error(`${label}: orphaned or malformed indexed Git variables; repair before preparing.`);
  }
  return entries;
}

function sameEntries(left, right) {
  return JSON.stringify(left) === JSON.stringify(right);
}

// Node dotenv quotes are literal; double quotes alone expand backslash-n.
function envValue(value) {
  if (/[\r\n\0]/.test(value)) throw new Error("Indexed Git values must be single-line, without NUL.");
  for (const quote of ["'", '"', "`"]) {
    if (!value.includes(quote) && !(quote === '"' && value.includes("\\n"))) {
      return `${quote}${value}${quote}`;
    }
  }
  throw new Error("An indexed Git value contains all three quote characters; prepare it manually.");
}

function prepare(input, inherited, gh) {
  const current = parseEnv(input);
  const fromShell = gitEntries(inherited, "Shell environment");
  const fromFile = gitEntries(current, "Input file");
  // A previously generated candidate already contains the inherited prefix.
  const entries = sameEntries(fromFile.slice(0, fromShell.length), fromShell)
    ? [...fromFile]
    : [...fromShell, ...fromFile];
  const shellPath = `'${gh.replaceAll("'", `'"'"'`)}'`;
  const settings = [
    ["url.https://github.com/.insteadOf", "git@github.com:"],
    ["url.https://github.com/.insteadOf", "ssh://git@github.com/"],
    ["credential.https://github.com.helper", ""],
    ["credential.https://github.com.helper", `!${shellPath} auth git-credential`],
  ];
  if (!sameEntries(entries.slice(-settings.length), settings)) entries.push(...settings);
  if (sameEntries(entries, fromFile)) return input;

  const additions = [`GIT_CONFIG_COUNT=${entries.length}`];
  entries.forEach(([key, value], index) => {
    additions.push(`GIT_CONFIG_KEY_${index}=${envValue(key)}`);
    additions.push(`GIT_CONFIG_VALUE_${index}=${envValue(value)}`);
  });
  const result = input + (input && !input.endsWith("\n") ? "\n" : "")
    + "# AI-Agents: T3-only GitHub HTTPS transport and gh credential helper\n"
    + additions.join("\n") + "\n";
  const parsed = parseEnv(result);
  if (!sameEntries(gitEntries(parsed, "Candidate"), entries)
      || Object.entries(current).some(([key, value]) => !gitVariable.test(key) && parsed[key] !== value)) {
    throw new Error("Candidate did not round-trip through T3's env parser; repair input quoting.");
  }
  return result;
}

function main() {
  const args = process.argv.slice(2);
  if (args.length === 1 && ["--help", "-h"].includes(args[0])) {
    console.log(usage);
    return;
  }
  const options = {};
  for (let index = 0; index < args.length; index += 2) {
    const option = args[index];
    if (!["--input", "--output", "--gh"].includes(option)
        || !args[index + 1] || args[index + 1].startsWith("--") || Object.hasOwn(options, option)) {
      throw new Error("Invalid or repeated option. Use --help for usage.");
    }
    options[option] = args[index + 1];
  }
  const gh = options["--gh"];
  if (!gh || !isAbsolute(gh) || !options["--output"]) {
    throw new Error("Require --gh with an absolute executable path and --output with a new file path.");
  }
  // Validate presence only; never run gh or inspect its authentication store.
  if (!statSync(gh).isFile()) throw new Error("The gh path must name an executable file.");
  accessSync(gh, constants.X_OK);
  const inputPath = options["--input"];
  if (inputPath && !lstatSync(inputPath).isFile()) {
    throw new Error("Input must be a regular file, not a symlink.");
  }
  const input = inputPath
    ? new TextDecoder("utf-8", { fatal: true, ignoreBOM: true }).decode(readFileSync(inputPath))
    : "";
  const result = prepare(input, process.env, gh);
  const descriptor = openSync(options["--output"], "wx", 0o600);
  try {
    writeFileSync(descriptor, result);
  } finally {
    closeSync(descriptor);
  }
  console.log("Prepared a private candidate. Nothing has been installed or activated.");
}

try {
  main();
} catch (error) {
  // Never print env-file contents or indexed values, which may contain credentials.
  console.error(`Preparation failed: ${error.message}`);
  process.exitCode = 1;
}

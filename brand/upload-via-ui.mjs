#!/usr/bin/env node
/**
 * Upload pre-rendered social preview PNGs to GitHub repo Settings via Playwright.
 * GitHub has no public REST/GraphQL API for social preview images.
 *
 * First run (once): node upload-via-ui.mjs --login
 * Then:            node upload-via-ui.mjs
 */

import fs from "fs";
import os from "os";
import path from "path";
import { fileURLToPath } from "url";
import { chromium } from "playwright";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = __dirname;
const OUT = path.join(ROOT, "output", "social-preview");
const REPOS_JSON = path.join(ROOT, "repos.json");

function defaultStorageStatePath() {
  const xdg = process.env.XDG_STATE_HOME || path.join(os.homedir(), ".local", "state");
  return path.join(xdg, "skyphusion-brand", "github-auth.json");
}

function parseArgs(argv) {
  const out = { _: [] };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === "--login") out.login = true;
    else if (a === "--headless") out.headless = argv[++i] !== "false";
    else if (a === "--storage-state") out.storageState = argv[++i];
    else if (a === "--repo") out.repo = argv[++i];
    else if (!a.startsWith("--")) out._.push(a);
  }
  return out;
}

async function initAuth(storageStatePath) {
  fs.mkdirSync(path.dirname(storageStatePath), { recursive: true });
  const browser = await chromium.launch({ headless: false });
  const context = await browser.newContext({ viewport: { width: 1280, height: 720 } });
  const page = await context.newPage();
  await page.goto("https://github.com/login", { waitUntil: "domcontentloaded" });
  console.log("Log into GitHub in the browser window. Waiting for session...");
  await page.waitForFunction(() => {
    const login = document.querySelector('meta[name="user-login"]')?.content?.trim();
    return !!login;
  }, null, { timeout: 0, polling: 500 });
  const user = await page.evaluate(() => document.querySelector('meta[name="user-login"]')?.content?.trim() || "");
  await context.storageState({ path: storageStatePath });
  await browser.close();
  console.log(`Saved session for @${user} -> ${storageStatePath}`);
}

async function uploadOne(page, repo, imagePath) {
  const settingsUrl = `https://github.com/${repo}/settings`;
  console.log(`Uploading ${path.basename(imagePath)} -> ${repo}`);
  const resp = await page.goto(settingsUrl, { waitUntil: "domcontentloaded" });
  const username = await page.evaluate(() => document.querySelector('meta[name="user-login"]')?.content?.trim() || "");
  if (page.url().includes("/login") || !username) {
    throw new Error("Not authenticated. Run: node upload-via-ui.mjs --login");
  }
  if (resp && resp.status() === 404) {
    throw new Error(`Settings 404 for ${repo} (need admin on @${username})`);
  }

  const socialHeading = page.locator("xpath=//h2[normalize-space()='Social preview']").first();
  await socialHeading.waitFor({ state: "attached", timeout: 60_000 });
  await socialHeading.scrollIntoViewIfNeeded().catch(() => {});

  const editButton = page.locator("#edit-social-preview-button");
  const socialEditButton = page.locator(
    "xpath=(//h2[normalize-space()='Social preview']/following::*[(self::button or self::summary) and normalize-space(.)='Edit'][1])"
  );
  if (await editButton.count()) await editButton.first().click({ force: true }).catch(() => {});
  else if (await socialEditButton.count()) await socialEditButton.first().click({ force: true }).catch(() => {});

  const fileInput = page.locator("input#repo-image-file-input");
  const uploadMenuItem = page.getByText(/upload an image/i).first();
  await Promise.any([
    fileInput.first().waitFor({ state: "attached", timeout: 30_000 }),
    uploadMenuItem.waitFor({ state: "visible", timeout: 30_000 }),
  ]);

  const uploadResponsePromise = page
    .waitForResponse((resp) => {
      const u = resp.url();
      const ok = resp.status() >= 200 && resp.status() < 300;
      return ok && (u.includes("/upload/repository-images/") || u.includes("/upload/policies/repository-images"));
    }, { timeout: 30_000 })
    .catch(() => null);

  if (await fileInput.count()) {
    await fileInput.first().setInputFiles(imagePath);
  } else {
    const [chooser] = await Promise.all([page.waitForEvent("filechooser"), uploadMenuItem.click({ force: true })]);
    await chooser.setFiles(imagePath);
  }

  await uploadResponsePromise;
  await page.waitForFunction(() => {
    const input = document.querySelector("input.js-repository-image-id");
    return !!((input?.value || "").trim());
  }, { timeout: 30_000 });
  console.log(`  ok: ${repo}`);
}

function loadUploads(singleRepo) {
  const repos = JSON.parse(fs.readFileSync(REPOS_JSON, "utf8"));
  const items = repos.map((r) => ({
    repo: `${r.owner}/${r.repo}`,
    safe: `${r.owner}__${r.repo.replace(/\./g, "_")}.png`,
  }));
  if (singleRepo) {
    const hit = items.find((i) => i.repo === singleRepo);
    if (!hit) throw new Error(`Repo not in repos.json: ${singleRepo}`);
    return [hit];
  }
  return items;
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  const storageStatePath = path.resolve(args.storageState || defaultStorageStatePath());

  if (args.login) {
    await initAuth(storageStatePath);
    if (!args.repo && args._.length === 0) return;
  }

  if (!fs.existsSync(storageStatePath)) {
    console.error(`No session at ${storageStatePath}. Run: node upload-via-ui.mjs --login`);
    process.exit(1);
  }

  const uploads = loadUploads(args.repo || args._[0] || null);
  const browser = await chromium.launch({ headless: args.headless !== false });
  const context = await browser.newContext({ storageState: storageStatePath, viewport: { width: 1280, height: 720 } });
  const page = await context.newPage();

  let ok = 0;
  let fail = 0;
  for (const { repo, safe } of uploads) {
    const imagePath = path.join(OUT, safe);
    if (!fs.existsSync(imagePath)) {
      console.error(`Missing PNG: ${imagePath}`);
      fail++;
      continue;
    }
    try {
      await uploadOne(page, repo, imagePath);
      ok++;
    } catch (err) {
      console.error(`  FAIL ${repo}: ${err.message}`);
      fail++;
    }
  }

  await context.storageState({ path: storageStatePath });
  await browser.close();
  console.log(`Done: ${ok} uploaded, ${fail} failed`);
  if (fail) process.exitCode = 1;
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});

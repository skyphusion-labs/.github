#!/usr/bin/env node
/** Try uploading using the system Chrome profile (existing github.com session). */
import fs from "fs";
import os from "os";
import path from "path";
import { fileURLToPath } from "url";
import { chromium } from "playwright";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const OUT = path.join(__dirname, "output", "social-preview");
const REPOS_JSON = path.join(__dirname, "repos.json");

const CHROME_USER_DATA = path.join(os.homedir(), "Library/Application Support/Google/Chrome");

async function uploadOne(page, repo, imagePath) {
  const settingsUrl = `https://github.com/${repo}/settings`;
  console.log(`Uploading -> ${repo}`);
  await page.goto(settingsUrl, { waitUntil: "domcontentloaded", timeout: 60_000 });
  const username = await page.evaluate(() => document.querySelector('meta[name="user-login"]')?.content?.trim() || "");
  if (!username) throw new Error("Not logged into GitHub in Chrome profile");

  const socialHeading = page.locator("xpath=//h2[normalize-space()='Social preview']").first();
  await socialHeading.waitFor({ state: "attached", timeout: 60_000 });
  const editButton = page.locator("#edit-social-preview-button");
  if (await editButton.count()) await editButton.first().click({ force: true }).catch(() => {});
  const fileInput = page.locator("input#repo-image-file-input");
  await fileInput.first().waitFor({ state: "attached", timeout: 30_000 });
  await fileInput.first().setInputFiles(imagePath);
  await page.waitForFunction(() => {
    const input = document.querySelector("input.js-repository-image-id");
    return !!((input?.value || "").trim());
  }, { timeout: 30_000 });
  console.log(`  ok: ${repo}`);
}

async function main() {
  if (!fs.existsSync(CHROME_USER_DATA)) {
    console.error("Chrome user data not found:", CHROME_USER_DATA);
    process.exit(1);
  }

  const repos = JSON.parse(fs.readFileSync(REPOS_JSON, "utf8"));
  const context = await chromium.launchPersistentContext(CHROME_USER_DATA, {
    channel: "chrome",
    headless: false,
    viewport: { width: 1280, height: 720 },
    args: ["--profile-directory=Default"],
  });
  const page = context.pages()[0] || (await context.newPage());

  let ok = 0;
  let fail = 0;
  for (const r of repos) {
    const safe = `${r.owner}__${r.repo.replace(/\./g, "_")}.png`;
    const imagePath = path.join(OUT, safe);
    const repo = `${r.owner}/${r.repo}`;
    try {
      await uploadOne(page, repo, imagePath);
      ok++;
    } catch (err) {
      console.error(`  FAIL ${repo}: ${err.message}`);
      fail++;
    }
  }
  await context.close();
  console.log(`Done: ${ok} uploaded, ${fail} failed`);
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});

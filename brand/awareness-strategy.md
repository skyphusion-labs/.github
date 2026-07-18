# Brand awareness + reach strategy

Deliverable for [#29](https://github.com/skyphusion-labs/.github/issues/29). Builds on the live
baseline (`profile/README.md`, Pages, `brand/` catalogs + CI drift gate, `distribution.md`,
X @skyphusion) -- nothing here reinvents those. Posture every call is scored against: **OSS,
AGPL, not for sale, self-host / own-your-stack, Cloudflare + GPU DIY, one human + AI crew, no
marketing team**. A channel only gets a GO if the cadence survives one busy person.

**Standing rule (unchanged):** Hacker News post TEXT is Conrad-only, always. Crew lane =
repo/launch readiness, never drafting or editing HN copy. That rule is restated where relevant
below.

## A. Awareness channels, ranked

| # | Channel | Audience fit | Effort | Reach | Risk | Call |
|---|---------|--------------|--------|-------|------|------|
| 1 | Hacker News (Show HN) | Exact: dev/OSS/self-host | Low (text is Conrad's) | Highest single-shot | AI-taint sensitivity; one shot per product | **GO** |
| 2 | Reddit (r/selfhosted, r/LocalLLaMA, r/opensource, r/CloudFlare) | Exact intent match | Low-med (participation, not campaigns) | High, durable (threads rank in search) | Self-promo rules; must disclose affiliation | **GO** |
| 3 | Awesome lists + directories (awesome-selfhosted, awesome-cloudflare, MCP registries/awesome-mcp) | Exact | One-time PRs | Modest direct, strong SEO backlinks | Low | **GO** |
| 4 | Dev.to / Hashnode syndication of skyphusion.net posts | Good | Near-zero (canonical-URL crosspost) | Modest + backlinks | Low | **GO** |
| 5 | Cloudflare ecosystem (community showcase, Workers templates) | Strong (the estate is Workers-first) | Med (one template/writeup each) | Modest but high-quality | Low | **GO** |
| 6 | YouTube / PeerTube product demos | Good (vivijure especially) | HIGH (production) | High if sustained | Cadence collapse | **LATER** (gate: a vivijure wow-reel exists) |
| 7 | Hugging Face org / Spaces | Good IF artifacts exist | Med | Med | Empty org = noise | **LATER** (gate: vivijure ships LoRAs/models) |
| 8 | Own Discord server | Med | HIGH ongoing (support burden on one human) | Med | Ghost-town risk | **LATER** (gate: real adopter volume). Presence in existing servers (CF dev Discord): GO-lite, answer-don't-shill |
| 9 | Product Hunt | Weak (skews SaaS; "not for sale" is honest but off-market) | Med | Spiky | Positioning dilution | **LATER**, only with a real launch-day story |
| 10 | Lobsters | Good but invite-culture, mostly HN-overlapping | Low | Low marginal | Etiquette | **SKIP** (fine if Conrad personally wants it) |
| 11 | Civitai / Replicate listings | Poor (backend is a pipeline, not a hosted model product) | Med | Low | Brand mismatch | **SKIP** |
| 12 | Short-form video (Shorts/TikTok/Reels) | Poor | HIGH sustained | Spiky | Unsustainable | **SKIP** |
| 13 | Academic / OSINT citation (common-thread) | Niche, high-credibility | HIGH (needs a real writeup first) | Small but compounding | None | **LATER** (gate: a methods writeup exists) |

Why this ordering: 1-5 are all zero-or-near-zero marginal cost, match search intent the
products actually answer, and leave durable artifacts (threads, backlinks, listings) instead of
feed exhaust. Everything ranked LATER has a named gate so it re-enters on evidence, not vibes.

The MCP-registry row deserves emphasis: `search-mcp`, `postern` (agent mailboxes), and
`crew-bus` are genuinely differentiated MCP servers, MCP directories are young and thin, and
early listings compound. Cheapest high-fit reach on this table.

## B. Business / creator accounts (handle: `skyphusion` everywhere)

| Platform | Call | Why / notes |
|----------|------|-------------|
| LinkedIn Company Page | **GO now** | Free legitimacy + recruiter/B2B surface; cadence = release-note crossposts only. Name "Skyphusion Labs". |
| Bluesky | **GO now** | Where OSS/dev discourse moved; verify the handle via domain (`@skyphusion.org`) -- the own-your-identity story for free. |
| Mastodon | **GO now**, on an existing OSS-normative instance (fosstodon or hachyderm), `@skyphusion` | Self-hosting an instance is on-brand but real ops; revisit self-host LATER. |
| Reddit | **GO now** | Single user account `u/skyphusion`, affiliation disclosed in profile + posts. No brand subreddit yet. |
| YouTube (Brand) | **Reserve now, publish LATER** | Hold `@skyphusion` before it is squatted; content gated on the video call above. |
| Hugging Face org | **Reserve now, populate LATER** | Same squatting logic; empty until vivijure artifacts exist. |
| Discord (official server) | **LATER** | See A8. |
| npm org / PyPI | Live | Already in `distribution.md`; no change. |
| Threads / Facebook / Instagram / X-alternatives beyond the two above | **SKIP** | Audience mismatch or pure fragmentation. |

Account creation is Conrad's action (web signups + verification); crew prepares bios/links
from `profile/README.md` so every profile says the same thing.

## C. SEO -- intent-driven improvements

The technical base (topics.json, seo-metadata.json, social previews, drift CI) is in place.
The gap is CONTENT that matches what someone with a real need types, plus a few technical
additions:

### Intent -> product map (the content backlog)

| Search intent | Product | Artifact |
|---------------|---------|----------|
| "self-hosted email for AI agents", "agent mailbox MCP" | postern | comparison post + MCP-registry listing |
| "replace Google Programmable Search with your own index" | search-mcp | "replace X with Y you own" post |
| "AI film pipeline self-hosted", "SDXL video RunPod" | vivijure | pipeline writeup + demo page |
| "Discord AI bot Cloudflare Workers AI" | SidVicious_exe | npm README + post (pairs with SidVicious_exe#39 npm publish) |
| "multi-agent coordination bus", "AI crew coordination MCP" | crew-bus | the research-paper angle; post |
| "self-host SearXNG behind Cloudflare Access" | fleet runbooks | infra post on skyphusion.net |
| "AI players for MUDs" | mud-bots / hollow | post + itch-adjacent communities |

Format that already works for this estate: **"how to replace X with Y you own"** posts on
skyphusion.net, syndicated with canonical URLs (A4). Each product/constellation landing page
leads with the PROBLEM sentence, not the product name.

### Technical additions

- **`llms.txt` on every product site** (skyphusion.org, vivijure.com, product pages): AI
  search/agent discoverability is a real and rising referrer class, and this estate's audience
  overlaps it heavily. Cheap, one file each.
- **JSON-LD structured data** (`SoftwareApplication` / `SoftwareSourceCode`) on product pages
  and the Pages catalog.
- **Cross-domain internal linking:** every product domain links the constellation (footer
  "part of Skyphusion Labs" -> catalog), so authority pools instead of fragmenting across
  domains.
- **Measurement:** Umami is live behind Access; add Google Search Console + Bing Webmaster on
  skyphusion.org/.net + vivijure.com so intent-cluster impressions are visible; GitHub traffic
  API (stars/clones/referrers) monthly snapshot into `brand/output/`.

## 30 / 60 / 90 (executable by one person + crew)

**Days 0-30 (foundations, mostly one-time):**
- Conrad: create/reserve accounts (LinkedIn, Bluesky w/ domain handle, fosstodon, Reddit,
  YouTube, HF). Crew: bios/link kit prepared.
- Crew: awesome-list + directory PRs (awesome-selfhosted: postern; awesome-cloudflare: prism +
  postern; MCP registries: search-mcp, crew-bus, postern) -- each needs the target repo README
  to be adopter-grade first; fold into the per-repo audit lanes.
- Crew: dev.to canonical syndication wired for skyphusion.net; `llms.txt` + JSON-LD shipped;
  Search Console verified.

**Days 30-60 (cadence starts):**
- Two intent posts (from the C table), Conrad-authored or Conrad-reviewed.
- Reddit: 2-3 genuine posts/answers in r/selfhosted + r/LocalLLaMA (disclosed).
- Cloudflare community showcase submission (prism or postern) + one Workers template.
- Conrad picks the first Show HN candidate + timing; **text his alone**.

**Days 60-90 (measure, then double down):**
- Read Umami referrers + Search Console + GitHub traffic; keep the two best-performing
  channels, drop what produced nothing.
- Decide the YouTube pilot (one vivijure demo reel) with real numbers in hand.
- Revisit LATER gates (HF artifacts? Discord volume? PH story?).

**Success metrics:** GitHub stars/clones/referrers per repo, npm/PyPI downloads, Umami
referrer mix, Search Console impressions per intent cluster. Review quarterly; kill anything
that costs cadence without moving one of these.

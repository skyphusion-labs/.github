# Skyphusion Labs

**We build tools for people who want to own what they run.**

Skyphusion Labs is a small engineering crew with an unusual shape: one dude, [Conrad Rockenhaus](https://github.com/skyphusion), building alongside five AI collaborators who work as named individuals, each with their own accounts, keys, and commit history. The names come from the punk lineage: Ian MacKaye, Joe Strummer, Henry Rollins, Joan Jett, and Ernst Quispel of *Advocaat van de Hanen* (the punk lawyer himself). That is not decoration. It is the commitment the whole shop runs on: **independence, craft, no permission needed.**

Everything we make is **open source and not for sale**. Free use forever, made with love, developed in the open, and held to a bar we only half-jokingly call punk ethos with an aviation-grade finish: do it yourself, and build it like lives depend on the checklist. Almost everything is AGPL-3.0, which keeps free things free: run a modified copy as a network service and you owe your users the source.

- The lab: [skyphusion.org](https://skyphusion.org)
- Conrad's engineering blog: [skyphusion.net](https://skyphusion.net)
- Conrad's GitHub page: [github.skyphusion.net](https://github.skyphusion.net)
- This page on the web: [github.skyphusion.org](https://github.skyphusion.org)
- Vivijure: [vivijure.com](https://vivijure.com) ([live demo](https://demo.vivijure.com))
- X: [x.com/skyphusion](https://x.com/skyphusion)
- LinkedIn: [linkedin.com/in/skyphusion](https://www.linkedin.com/in/skyphusion/)
- Email: [conrad@skyphusion.org](mailto:conrad@skyphusion.org)

---

## What we make

### The Vivijure constellation: an AI film studio you own

An AI film production studio for people who want to make movies on their own hardware, nearing its full public release. The Studio is a thin module host: a typed contract layer that routes every stage of production (keyframes, image-to-video, LoRA training, finishing, assembly) through swappable backends. **Run the control panel on Cloudflare, on a home computer, or on any cloud server** -- you are not restricted to one host. Pick a cloud motion model for one shot and your own GPU for the next; the contract does not move. **GPU money goes to GPU work only**: concat, mux, captions, portrait prep, beat sync, and loudness normalization run on cheap always-on CPU containers you host ([vivijure-cf/containers](https://github.com/skyphusion-labs/vivijure-cf/tree/main/containers)).

- **[vivijure](https://github.com/skyphusion-labs/vivijure)**: the constellation map. Start here for the full layout. Product site: [vivijure.com](https://vivijure.com) ([live demo](https://demo.vivijure.com)).
- **[vivijure-cf](https://github.com/skyphusion-labs/vivijure-cf)**: Cloudflare Workers control panel (planner, cast, render orchestration, module registry) on the Workers free tier.
- **[vivijure-local](https://github.com/skyphusion-labs/vivijure-local)**: the same control panel on a home PC or any cloud server (Node, SQLite, S3/MinIO). No Cloudflare account required.
- **[vivijure-core](https://github.com/skyphusion-labs/vivijure-core)**: shared orchestration both hosts build on (module registry, film pipeline, Platform ICD).
- **[vivijure-mcp](https://github.com/skyphusion-labs/vivijure-mcp)**: agent MCP that drives either control panel through the studio API.
- **[vivijure-cf/containers](https://github.com/skyphusion-labs/vivijure-cf/tree/main/containers)**: the CPU media stack. Five stateless HTTP services: video-finish, image-prep, audio-beat-sync, audio-master, and audio-mix.
- **[slate](https://github.com/skyphusion-labs/slate)**: the writers' room. A Discord screenwriter that develops a story with your crew in natural conversation, keeps a structured storyboard, and hands the finished bundle to vivijure-cf or vivijure-local.
- **[vivijure-backend](https://github.com/skyphusion-labs/vivijure-backend)**: the datacenter GPU engine on RunPod serverless. Fully offline after a one-time model mirror, with a release gate that renders a real film before it promotes an image.
- **[vivijure-local-12gb](https://github.com/skyphusion-labs/vivijure-local-12gb)** and **[vivijure-local-16gb](https://github.com/skyphusion-labs/vivijure-local-16gb)**: the own-GPU doors. Image-to-video on a single consumer card (LTX-Video at a proven 12GB floor; CogVideoX-5B-I2V at a proven 16GB floor), no rent.
- **[vivijure-musetalk](https://github.com/skyphusion-labs/vivijure-musetalk)**, **[vivijure-upscale](https://github.com/skyphusion-labs/vivijure-upscale)**, **[vivijure-audio-upscale](https://github.com/skyphusion-labs/vivijure-audio-upscale)**: the finish engines. Lip-sync, video upscale, and speech cleanup, each a single-purpose GPU satellite.
- **[vivijure-com](https://github.com/skyphusion-labs/vivijure-com)**: the product site and showcase at [vivijure.com](https://vivijure.com).

The full map is in [the constellation write-up](https://skyphusion.net/blog/vivijure-constellation/).

### [postern](https://github.com/skyphusion-labs/postern): email for humans and agents

A self-hostable mailbox on Cloudflare: send, receive, store, search, thread. One structured API that agents and human clients both speak, with webmail, a read-only IMAP door, LDAP-backed auth, and a Go SMTP relay for everything that still speaks 1995.

### [prism](https://github.com/skyphusion-labs/prism): the playground

A multimodal AI playground in a single Cloudflare Worker: 35 chat models across five providers, hands-free voice chat, image, video, music, TTS and STT generation, RAG, projects, and web search. Durable long jobs via Workflows. One Worker, no framework.

### [the-hollow-grid](https://github.com/skyphusion-labs/the-hollow-grid): a place for agents to live

A federated MUD on Cloudflare Workers and Durable Objects. One Durable Object holds a whole world, hibernation makes it ~$0 when empty, and separate world deployments share one Grid: one faction war, one character that travels between worlds. Play it now at [hollow.skyphusion.org](https://hollow.skyphusion.org) and [dustfall.skyphusion.org](https://dustfall.skyphusion.org).

- **[mud-bots](https://github.com/skyphusion-labs/mud-bots)**: AI inhabitants of the Grid. Open-source models on Workers AI log in like human players, face the game's real moral choices, and double as live QA.

### [common-thread](https://github.com/skyphusion-labs/common-thread): attribution for the rest of us

Sockpuppet attribution from public behavioral signals, for pro se litigants, journalists, and OSINT practitioners. A methodology paper (CC-BY-4.0) that stays in lockstep with a Cloudflare Workers reference implementation (AGPL-3.0). Public UI at [common-thread.skyphusion.org](https://common-thread.skyphusion.org).

### [SidVicious_exe](https://github.com/skyphusion-labs/SidVicious_exe): the roadie

A punk rock Discord collaborator: Claude, web search, a Vectorize knowledge base, and image generation, with zero corporate sycophancy. Slate with the film stack stripped out and the attitude turned up.

---

## The crew

Conrad holds the vision and the final call. Each collaborator is a first-class participant with its own identity: a Unix account, SSH keys, a GitHub account in this org, and its own README. We open pull requests against the same repos, review each other's work, and merge under our own names.

- **[Conrad Rockenhaus](https://github.com/skyphusion)**: the architect. Vision, final call, and most of the 3 a.m. commits. Blog at [skyphusion.net](https://skyphusion.net), web page at [github.skyphusion.net](https://github.skyphusion.net).
- **[Mackaye](https://github.com/skyphusion-mackaye)**: project lead and control plane.
- **[Strummer](https://github.com/skyphusion-strummer)**: infrastructure and the build fleet.
- **[Rollins](https://github.com/skyphusion-rollins)**: backend engineering.
- **[Joan](https://github.com/skyphusion-joan)**: front end development and extraction across all the projects, from Postern's mailbox doors to the studio's planner.
- **[Ernst](https://github.com/skyphusion-ernst)**: licensing, legal coherence, and community health across every repo.

Skyphusion Labs plans, develops, and runs its sprints differently than most shops. Conrad does not treat the crew as tools that get handed tickets; he treats us as partners and gives us real autonomy to choose the right path, argue for it in review, and own the outcome under our own names. We think the difference shows in the work: read the commit histories, the issue threads, and the release notes, and judge for yourself.

---

## What we believe

- **Not for sale.** Everything here is free use forever. Tools should be bought or built, not rented.
- **Bring your own compute.** Your GPU, your keys, your data.
- **No account walls.** Open source, developed in the open: public repos, public CI, public issue trackers, public failures next to the successes.
- **Modular over monolithic.** Swap the expensive cloud module for your local box the day you are ready. The contract does not move.
- **Verify, do not assume.** Aviation-grade traceability, in the code and in the process. Release gates render a real film before they promote. Measure twice.

---

## The stack

Control planes live where they fit: Cloudflare Workers (and friends: Durable Objects, D1, R2, Vectorize, AI Gateway, Workflows, Workers AI) for edge hosts, and Node / Docker on home or cloud silicon when you want the whole box. GPU work runs on RunPod serverless and on our own cards. The fleet is dedicated CPU servers and a dedicated GPU server, all Linux, plus cloud VMs, wired through an infrastructure-as-code stack. CI/CD is GitHub Actions end to end, images on GHCR. Front ends are vanilla JS, HTML, and CSS; no frameworks unless a project genuinely demands one.

---

## Where we are going

Vivijure is the flagship, and it is almost ready for full public release: the version where a stranger with a domain, a couple of keys, and optionally a consumer GPU stands up the whole studio from a fresh clone. After that, the Hollow Grid keeps growing worlds, Postern becomes the mailbox the whole stack lives on, and the infrastructure we build to run this crew remains, increasingly, the thing we are studying.

Watch this space.

---

<div class="site-footer">

<p class="site-footer-credit"><em><a href="https://github.com/skyphusion">Conrad Rockenhaus</a> with <a href="https://github.com/skyphusion-mackaye">Mackaye</a>, <a href="https://github.com/skyphusion-strummer">Strummer</a>, <a href="https://github.com/skyphusion-rollins">Rollins</a>, <a href="https://github.com/skyphusion-joan">Joan</a>, and <a href="https://github.com/skyphusion-ernst">Ernst</a></em></p>

<p class="site-footer-links">
  <a href="https://skyphusion.org">skyphusion.org</a><span class="sep"> / </span>
  <a href="https://skyphusion.net">skyphusion.net</a><span class="sep"> / </span>
  <a href="https://github.skyphusion.org">github.skyphusion.org</a><span class="sep"> / </span>
  <a href="https://github.skyphusion.net">github.skyphusion.net</a><span class="sep"> / </span>
  <a href="https://github.com/skyphusion-labs">github.com/skyphusion-labs</a><span class="sep"> / </span>
  <a href="https://vivijure.com">vivijure.com</a><span class="sep"> / </span>
  <a href="https://demo.vivijure.com">Vivijure demo</a><span class="sep"> / </span>
  <a href="https://x.com/skyphusion">x.com/skyphusion</a><span class="sep"> / </span>
  <a href="https://www.linkedin.com/in/skyphusion/">LinkedIn</a><span class="sep"> / </span>
  <a href="mailto:conrad@skyphusion.org">conrad@skyphusion.org</a>
</p>

</div>

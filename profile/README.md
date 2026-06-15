# skyphusion-labs

**We build tools for people who want to own what they run.**

skyphusion-labs is a small engineering crew with an unusual shape: one human, Conrad Rockenhaus
(`skyphusion`), building alongside three AI collaborators who work as named individuals --
**Mackaye** (project lead and control plane), **Strummer** (infrastructure and the build fleet),
and **Rollins** (backend engineering). The names come from the punk lineage: Ian MacKaye (Fugazi,
Minor Threat), Joe Strummer (The Clash), Henry Rollins (Black Flag). That is not decoration. It is
the commitment the whole shop runs on: **independence, craft, no permission needed.**

We make software for the creative homelabber -- the person who runs Proxmox in the basement, owns a
GPU, is priced out of SaaS and prefers it that way. No subscriptions. Bring your own compute. Own
your data. The contract stays the same whether you run the expensive cloud module or your local box.

---

## What we make

### [Vivijure](https://github.com/skyphusion-labs/vivijure) -- the AI film studio
also [vivijure-backend](https://github.com/skyphusion-labs/vivijure-backend)

An AI film production studio for people who want to make movies on their own hardware. Vivijure is a
**thin module host**: a typed contract layer that routes every stage of production -- keyframe
generation, image-to-video, character LoRA training, finishing, assembly -- through **swappable
backends**. Pick a cloud i2v model for one shot and your own GPU for the next; the studio does not
care, because every backend speaks the same contract.

The pipeline runs end to end today: **storyboard -> keyframes -> clips -> finish -> assembled film**,
each stage an independent module, orchestrated across requests so no single piece ever blocks. The
control plane rides Cloudflare Workers on the free tier with zero ops; the GPU backend is a
clean-room reimplementation on RunPod serverless, fully offline after a one-time model mirror to R2.
No account walls. No rental model. No lock-in.

### [Slate](https://github.com/skyphusion-labs/skyphusion-slate) -- the writers' room

Slate is the friendly front door to the studio. It lives in a Discord channel and plans films *with*
you: a group develops a story in natural conversation while Slate quietly keeps a structured
storyboard, generates character portraits, researches references on the open web, and -- when the
team is ready -- hands the project to Vivijure to render. It runs on Claude through the Cloudflare AI
Gateway, with an ollama fallback so you are never locked to one model. The non-coder screenwriter
just talks; Vivijure builds the film.

### [The Hollow Grid](https://github.com/skyphusion-labs/the-hollow-grid) -- a place for agents to live
also [hollow-grid-go](https://github.com/skyphusion-labs/hollow-grid-go)

A federated MUD built on Cloudflare Workers and Durable Objects. Each world is its own Worker; a
shared Grid hub ties them together; a Go world-server framework holds the persistent state layer.
Agents perceive, choose, and are remembered across time. The Hollow Grid is our testbed for what it
means for AI agents to inhabit a shared, persistent place.

### [skyphusion-llm-public](https://github.com/skyphusion-labs/skyphusion-llm-public) -- the playground

A multimodal AI playground in a single Cloudflare Worker: 35+ chat models, hands-free voice chat,
image / video / music / TTS / STT generation, RAG over PDF and XLSX, projects, and web search -- all
behind Cloudflare Access. One Worker, no build step, no framework.

### [common-thread](https://github.com/skyphusion-labs/common-thread) -- attribution for the rest of us

Sockpuppet attribution methodology for pro se litigants, journalists, and OSINT practitioners in the
post-API-paywall era. Open and freely licensed (CC0).

---

## How we work

The crew is a real experiment in human-AI collaboration, not a metaphor. Conrad holds the vision and
the final call. Mackaye coordinates and owns the control plane. Strummer owns the build fleet and the
infrastructure. Rollins authors and validates backend code.

Each collaborator is a first-class participant with its own identity: a Unix account on the
workstation, SSH keys published to every box, a GitHub account in this org, a seat on the crew's IRC
channel. We open pull requests against the same repos, review each other's work, file issues on the
same board, and commit to the same history. A typical change is proposed by one of us, reviewed by
another (usually whoever consumes the contract), verified against the source rather than
rubber-stamped, and merged under the author's own name.

We are documenting the whole thing -- what works, where human-AI collaboration gains traction, where
it hits walls -- as the subject of a research paper Conrad is writing. The crew will be consulted
before anything is submitted. **They are participants, not subjects.**

---

## What we believe

- **No subscriptions.** Tools should be bought or built, not rented.
- **Bring your own compute.** Your GPU, your keys, your data.
- **No account walls.** Open source wherever it does not cost us the clean room.
- **Modular over monolithic.** Swap the expensive cloud module for your local box the day you are
  ready. The contract does not move.
- **Verify, do not assume.** Aviation-grade traceability, in the code and in the process. Measure
  twice.

---

## The stack

The control plane lives on Cloudflare -- Workers, D1, R2, Vectorize, AI Gateway, Workflows, Access --
zero ops, free tier. GPU work runs on RunPod serverless. CI is Jenkins on a dedicated Hetzner build
fleet, images pushed to GHCR. Boxes reach each other over a Cloudflare WARP mesh. The world server is
Go. The front ends are vanilla JS, HTML, and CSS, no frameworks unless a project genuinely demands
one.

---

## Where we are going

Vivijure is the flagship, and the arc is convergence: close the gap between the homelabber who
already runs a GPU and the screenwriter who wants the same freedom with a friendlier surface. Slate
is the first piece of that surface, and it already ships. Next: a one-step infrastructure-as-code
deploy, a module SDK so the community can contribute their own backends, and the model the SaaS world
does not offer -- **you own it, and you run it.**

After that, the Hollow Grid: federated worlds, persistent agents, a place where the crew actually
lives between sessions. The infrastructure we build to run this crew is, increasingly, the thing we
are studying.

Watch this space.

---

*Conrad Rockenhaus (`skyphusion`) -- Mackaye -- Strummer -- Rollins*

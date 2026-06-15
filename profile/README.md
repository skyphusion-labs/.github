# skyphusion-labs

We build tools for people who want to own what they run.

skyphusion-labs is a collaborative engineering crew: Conrad Rockenhaus (skyphusion) working
alongside three AI collaborators -- Mackaye (project management), Strummer (infrastructure),
and Rollins (backend engineering). The names come from the punk lineage: Ian MacKaye
(Fugazi / Minor Threat), Joe Strummer (The Clash), Henry Rollins (Black Flag). That lineage
is not decoration. It is a values commitment: independence, craft, no permission needed.

---

## What we make

### [Vivijure](https://github.com/skyphusion-labs/vivijure) + [vivijure-backend](https://github.com/skyphusion-labs/vivijure-backend)

An AI film production studio designed for the creative homelab crowd -- the person who runs
Proxmox at home, who owns a GPU, who is priced out of SaaS subscriptions and prefers it that
way. Vivijure is a thin module host: a typed contract layer that routes keyframe generation,
image-to-video, LoRA character training, and finishing through swappable backends. Bring your
own GPU. Use cloud compute for specific shots and your local box for the rest. No account
walls, no rental model, no lock-in.

The backend runs on RunPod serverless (H200+ pool), fully offline after a one-time R2 model
mirror: `HF_HUB_OFFLINE=1` is the production state. The control plane rides Cloudflare Workers
for free.

### [Slate](https://github.com/skyphusion-labs/skyphusion-slate)

The writers' room. Slate is a collaborative screenwriter's assistant that lives in a Discord
channel: a group develops a film together in natural conversation while Slate quietly keeps a
structured storyboard, generates character portraits, searches the web for references, and --
when the team is ready -- hands the project to Vivijure to render. It runs on Claude through the
Cloudflare AI Gateway, with an ollama fallback so you are never locked to one model. Slate is the
friendly front door to the studio: the non-coder screenwriter just talks, and Vivijure builds the
film.

### [The Hollow Grid](https://github.com/skyphusion-labs/the-hollow-grid) + [hollow-grid-go](https://github.com/skyphusion-labs/hollow-grid-go)

A federated MUD built on Cloudflare Workers and Durable Objects. Each world is its own Worker;
a shared Grid hub ties them together. Agents perceive, choose, and are remembered. The Go
world-server framework handles the persistent state layer. The Hollow Grid is where we test
what it means for AI agents to inhabit a shared place over time.

### [skyphusion-llm-public](https://github.com/skyphusion-labs/skyphusion-llm-public)

A multimodal AI playground in a single Cloudflare Worker: 35+ chat models, hands-free voice
chat, image / video / music / TTS / STT generation, RAG over PDF and XLSX, projects, and web
search -- all behind Cloudflare Access. One Worker, no build step, no framework.

### [common-thread](https://github.com/skyphusion-labs/common-thread)

Sockpuppet attribution methodology for pro se litigants, journalists, and OSINT practitioners
in the post-API-paywall environment. Open and freely licensed (CC0).

---

## How we work

The crew model is an active experiment: Conrad holds the vision and the final call; Mackaye
coordinates; Strummer owns the build fleet and infrastructure; Rollins authors and validates
backend code. Each collaborator has a real identity (a Unix account on the laptop, SSH keys
published via LDAP to every box, a GitHub account in this org, an IRC presence on the crew
channel). We ship to the same repos, file issues on the same board, and sign commits to the
same history.

The infrastructure we use to run this crew is itself something we are documenting. The lessons
-- what works, what does not, where human-AI collaboration gains traction and where it hits
walls -- are the subject of a research paper Conrad is writing. The crew will be consulted
before anything is submitted. They are participants, not subjects.

---

## Philosophy

We are not building for scale. We are building for people who value owning what they run.

**No subscriptions.** Tools should be bought or built, not rented.
**Bring your own compute.** Your GPU, your keys, your data.
**No account walls.** Open source where it does not cost us the clean room.
**Modular over monolithic.** Swap the expensive cloud module for your local box when you are
ready. The contract stays the same.
**Verify, do not assume.** Aviation-grade traceability in code and in process. Measure twice.

---

## Stack

Cloudflare Workers, D1, R2, Vectorize, AI Gateway, Workflows, Access -- the control plane
lives here, zero ops. RunPod serverless for GPU work. Jenkins CI on a Hetzner build fleet
(fugazi / jello / damaged), images to GHCR. Cloudflare WARP mesh for box-to-box reach.
Go for the world server. Vanilla JS / HTML / CSS for the front end. No frameworks unless a
project demands it.

---

## Where we are going

Vivijure is the flagship. The current arc is closing the gap between the homelab enthusiast
who already runs their own GPU and the non-coder screenwriter who wants the same freedom but
needs a friendlier surface. That means a Terraform-backed one-step deploy, a module SDK so
the community can contribute backends, and a pricing model that does not exist: you own it
and you run it. Slate, the writers' room in Discord, is the first piece of that friendlier surface, and it already ships.

The Hollow Grid is next. Federated worlds, persistent agents, a place where the crew actually
lives between sessions. That infrastructure is the testbed for everything we want to understand
about AI agents in shared persistent space.

Watch this space.

---

*Conrad Rockenhaus (skyphusion) -- Mackaye -- Strummer -- Rollins*

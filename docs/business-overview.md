# Delta One — Business Overview

*Compiled 16 August 2026 from the `delta-dev` repository (git history, DevLog.txt, canonical docs, live templates, content files, local DB) and the adjacent planning documents referenced by the repo's own handoff pack.*

**Status of this document:** descriptive, not aspirational. Where the repo contradicts itself, both sides are recorded and the conflict is flagged rather than resolved silently.

---

## 1. Executive summary

Delta One is a curriculum-first market education product for people who want to genuinely understand how markets work, built by a two-person founding team — Bhanu Sugguna (founder; product, engineering, curriculum) and Jacob Blais (co-founder, head of marketing) — with Bhanu himself inside the target user experience. The public product at launch is **Delta Core** — a structured, gated learning path of roughly 97 lessons, activities and checks delivered through a terminal-styled web workspace. A momentum-signal trading bot (**Delta Pro**) exists as separate private infrastructure and is deliberately parked.

The project began life as a bot/signal platform with education attached. In late June 2026 it pivoted hard: the bot was stripped out of the platform repo entirely, AI was demoted from headline feature to optional support layer, and the docs were rewritten around a single principle — *"Curriculum is the product. Everything else supports it."*

Target launch is **1 January 2027 — free tier only**, and the founder treats that date as a hard commitment. Monetization is deliberately staged behind it: Pro roughly a month later, then one new feature per month on a consistent rollout cadence.

The honest current position: the **delivery system is genuinely good and the content is genuinely not there yet.** Module 0 is deep, interactive, and well-built. The other ~88 curriculum items exist as ~110-word skeletons. Five pull requests containing essentially all of the good engineering work are open and unmerged. The full-curriculum writing sprint was planned in detail on 27 July and paused before a single word was written — and nothing has been committed in the 20 days since. Meanwhile the live public landing page still markets an algo trading engine and backtest statistics that the product direction explicitly abandoned.

---

## 2. What Delta One is

### The product promise

> "We help you understand how markets move, how price behaves, and how to think more clearly about what you are seeing."
> — `docs/product-vision.md`

Explicitly *not* "we tell you what to trade."

The learner should finish "smarter, more structurally aware, and better able to explain what price is doing."

### The two named products

| | **Delta Core** | **Delta Pro** |
|---|---|---|
| What | Structured curriculum, activities, progress tracking, learning workspace | Momentum-signal algo trading engine + explainability layer |
| Status | The launch product. Actively built. | Parked. Migrated out to a separate `delta-bot` repo, on hold since 29 June 2026 |
| Pricing | Free, permanently | $20/month (page copy) — no payment system exists |

The reasoning behind parking Delta Pro is recorded plainly: it "needs proper dedicated development time to actually *think like a real trader*, and launching it half-ready would undercut trust in everything else."

### What Delta One is deliberately not

From `docs/product-vision.md`, these framings are rejected because they "create the wrong expectations and pull the build in the wrong direction":

- a public signal platform
- a live bot dashboard product
- an AI-first assistant
- a get-rich-quick tool

The repo's disclaimer language reinforces this: education platform, historical backtests don't guarantee future performance, no financial advice.

---

## 3. Who it's for

### The stated audience

Absolute beginners. The contributor guide's framing is the sharpest definition in the repo:

> "The learner coming in has never opened a brokerage account. They have heard the word 'stock' but it means nothing concrete to them yet."

Tone standard: *"Plain English. If a 16-year-old can't follow it, rewrite it."*

### The segment question — still open

The Phase 0 problem statement (16 July 2026) is candid that the paying audience is unvalidated. Two segments were being tested in parallel:

- **Students** — curious, time-rich, capital-poor, low urgency. Investing feels abstract. Reached via campus distribution.
- **Working professionals / knowledge workers** — income and real motivation ("they want to grow money they're now earning"), time-poor, and often quietly embarrassed not to know this already. Reached via online communities.

The open question, verbatim: *"which of these two groups feels this pain deeply enough to pay to solve it — and whether it's one, the other, or both in different ways (e.g. students as the entry funnel, professionals as the paying core)."*

Note the tension: the **live landing page** commits to one answer already — *"built for college students who are tired of market noise"* — while the internal doc treats it as unresolved.

---

## 4. Why it exists — the problem

The information available to someone trying to understand investing is either **too shallow** (social-media tips content) or **too dense** (textbooks, courses and financial media written for people who already speak the language). Very little walks someone through *why* things work rather than *what* to do.

The differentiation hypothesis has three parts:

1. **Structured and sequenced**, not a firehose — hard-gated modules where each one must be earned before the next unlocks.
2. **Respects time** — 400–550 word lessons, a 3–4 minute read each.
3. **Built from inside the problem** — "built by someone actually inside the target-user experience (a student navigating this himself), not a finance institution talking down."

A fourth differentiator emerged from the contributor guide and is arguably the most defensible one: **the example discipline**.

> "Never introduce a company and a concept at the same time. Only one thing should be new."

Concepts are anchored to brands the learner already has a relationship with — Starbucks, Nike, Apple, Uniqlo, McDonald's, eBay/StockX, Netflix — and the example is written *before* the term is named. The guide includes a full concept-to-brand mapping table and a worked wrong/right example. This is a real pedagogical asset, not boilerplate.

---

## 5. The curriculum — the actual product

`docs/curriculum.txt` (v3, 28 June 2026) is the source of truth. Two layers:

**FOUNDATION — Modules 0–5. Hard gated.** Every module must be completed before the next unlocks.

| Module | Title | Items |
|---|---|---|
| 0 | What is the Market? | 10 |
| 1 | Reading the Market | 9 |
| 2 | How Big Money Moves | 11 |
| 3 | How Price Really Behaves | 9 |
| 4 | Pattern Box | 9 |
| 5 | Reading a Setup (foundation capstone) | 9 |

**THE FORK — Module 6, "Choose Your Path"** (8 items). Soft gated. The learner declares a path via written reflection, not a quiz. Contributor instruction: *"6.1 must be completely neutral. Do not imply that day trading is more sophisticated or that ETF investing is boring."*

**OPEN LAYER — Stages.** Unlocked after Module 6.

- **Stage A** — ETF & long-term investing (~8 items)
- **Stage B** — Swing trading (~8 items)
- **Stage C** — Intraday / day trading (~8 items)
- **Stage R** — Resources: forex, futures, options, crypto, tools, books, glossary (8 reference items, no activities, unlocked for everyone)

**Total: ~97 items.** Everything free at launch.

### Content pattern

`Lesson → Activity → Lesson → Activity → … → Check`

Each activity builds on the *output* of the previous activity — the learner annotates one chart progressively across a module. Each module ends with a **Check**: what you should be able to do now, quick questions requiring genuine thought, one real-chart task, and an honest self-assessment ("if you can't do X without looking it up, go back to lesson Y"). Checks are self-reported at launch; AI-graded feedback is a post-launch Pro idea.

Module 5's check is marked a **"COMPLETION MOMENT"** the UX must explicitly acknowledge before opening the fork.

---

## 6. Business model

| Tier | Price | Contents | Reality |
|---|---|---|---|
| Core | Free forever | Full curriculum | This is what exists |
| Pro | $20/mo (page), $10–20 "to be validated" (internal) | Enhanced AI-guided learning, deeper case studies; algo bot *only when genuinely ready* | No Stripe, no checkout, no webhooks, no subscription tracking. `tier` is a string column on `users` with a `tier_required` decorator and a badge in the UI |
| Max | — | Broader coverage, intraday signals, extended history | Concept only |

### Rollout sequence (confirmed August 2026)

Willingness to pay has not been demonstrated, and the founding team's answer is to stop trying to prove it up front and earn it in public instead:

1. **1 January 2027 — free tier only.** The hard commitment. No payment system required to launch.
2. **~February 2027 — Pro introduced.**
3. **Monthly thereafter — one new feature per month**, on a visible, consistent cadence.

Two consequences worth stating plainly. First, **Stripe drops off the launch critical path** — the absence of a payment system is now a deliberate sequencing choice, not a gap. Second, the monthly cadence is a marketing promise as much as a product one, and it only holds if there is a queue of shippable features behind it. No such queue is currently written down.

The price point remains unvalidated ($20/mo on the pricing page, $10–20 internally). Monetization is deliberately *not* centered on the bot.

**Current commercial traction: 2 verified waitlist signups.** (Four rows existed; two were test entries and were deleted on 29 June.) A founding-user conversion plan is designed — one-time script generates credentials, single transactional email, no forced reset — but requires an email sender that hasn't been set up.

---

## 7. Company, legal and operations

*Sourced directly from the founder, August 2026. Items marked ⚠ remain open.*

### Entity and ownership

No registered entity. Delta One is currently **Bhanu Sugguna personally** — a sole trader in practice. No incorporation is planned at this stage.

**Licensing — resolved 16 August 2026.** The repository was MIT-licensed, which would have let anyone take the code *and the curriculum content* and sell it. `LICENSE` has been replaced with a proprietary all-rights-reserved notice covering code, `content/` and `docs/`, plus a contribution-assignment clause so future contributors' lessons belong to Delta One rather than to whoever wrote them.

The timing was clean and worth understanding: because the repo has been private since inception, the MIT grant never actually reached a third party, so there was nothing to revoke. That window closes the moment the repo goes public or an outside contributor commits — which is exactly what the contributor guide is designed to cause.

### Team

| Person | Role | Scope |
|---|---|---|
| Bhanu Sugguna | Founder | Product, engineering, curriculum, all approvals |
| Jacob Blais | Co-founder, Head of Marketing *(working title)* | Marketing |

No other people are involved in any capacity. The "contributors" addressed throughout `docs/contributor-guide.md` are a **future audience, not existing people** — the guide is a recruiting and standards asset written ahead of the team it describes.

**Equity: 65% Bhanu / 35% Jacob**, agreed August 2026.

⚠ Two things make that number currently unenforceable as written. First, **there is no entity to hold shares in** — you cannot issue equity in a sole trader, so until Delta One is incorporated the split is an intention rather than a grant. Second, **there is no vesting**: as agreed, Jacob holds 35% from day one regardless of how long he stays. The standard structure is four years with a one-year cliff, and it protects both sides — it is as much a guarantee to Jacob that his stake can't be diluted away as it is protection for Bhanu if he leaves in month three.

The cheap fix, in this order: a short written founder agreement now that records the 65/35 split, vesting terms, and what happens on departure, expressed as a commitment binding on a future entity — then convert it into actual shares at incorporation. This is a one-page document and a conversation that only gets harder to have later.

⚠ Approval authority is undocumented. In practice, all product and content sign-off sits with Bhanu.

### Finance

- **Current run cost: effectively zero.** Everything is on free tiers — Cloudflare Pages, Render, Supabase, Groq.
- Self-funded by Bhanu. No outside money, grants, or funding.
- **Budget ceiling ~$5,000**, adjustable with justification.
- There is explicit room in that budget to **pay a curriculum writer**.

That last point matters more than its placement suggests. There are 88 items on the launch critical path, a founder leaving on 24 August and starting university after that, and an unused budget line for exactly the kind of help that would close the gap.

### Regulatory position

The founder's position, recorded as stated and **not professionally verified**:

> Teaching trading methodology — market structure, liquidity, entries, stops, targets — is common knowledge and legal to teach. These are skills a competent trader needs. The line is crossed by specific recommendations: *"invest in Nvidia, invest in this new and upcoming aerospace company."* Delta One does not and will not do that.

This is coherent with how the product is actually written. `docs/contributor-guide.md` bans advice language outright — *"You should buy" is never acceptable. "This is how it works" always is* — so the curriculum's own editorial rules already enforce the line the founder is drawing. The exposure is not the curriculum; it is anything that ships alongside it. **Delta Pro's live signals are the obvious future pressure point**, and the distinction between "here is a signal our engine generated" and "buy this" is thinner than the distinction the curriculum maintains. Worth resolving before Pro returns, not after.

⚠ No Terms of Service exists and one needs writing. No privacy policy is noted. Neither has had legal review.

### Age policy

Open to all ages, with an informal floor around 15. ⚠ This interacts directly with the missing TOS: the product creates accounts and collects email addresses, which brings any under-13 user into COPPA (US) and GDPR children's-data (UK/EU) scope. The cheap fix is a stated minimum age in the TOS and at signup, not an age-verification system.

### AI policy — confirmed, and it constrains the build

This is the most operationally significant answer in this section, because 88 curriculum items are planned to be AI-written.

| | |
|---|---|
| **Permitted** | AI does the writing, the formatting, and the compilation |
| **Required** | AI works only from sources the founder has pulled and pre-approved — Bhanu controls what it reads |
| **Hard red line** | AI must never write from its own knowledge. If it can't find something in the approved sources, a human supplies a URL that covers it |
| **Review** | Every item is human-read for usability, readability and user fit before it goes live |
| **Disclosure to learners** | Not planned |

The consequence is a prerequisite nobody has scheduled. **A pre-approved source library covering Modules 1–6 and Stages A/B/C/R must exist before the content sprint can legitimately begin.** The 27 July plan assumed writing could start as soon as the loader was fixed; under this policy, it cannot. That is a real, unbudgeted task sitting on the critical path.

It is also, usefully, one of the few tasks here that is separable from editorial control — curating and approving sources is not the same job as writing, so it can go to Jacob or to a paid contractor without Bhanu giving up the thing he wants to keep.

### Access

GitHub, Render, Cloudflare and Supabase are all **private, with Bhanu as the only account holder.** No shared credentials, no third-party access.

⚠ The flip side is a **bus factor of one on every system the product runs on.** If Bhanu loses access to an account — lost device, lost 2FA, locked email — there is no second person and no documented recovery path. The proportionate fix at this stage is not an access-management process; it is storing 2FA recovery codes and account recovery details somewhere durable and separate from the laptop.

### Still open ⚠

Analytics/tracking in use · where production secrets are stored (Render env vars vs. a local `.env`) · branch protection and rollback procedure · domain ownership and whether `hello@deltaone.app` is a live inbox.

---

## 8. Technical architecture

| Layer | Choice |
|---|---|
| Backend | Flask (app-factory pattern, 6 blueprints: public, auth, api, workspace, admin, onboarding) |
| Database | PostgreSQL / Supabase in production; SQLite for local dev |
| ORM / migrations | SQLAlchemy + Flask-Migrate (Alembic), 4 migrations |
| Auth | Flask-Login + Flask-WTF |
| Frontend | Jinja2 + vanilla JS/CSS — no framework |
| AI | Groq (`llama3-70b`), rate-limited by tier, every call logged |
| Hosting | Cloudflare Pages (static waitlist) + Render (Flask app, still dev server) |
| Content | Markdown files in `content/`, loaded into DB by `seeds/load_content.py` |

**Models (7):** User, Module, Lesson, UserProgress, Session, WaitlistEntry, AiInteraction.

**Design language:** near-black `#0a0b0c`, green accent `#4ade80`, JetBrains Mono, 0px border radius — a deliberate Linux-terminal aesthetic applied consistently across marketing, workspace and admin.

**Infrastructure state (audited 29 June, unchanged since):** Cloudflare Pages running; Render running on the Flask dev server; Supabase project `DeltaOne-Waitlist` (us-east-1) contains exactly one table, `public.waitlist`. **The platform schema does not exist in Supabase and production `DATABASE_URL` is not pointed at it.**

---

## 9. What has been built

### Solid and working

- **Full app skeleton** — factory, config, 6 blueprints, 7 models, 4 services, admin panel, error pages. Boots clean; 18 smoke tests pass.
- **Auth** — signup/login/logout, password hashing, email normalization, session kill on logout, login timestamps.
- **Security hardening pass** — all API endpoints require auth; production refuses to boot without `SECRET_KEY`; UUID validation on admin routes; open-redirect protection on `?next=`; UTC standardization.
- **Admin panel** — usage dashboard, user management with tier changes, system overview, per-module curriculum completion stats.
- **Onboarding quiz** — 10 scenario-based, curriculum-aligned questions across 5 topic areas with a topic-breakdown result page.
- **Groq AI assistant** — real LLM, tier-based rate limits, every interaction logged, graceful degradation if the key is missing.
- **Markdown → DB content pipeline** (`seeds/load_content.py`) — parses filenames to derive ordering and lesson-vs-activity type, converts to HTML, links activities to their parent lesson, and re-syncs on re-run so editing a `.md` updates what the app serves.
- **Lesson delivery spine** — full typography system, module browser, lesson header/footer nav, dashboard with focus bar and progress bars, reading-progress indicator, keyboard navigation (←/k, →/j), mark-complete animation.
- **Guided "tour guide" mode** — splits each lesson at its `<h2>` boundaries into one-screen steps with dot navigation and a counter; section headings type out like a guide introducing the next stop; skippable; respects `prefers-reduced-motion`; Guided ⇄ Read toggle persisted per user.
- **Interactive block library** — an authoring shortcode syntax written directly into markdown that expands to live widgets: `[[stat]]` (animated count-up, auto-colored green/red by direction), `[[reveal]]` (tap-to-reveal), `[[quiz]]` (inline multiple choice with instant feedback), `[[calc]]` (live ownership-percentage calculator). Hydrates in both guided and read views.
- **Module 0 content** — 9 items, ~4,700 words, ~520 words each across 4 guided steps, with interactive blocks wired into real teaching moments.
- **Local dev path** — runs entirely on SQLite with no Postgres or Supabase needed; three seeded test logins via a `flask seed-users` CLI command.

### The 5-PR stack — built, open, unmerged

```
fix/app-boot (#1) → feat/run-module-0 (#2) → feat/lesson-experience (#3)
  → feat/guided-lessons (#4) → feat/lesson-blocks (#5)
```

Essentially every item in the "solid and working" list above from the content pipeline downward lives in this stack. **None of it is merged to `main`.** It is stacked in dependency order, so nothing lands until review starts at #1.

---

## 10. What needs work

### Critical path

1. **The curriculum is 9% written.** Module 0 averages ~520 words per item. Every other folder averages ~110 words — one sentence per section, the exact "2–3 lines" thinness that was already identified and fixed for Module 0. This is the single biggest gap between the product as described and the product as it exists.

   | Folder | Files | Words | Per item |
   |---|---|---|---|
   | module-0 | 9 | 4,697 | ~522 ✅ |
   | module-1 | 9 | 1,044 | ~116 ⚠️ |
   | module-2 | 11 | 1,277 | ~116 ⚠️ |
   | module-3 | 9 | 1,022 | ~114 ⚠️ |
   | module-4 | 9 | 1,006 | ~112 ⚠️ |
   | module-5 | 9 | 1,004 | ~112 ⚠️ |
   | module-6 | 8 | 889 | ~111 ⚠️ |
   | stage-a/b/c/r | 32 | 3,941 | ~123 ⚠️ |

   **88 items to write.** `0-check.md` doesn't exist — Module 0 has no capstone.

   Under the confirmed AI policy (§7), this work has an unscheduled prerequisite: **a pre-approved source library for every remaining module and stage**, because AI is not permitted to write from its own knowledge. That library does not exist and is not on any plan.

2. **Merge the 5-PR stack.** All the good work is sitting on branches. Risk compounds daily.

3. **The content loader can't parse most of the files that need writing.** `parse_filename()` only matches the numeric `X.Y[-A]-slug.md` pattern. It cannot parse module checks (`1-check.md`), letter-stage lessons (`A.1-slug.md`), or stage checks (`A-check.md`). There is no `item_type="check"`, and only `module-0` is registered in the `MODULES` table. Writing 88 files against this loader means most of them silently never load. **This was correctly identified as needing to be fixed first, and the fix has not been started.**

4. **Nothing is production-ready.** From the pre-launch checklist, all still open: run migrations against Supabase, drop the orphaned `bot_events` table, point Render's `DATABASE_URL` at Supabase, seed curriculum, set up a transactional email sender, run the founding-user migration, and smoke test prod end to end. The app still runs on the Flask dev server.

### Also outstanding

- **No payments** — Stripe products, checkout, webhooks and real tier gating logic all unbuilt. **This is no longer a launch blocker**: the January launch is free-tier only by design, and Pro follows about a month later. It becomes critical in roughly February 2027.
- **Test coverage is one smoke file** (18 tests). No unit tests for services, models, or the content pipeline.
- **The fifth block type** — an annotated interactive diagram (order book, buyers/sellers matching) — was described as the most literal expression of the "tour guide explains each item" vision. Never built.
- **`Claude Files/Company.md`** was an unanswered questionnaire; it has now been filled in from the founder (see §7). What remains open there is narrower: analytics, secrets handling, access lists, branch protection and rollback, domain ownership, and two decisions — the MIT licence and the product name.
- **No Terms of Service.** Required before launch, and the age policy depends on it.

### Contradictions that need a decision

- **The live landing page contradicts the product strategy.** It leads with *"Structured learning on top. An algo trading engine underneath,"* presents three backtest stats as headline social proof (208 trades, 49% win rate, 1.37× profit factor), and dedicates half the feature grid to "Delta Pro — Algo Engine" with live signals and portfolio tracking. The strategy docs say the bot is not the promise; the July build spec says don't reference Delta Pro at all. Anyone arriving from the LinkedIn or Instagram profile sees the abandoned positioning.
- **The Delta Core feature list on that page also promises things that don't exist** — simulations on real historical data, macro and news context wired to learning state, integrated notes.
- **Doc drift.** `docs/technical-spec.md` still cites a "42-item structure" (curriculum v2) against curriculum v3's ~97, still lists only `module-0` through `module-4`, and still says bot code lives in the repo as `sweep_*.py` — it doesn't. `curriculum.txt`'s header says "8 Modules" but enumerates seven (0–6).
- **The July 20 MVP build spec was never implemented.** It specified splitting the repo into `mvp/` and `dev/`, moving to Supabase Auth, adding per-item "Did this make sense?" feedback capture, and shipping a private Module-0-only app for testers. The repo has no such split, auth is still Flask-Login, and no feedback mechanism exists. **The feedback capture is the notable loss** — it was the mechanism for learning which lessons confuse people, which is exactly what an unvalidated curriculum needs.

---

## 11. Pivots

Eight direction changes are traceable in the record.

**1. Bot-first → curriculum-first** *(28–29 June 2026)* — the defining pivot. Docs fully rewritten, bot-first architecture plans deleted, all bot-facing code stripped from the platform in a single commit (`0c1ebf5`): five API endpoints, the bot health admin route and log tail, the signal explainer service, the `BotEvent` model, and `market.py` reduced to a 6-line timezone stub. Bot files migrated to a separate `delta-bot` repo across nine commits. Rationale: *"The product does not launch because the bot is impressive. It launches because the learning experience is useful and coherent."*

**2. AI-first → AI optional** *(28 June)* — Groq assistant demoted to a possible later support layer. *"If AI adds complexity before the curriculum is strong, it is a distraction."*

**3. Workspace UI, three iterations** *(pre-June 19)* — a vis-network concept-map terminal → a draggable 5-pane shell → the current fixed 3-column terminal multiplexer. Each iteration's routes and templates were deleted rather than left behind.

**4. Curriculum v2 → v3** *(26 → 28 June)* — 42 items across 5 modules became ~97 items across 7 modules plus 4 stages, with hard gating on the foundation, a fork module, and path-based open layer.

**5. DB-seeded content → markdown-as-source-of-truth** *(26 July)* — the docs had flagged that `content/` markdown and the DB-backed app were unconnected. `seeds/load_content.py` bridged them; markdown files became the authoring surface and the DB became a render cache.

**6. Static lessons → guided interactive experience** *(26–27 July)* — driven by direct founder feedback in two rounds: first *"feel like a tour guide walking you through, not a wall of text,"* then *"we have everything and then just one or two lines of text"* — wanting buttons, interactivity, visual weight. Produced guided mode, the block library, and a content-depth pass that merged thin sections and roughly tripled Module 0's per-lesson word count.

**7. NVDA/META → familiar consumer brands** *(27 July)* — the contributor guide bans NVDA ("the learner does not know what a GPU is") and META ("negative associations, abstract business model") and mandates Starbucks, Nike, Apple, Uniqlo, McDonald's, eBay/StockX, Netflix. Module 0 — built before the guide was enforced — uses NVDA/META throughout and is marked "complete, do not modify." Resolution: Module 0 is grandfathered as the "before"; everything new uses approved brands; `0-check.md` stays on NVDA/META for within-module consistency. **This means the reference module a contributor will copy the *format* from also demonstrates the *anti-pattern*.**

**8. Broad audience → segment testing** *(16 July)* — from "anyone interested in the stock market" to actively testing students vs. knowledge workers to find where willingness-to-pay actually lives.

---

## 12. Timeline

| Date | Event |
|---|---|
| **May 27, 2026** | Earliest surviving artifacts — roadmap and technical-spec PDFs. A v1 predates this repository. |
| **Jun 10** | Delta Core roadmap document |
| **Jun 19** | **Initial commit: "Delta One v2"** — full Flask app, workspace multiplexer, Groq AI assistant, admin panel, all landing in one commit. Same-day documentation audit: 10 unimplemented placeholder files deleted, docs realigned to the real codebase. |
| **Jun 21** | Codebase audit document |
| **Jun 22** | Hero/waitlist landing page ships. 50-trade historical signals seed for the signal explorer demo. Render deploy files (Procfile, gunicorn). |
| **Jun 23** | Heavy build day: entire app unified to the terminal aesthetic (`#0a0b0c` / `#4ade80` / JetBrains Mono / 0px radius), `tier_required` decorator, onboarding blueprint, Pro badge, plus a run of 404/CSRF/migration fixes. |
| **Jun 26** | Curriculum v2 committed — 42 items, Module 0 lessons and activities. Team brand doc. |
| **Jun 27** | Old branding removed. Modules 1–4 curriculum draft. |
| **Jun 28** | **THE PIVOT.** Docs fully rewritten curriculum-first. Curriculum v3 — 7 modules, 4 stages, gating logic. Contributor guide expanded with the relatability audit, approved-brand list and tone rules. Six superseded bot-first documents deleted. "Private beta" label removed from the landing page. |
| **Jun 29** | Bot removal executed. Admin/skeleton audit. Quiz overhauled to 10 scenario-based questions. Curriculum stats added to admin. Infrastructure audit; waitlist cleaned to 2 real signups; pre-launch DB checklist written. |
| **Jul (early)** | Quiet — day job leaves no time for Delta One. |
| **Jul 16** | Phase 0 problem statement — audience segmentation reframed as an open validation question; Delta Pro formally described as "deliberately backtracked." |
| **Jul 17** | Handoff pack generated ahead of a model hand-off — `AGENTS.md`, `prompt.md`, `Code-Roadmap.md`, `Company.md`. DevLog.txt established as the mandatory first-read for every session, with a write-back rule at every milestone. |
| **Jul 20** | MVP build spec written — private Module-0-only app split from the public waitlist, Supabase Auth, per-item feedback capture. **Never implemented.** |
| **Jul 26–27** | **The big build session.** Five stacked PRs: app boot fixed (import chain broken since bot removal — app wouldn't start), Module 0 running end-to-end locally on SQLite, the lesson-delivery design spine, guided tour-style lessons, and the interactive block library plus content-depth pass. |
| **Jul 27 (later)** | Full-curriculum build scoped precisely — 88 remaining items — and two decisions made (brand conflict resolved; loader gap identified as blocking). Branch `content/full-curriculum` created off `feat/lesson-blocks`. **Zero commits. Paused before writing anything.** Constraint stated: Calgary on Aug 24, then university — this month is the only window before a September social/beta push. |
| **Aug 3** | Last file activity in the working tree (local DB). |
| **Aug 3–16** | **Deliberate break.** Recorded by the founder as a needed mental reset rather than a stall — "I can't be working on this 24/7 without running into headwind at some point." |
| **Aug 16 (today)** | 20 days with no commits. `content/full-curriculum` still checked out and still empty; five PRs still open. Company, legal, finance and AI-policy facts captured from the founder and recorded in §7. Monetization restructured to free-first with a staged Pro rollout. |
| **Aug 24** | Founder leaves for Calgary. |
| **Sept** | Intended social + beta push. |
| **Jan 1, 2027** | Target public launch. 138 days out. |

---

## 13. Risks

**Founder-time risk is the dominant one.** The August window identified on 27 July as the only stretch available for content work is more than half gone with nothing written. The three-week gap was a deliberate mental reset rather than a stall — which is healthier than the alternative and shouldn't be read as drift — but it doesn't change the arithmetic. 88 items, plus a source library that has to be assembled first, against a founder who leaves on 24 August and starts university after that. Two levers exist and neither has been pulled: the ~$5k budget, and Jacob.

**Merge risk.** Five stacked PRs and a sixth branch on top. Every day unmerged raises the cost of review and the chance of conflict. `main` currently does not contain a working lesson experience.

**Sequencing risk.** The loader fix is a hard prerequisite for the content sprint, and it hasn't started. Writing content first means discovering the gap after 88 files are on disk.

**Positioning risk.** The live public page sells the algo engine and backtest numbers. If the September push drives traffic there, arrivals are being sold the abandoned product — and the education content they'd actually get is thin outside Module 0.

**Validation risk, now reshaped.** Two waitlist signups. The audience question is unresolved and willingness to pay is openly assumed absent. The staged free-first rollout is a sensible response — but it converts a pricing problem into a **retention problem**: the free tier has to be good enough that people are still there in February to be sold to. The one mechanism designed to produce that signal, per-lesson "Did this make sense?" feedback, was specified in July and never built. It is cheap, and it is the highest-information thing missing from the product.

**Cadence risk.** "A new feature every month" is a public promise being made by a team of two, one of whom is at university, with no feature queue written down. Missing that cadence in month two is more damaging to trust than never having promised it.

**Name risk — accepted, knowingly.** "Delta One" is Delta Air Lines' trademarked premium-cabin brand, and separately the standard investment-banking term for delta-one desks and products. The founder has acknowledged the conflict and decided to keep the name. Recorded as a deliberate call, not an oversight.

The residual exposure splits in two, and only one half is serious:

- **Trademark.** Low-to-moderate. Trademarks are class-based, and market education is a different class of goods from air travel — but Delta Air Lines defends the "Delta" family aggressively, and financial services sit closer to their registrations than most sectors would. The practical risk is a cease-and-desist, not litigation, and the cost of one scales with how much brand equity exists when it arrives.
- **Search.** Certain and permanent. Delta One will never rank for "Delta One" — the competition is an airline and Wall Street. This is not a risk to manage, it is a constraint to design around: SEO and paid acquisition have to target qualified phrases ("delta one trading course," "learn how markets work") and brand-plus-modifier terms, never the bare name. Discovery has to come from social, campus and referral rather than organic search.

Mitigations that don't require renaming: register and consistently use a distinctive wordmark/logo rather than the plain words; keep messaging unambiguously in the education category; run a knockout search on the relevant trademark classes (education services and financial services) before spending money on brand assets; and keep the rename option genuinely open until there is an audience, since the code, curriculum and product all carry over intact — the only brand assets today are a landing page, a logo and two social handles.

**Single-point-of-knowledge risk.** Two founders, but the split is Bhanu on product, engineering and curriculum, and Jacob on marketing — so every line of code, every lesson and every approval still runs through one person, with no entity, no documented access process and no second engineer. Mitigation exists in spirit: DevLog.txt is an unusually disciplined handoff artifact, and the contributor guide is good enough that a paid writer could work from it on day one. The budget to hire that writer exists and is unused.

---

## 14. Recommended sequence

Ordered by dependency and by what unblocks the most.

1. **Merge the PR stack** (#1 → #5, in order). Nothing else is safe to build on until `main` reflects reality.
2. **Fix `load_content.py`** — generalize the filename parser to cover numeric checks, letter-stage lessons and stage checks; add `item_type="check"` with distinct styling; register all 11 remaining modules and stages in `MODULES`. Half a day, and it unblocks the entire content sprint.
3. **Write `0-check.md`.** Module 0 currently has no capstone, which means the one complete module can't actually be completed.
4. **Fix the landing page** — strip the algo-engine framing, backtest stats and unbuilt Core features. This is an hour of work protecting every impression the September push generates.
5. **Add the feedback mechanism from the July 20 spec.** Per-item yes/no plus optional comment. Cheap, and it is the only thing that will tell you which lessons fail before you scale the writing.
6. **Assemble the pre-approved source library** for Modules 1–6 and Stages A/B/C/R. Required by the AI policy before any writing can legitimately start, and delegable — this is the single best first task to hand to Jacob or to a paid contractor, because it needs judgement about *what counts as a good source* but not editorial voice.
7. **Then write content, module by module, with a load-and-verify checkpoint after each.** Prefer shipping Modules 1 and 2 at Module 0's depth over all 88 at skeleton depth — a shallow full curriculum reads as generic finance content, which the contributor guide itself names as the failure mode.
8. **Write the Terms of Service**, with a stated minimum age. Launch-blocking, and it resolves the under-13 data question cheaply.
9. **Write the founder agreement with Jacob** — 65/35, vesting, departure terms, binding on a future entity. One page, and the easiest version of this conversation is the one you have now.
10. **Reconcile `docs/technical-spec.md`** with curriculum v3 and the current repo layout.
11. **Work the pre-launch infrastructure checklist** — runs in parallel, off the content critical path. Stripe is no longer part of it; the transactional email sender still gates founding-user conversion on day one.

---

## 15. Reference

**Repository:** `github.com/justbrowsing37/delta-dev` · current branch `content/full-curriculum` · 62 commits · MIT licensed
**Public:** thedeltaone.pages.dev · linkedin.com/company/thedeltaone · instagram.com/thedeltaone · hello@deltaone.app
**Founders:** Bhanu Sugguna (founder — product, engineering, curriculum) — linkedin.com/in/bhanusugguna · Jacob Blais (co-founder, head of marketing)

**Canonical docs in this repo:**
`DevLog.txt` (read first — the plain-English running record) · `docs/product-vision.md` · `docs/roadmap.md` · `docs/technical-spec.md` · `docs/curriculum.txt` · `docs/contributor-guide.md` · `Claude Files/AGENTS.md`

**External planning docs referenced above** (in `~/Downloads`, not in the repo — worth pulling in):
`delta-one-problem-statement.md` (Jul 16) · `delta-one-mvp-build-spec.md` (Jul 20) · `delta_one_audit.md` (Jun 21) · `DeltaOne_Team_Brand_Doc.pdf` (Jun 26)

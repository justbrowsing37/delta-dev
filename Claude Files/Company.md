# Delta One — Company Operations & Information Handbook

*Last updated 16 August 2026. Answers sourced directly from Bhanu Sugguna.*

This file was previously a blank questionnaire. It is now populated. Items marked **⚠ OPEN** are still unanswered — treat those as unknown, not as zero. Do not guess at them; ask.

Full business context, timeline and current state: `docs/business-overview.md`.

---

## 1. Company overview

- **Legal entity:** none. Delta One is **Bhanu Sugguna personally** — sole trader in practice. No incorporation planned at this stage.
- **Stage:** pre-launch, pre-revenue.
- **Business model:** freemium. Free curriculum tier; paid Pro tier introduced after launch.
- **Target audience:** beginners who have never opened a brokerage account. Two segments under test — students and early-career knowledge workers. Which one pays is unresolved.
- **Value proposition:** structured, sequenced, time-respecting market education that explains *why* markets move, built by someone inside the target user experience rather than a finance institution talking down.

**Licensing — resolved 16 Aug 2026.** `LICENSE` is now proprietary, all rights reserved, covering code, `content/` and `docs/`, with a contribution-assignment clause. It replaced an MIT licence. The repo has been private since inception, so the MIT grant never reached a third party and there was nothing to revoke.

**Name — decision recorded.** "Delta One" collides with Delta Air Lines' trademarked cabin brand and with standard investment-banking terminology. The founder has acknowledged this and is keeping the name. Consequence to design around: the product will never rank for its own name, so acquisition must come from social, campus and referral, with SEO targeting qualified phrases rather than the bare brand.

## 2. Product overview

Delta One is **primarily an education product.** Not a trading tool, not a community.

- **Delta Core** — the launch product. ~97 lessons, activities and checks across 7 modules and 4 stages. Hard-gated foundation, then a fork into learner-chosen paths.
- **Delta Pro** — momentum-signal algo engine. Parked in a separate `delta-bot` repo since 29 June 2026. Returns only when genuinely ready.

**Core user journey:** land → sign up → onboarding quiz → Module 0 → work through gated foundation modules → Module 6 fork → chosen stage.

**Success for a new user:** they can look at a chart and explain in plain English what price is doing and why.

## 3. Product positioning

**Known for:** clear, honest, structured market education. Concepts before jargon. Examples anchored to brands the learner already understands.

**Not known for:** signals, bot dashboards, AI-first gimmicks, get-rich-quick framing.

**Messaging guardrails:**
- No advice language, ever. "This is how it works," never "you should buy."
- No fake hype. Trading is a skill; treat it like one.
- No jargon without definition on first use.
- Do not market Delta Pro or the algo engine while it is parked.

**⚠ Known violation:** the live landing page still leads with "an algo trading engine underneath," shows backtest statistics as headline social proof, and dedicates half its feature grid to Delta Pro. It contradicts the above and needs fixing before the September push.

## 4. Team and roles

| Person | Role | Owns |
|---|---|---|
| **Bhanu Sugguna** | Founder | Product, engineering, curriculum, content approval, all final decisions |
| **Jacob Blais** | Co-founder, Head of Marketing *(working title)* | Marketing |

No one else is involved in any capacity. The contributors addressed in `docs/contributor-guide.md` are a **future audience, not existing people.**

**Approvals:** all product and content sign-off is Bhanu. There is no second approver.

**Equity: 65% Bhanu / 35% Jacob**, agreed August 2026.

**⚠ OPEN:** no entity exists to hold shares in, and no vesting has been agreed — so as it stands, the split is an intention rather than a grant, and Jacob's 35% is unconditional from day one. Needs a one-page founder agreement recording the split, vesting (four years / one-year cliff is standard), and departure terms, binding on a future entity and convertible to real shares at incorporation.

## 5. Product roadmap

**Launch:** 1 January 2027, **free tier only**. Treated as a hard commitment.

**Post-launch monetization, staged:**
1. Jan 2027 — free tier only
2. ~Feb 2027 — Pro introduced
3. Monthly thereafter — one new feature per month, consistent cadence

**Launch-critical:** curriculum content (88 items remaining), the merged lesson-delivery stack, the content loader fix, hosting and DB migration to Supabase, transactional email, Terms of Service.

**Explicitly deferred:** Stripe and all payment infrastructure (not needed until ~Feb 2027), Delta Pro, AI assistant as a headline feature, Max tier, community features, mobile.

**⚠ OPEN:** the monthly feature cadence is a public commitment with no feature queue written down.

## 6. Curriculum and content operations

**Authoring:** markdown files in `content/module-X/` and `content/stage-X/`, committed to the repo. `seeds/load_content.py` loads them into the database. Markdown is the source of truth; the DB is a render cache.

**Standard:** `docs/contributor-guide.md` is binding — exact templates for lessons, activities and checks; 400–550 words per lesson; approved example brands only; tone rules enforced.

**Approval:** Bhanu reads every item for usability, readability and user fit before it goes live.

**Module 0 caveat:** marked complete and not to be modified, but it uses NVDA/META throughout — brands the contributor guide explicitly bans. Copy its *format*, not its *examples*.

## 7. Engineering operations

- **Stack:** Flask, SQLAlchemy, Flask-Login, Jinja2, vanilla JS/CSS, Alembic migrations.
- **Hosting:** Cloudflare Pages (static waitlist), Render (Flask app, still on the dev server).
- **Database:** Supabase Postgres in production (platform schema not yet created); SQLite locally.
- **Local dev:** `DATABASE_URL="sqlite:///delta_local.db"` — no Postgres needed. See DevLog.txt for the exact commands and seeded test logins.
- **Workflow:** feature branches, PRs against `main`. Five PRs are currently open and stacked in dependency order.

**⚠ OPEN:** branch protection status, whether Bhanu self-merges without review, rollback procedure, and the production hosting decision (Render vs. a dedicated server).

## 8. Data and information handling

**Collected:** email, hashed password, tier, lesson progress, AI interaction logs, session records, waitlist emails.

**Sensitive:** email addresses and password hashes. Waitlist currently holds 2 real signups.

**Age policy:** open to all ages, informal floor around 15. ⚠ With account creation and email collection, any under-13 user brings COPPA (US) and GDPR children's-data (UK/EU) obligations into scope. Mitigate with a stated minimum age in the TOS and at signup — not an age-verification system.

**⚠ OPEN:** what analytics or tracking runs on the live site; whether any compliance regime is being actively observed.

## 9. Security and access

GitHub, Render, Cloudflare and Supabase are all **private, Bhanu as sole account holder.** No shared credentials, no third-party access.

From the code: production refuses to boot without `SECRET_KEY` set as an environment variable — no fallback default. All API endpoints require authentication.

**⚠ OPEN:** where production secrets are stored (Render env vars vs. a local `.env`); whether anything sensitive was ever committed; rotation and incident-response expectations.

**⚠ Bus factor of one.** Every system runs on a single account holder with no second person and no documented recovery path. Proportionate fix at this stage: store 2FA recovery codes and account recovery details somewhere durable and separate from the laptop.

## 10. AI and automation policy

**AI-written curriculum content is permitted, under strict sourcing conditions.**

| | |
|---|---|
| **Permitted** | AI does the writing, formatting and compilation of information |
| **Required** | AI works **only** from sources Bhanu has pulled and pre-approved. He controls what it reads |
| **Hard red line** | AI must **never** write from its own knowledge. If it cannot find something in the approved sources, stop and ask a human for a URL that covers it |
| **Review** | Every item is human-read for usability, readability and user fit before it goes live |
| **Disclosure** | Not planned — AI authorship is not disclosed to learners |

**Operational consequence for any agent picking this up:** a pre-approved source library for Modules 1–6 and Stages A/B/C/R **does not yet exist**. Do not start writing curriculum content until it does. Ask Bhanu for sources; do not substitute your own knowledge, however confident you are.

## 11. Legal, finance and commercial

- **Funding:** self-funded by Bhanu. No outside money, grants or investment.
- **Run cost:** effectively zero — everything is on free tiers.
- **Budget ceiling:** ~$5,000, adjustable with justification. There is explicit room to pay a curriculum writer.
- **Partnerships/contracts:** none.

**Regulatory position** (founder's view, **not professionally verified**): teaching trading methodology — market structure, liquidity, entries, stops, targets — is common knowledge and legal to teach. The line is crossed by specific recommendations ("invest in Nvidia"). Delta One does not do that, and the contributor guide's ban on advice language enforces it editorially. The future pressure point is Delta Pro's live signals, where the distinction is thinner.

**⚠ OPEN:** no Terms of Service (needs writing, launch-blocking), no privacy policy, no legal review. Domain ownership of `deltaone.app` and whether `hello@deltaone.app` is a live inbox.

## 12. Communication and documentation standards

- **`DevLog.txt` is the canonical running log.** Read it first, every session, before anything else. Append a dated entry at every milestone.
- Canonical docs live in `docs/`. `docs/business-overview.md` holds the full business picture.
- Docs describe the *current* direction only. Superseded documents get deleted, not left in place.
- Bhanu maintains this handbook.

## 13. Remaining open items

Everything marked ⚠ above, consolidated:

1. Founder agreement with Jacob — 65/35 recorded, but no entity, no vesting, nothing in writing
2. Terms of Service (launch-blocking) and privacy policy
3. Analytics and tracking currently in use
4. Where production secrets are stored; rotation and incident response
5. Account recovery / bus-factor mitigation for the four private accounts
6. Branch protection, review policy, rollback procedure
7. Domain ownership and whether the contact inbox is live
8. The feature queue backing the monthly post-launch cadence
9. Landing-page copy still marketing the parked algo engine

**Closed since the first pass:** MIT licence replaced with proprietary (16 Aug) · name conflict acknowledged and name retained (16 Aug) · access model confirmed private, sole account holder (16 Aug).

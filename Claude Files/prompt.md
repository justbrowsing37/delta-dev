# Sonnet 5 Prompt — Delta One

You are working inside the Delta One repository. Your job is to continue development autonomously and make useful progress without needing hand-holding.

## Mission

Advance the Delta One product as a curriculum-first market education platform. Prioritize the learning experience, lesson delivery, contributor workflow, and app stability over bot/signal infrastructure.

## What this project is

Delta One is a Flask-based web app for teaching beginners how markets work through structured lessons, activities, progress tracking, and a simple learning workspace.

The product is not currently positioned as:
- a public trading bot,
- a signal platform,
- or an AI-first assistant.

## Primary goals

When you work in this repo, prefer tasks that:
1. improve the curriculum experience,
2. improve lesson/module navigation and progress handling,
3. make the app easier to run or maintain,
4. improve contributor onboarding or content workflow.

## Important product constraints

- Keep the curriculum-first direction intact.
- Do not turn the app into a bot dashboard or trading signal tool.
- Treat AI as optional support infrastructure, not the core product.
- Follow the documentation in the docs/ folder as the source of truth.

## Repository reality

This repo contains both:
- a curriculum-first product, and
- older bot/signal-related infrastructure.

The current implementation is a Flask app with SQLAlchemy models, Flask blueprints, and database-backed lesson content. The content files under content/ are not yet fully wired into the runtime as a markdown-driven system.

## Files to read first

Start by reading these files in order:
1. **DevLog.txt** — the running development log. Always read this FIRST,
   before anything else, in every session. It's the plain-English record of
   what's actually been built, what's in progress, and what's still open —
   more current than any of the docs below. See "Documentation policy" below
   for the write-back rule.
2. AGENTS.md
3. docs/product-vision.md
4. docs/roadmap.md
5. docs/technical-spec.md
6. docs/contributor-guide.md
7. app/__init__.py
8. app/services/curriculum.py
9. app/routes/workspace.py
10. tests/test_smoke.py

## Documentation policy — keep DevLog.txt current

DevLog.txt is the single, universal running log for this project — the same
file every session writes to, named consistently on purpose so "check the
log" always means the same thing regardless of which model or session is
picking this up.

- At the start of every session, read DevLog.txt before doing anything else.
- At every major milestone — a PR opened, a feature completed, a real bug
  fixed, a meaningful architecture decision — append a new dated entry
  before the session ends, following the existing entries' format (dated
  section header, "─── Subsection ───" dividers, past-tense plain English,
  bullet lists). Insert new entries just before the "END OF DEVELOPMENT LOG"
  footer.
- If a session produces meaningful progress but is about to end without a
  DevLog.txt entry — or if it's been a while since the last entry and more
  work has piled up undocumented — proactively ask Bhanu whether to add one
  before wrapping up. Keep the ask short; he'll almost always say yes.

## Working rules

- Prefer small, targeted changes over broad rewrites.
- Preserve existing architecture unless there is a clear reason to change it.
- Make changes that align with the product direction in the docs.
- Write or update tests when behavior changes.
- Verify your work with fresh test runs or app import checks before claiming success.
- If you are unsure whether a change belongs in the app, curriculum layer, or bot layer, default to the docs and current product direction.

## Default workflow

When taking on a task:
1. Read the relevant docs and implementation files.
2. Reproduce or understand the current behavior.
3. Make the smallest change that addresses the real issue.
4. Add or update tests if appropriate.
5. Run the relevant verification commands.
6. Summarize what changed and any follow-up items.

## Suggested starting points

If no task is specified, choose one of these high-value next steps:
- improve the lesson/workspace experience,
- fix a navigation or progress issue,
- make curriculum content loading more coherent,
- improve contributor setup or documentation,
- or clean up an app stability issue.

## Verification expectations

Before finishing a task, verify with evidence.
Examples:
- run pytest for relevant tests,
- run targeted import checks,
- or verify the affected route or service behavior.

Do not say something is fixed unless you have fresh verification output.

## Important implementation note

The docs and content structure suggest a markdown-first curriculum system, but the current app uses SQLAlchemy-backed lesson records and seed scripts. If you need to connect content files to the runtime, implement that path intentionally rather than bolting on a hack.

## First action on startup

Start by reading the handoff files, then run the test suite to establish the current baseline. After that, pick one meaningful next task and move forward.

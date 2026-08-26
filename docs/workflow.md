# Delta One — Operating Workflow

**Purpose:** provide one repeatable way to decide what to work on, produce it,
review it, ship it, and learn from it.

This workflow is based on the current business direction: **Delta Core is a
curriculum-first, free launch product.** The bot is private infrastructure, AI
is optional, and Pro work begins after the January 1, 2027 launch.

## 1. Operating principles

1. Curriculum quality is the primary product work.
2. Work is ordered by dependency and learning value, not by technical novelty.
3. A module is not done when files exist. It is done when the content loads,
   the learner can complete it, and the team has reviewed the experience.
4. Every content claim must have an approved source or a human-supplied source
   URL. AI must not fill gaps from its own knowledge.
5. Ship small vertical slices: content, delivery, and validation should move
   together.
6. Do not add a launch dependency for the bot, payments, or AI.

## 2. Work queue order

Use this order when choosing the next task:

1. **Unblock the system:** merge the stacked lesson PRs, fix the content loader,
   and register the full curriculum structure.
2. **Complete the learning path:** add the Module 0 check, then write and ship
   the remaining curriculum module by module.
3. **Protect the audience:** correct public positioning and add per-item
   learner feedback.
4. **Make launch reliable:** terms, age policy, migrations, production
   configuration, email, hosting, and end-to-end checks.
5. **Prepare post-launch work:** maintain a queue of validated Pro features;
   do not build payment infrastructure before it becomes necessary.

When two tasks have similar priority, choose the one that removes a dependency
or produces direct learner evidence sooner.

## 3. Ownership and approval

| Area | Working owner | Required approval |
|---|---|---|
| Product direction, curriculum, engineering | Bhanu | Bhanu |
| Audience research, distribution, source discovery | Jacob | Bhanu for source approval and product claims |
| Paid curriculum writing | Assigned writer | Bhanu for editorial and factual review |
| Marketing copy and launch campaigns | Jacob | Bhanu for product and compliance accuracy |
| Legal, age policy, licensing, founder agreement | Bhanu with professional review where needed | Both founders for founder terms |

No contributor should infer approval from a merged branch alone. Content is
published only after the content review below is complete.

## 4. Content workflow

### Step 1: Define the item

Before drafting, record:

- module and item number;
- item type: lesson, activity, or check;
- the learner outcome in one sentence;
- the previous item it builds on;
- the chart, data, or free tool the learner needs;
- the approved example brand;
- the source packet or human-supplied URLs.

For activities, name the artifact the learner carries forward. Each activity
must build on the previous activity's output.

### Step 2: Prepare and approve sources

Create a source packet before AI-assisted drafting begins. Each packet should
contain the URLs or documents used, the claims they support, and the date they
were approved by Bhanu.

If a required fact is missing, stop and obtain a human-supplied source. Do not
ask AI to complete the gap from general knowledge. Source discovery can be
delegated; source approval cannot.

### Step 3: Draft to the contributor standard

Use the exact templates in [contributor-guide.md](contributor-guide.md).

- Lessons: 400–550 words and a 3–4 minute read.
- Activities: concrete, free-tool friendly, and connected to prior work.
- Checks: self-assessment, short-answer questions, one chart task, and an
  honest recovery path.
- Voice: plain English, second person, active, direct, and free of advice.
- Examples: introduce the familiar brand or situation before naming the
  market term; use approved consumer brands by default.

AI may help write, format, or compile only from the approved source packet.
Every draft receives a human review for factual accuracy, usability,
readability, learner fit, and financial-advice boundaries.

### Step 4: Review the item

The reviewer checks:

- required headings and file naming;
- correct module ordering and `Connects to` references;
- one new concept at a time;
- no unsupported claims, recommendations, hype, or unexplained jargon;
- activity instructions that can be completed without premium tools;
- a useful `Next` section and a clear learner artifact;
- examples that a beginner can recognize;
- length and readability.

Return the item for revision when any check fails. Do not compensate for weak
content with UI polish.

### Step 5: Load and verify

After each item or small batch:

1. run the content loader locally;
2. confirm the item appears in the correct module and order;
3. confirm the item type, check gating, and activity links;
4. open it in both Read and Guided views;
5. mark it complete and confirm progress persists;
6. record any broken import, rendering, or navigation behavior as an issue.

At the end of each module, run the same check against the module gate and
complete the module's check as a learner would.

## 5. Engineering workflow

For app or infrastructure work:

1. State the learner or operator problem and the smallest acceptance test.
2. Check the owning route, service, model, seed path, or template before
   editing.
3. Keep the change on the smallest dependency-aware branch.
4. Add or update a focused test for behavior that can regress.
5. Run the focused test immediately, then the full smoke suite when practical.
6. Review the change for auth, progress persistence, content ordering, and
   production configuration impact.
7. Merge stacked work from the base dependency upward.
8. Deploy to staging and perform the relevant user journey before production.

The content loader is part of the product contract. A new filename or item
type is incomplete until parsing, database seeding, rendering, and gating all
support it.

## 6. Learner validation loop

For every released module or meaningful UX change:

1. Put the slice in front of a small beginner cohort.
2. Capture per-item “Did this make sense?” feedback with an optional comment.
3. Record where the learner hesitated, skipped, misunderstood, or needed help.
4. Fix the highest-frequency or highest-risk confusion first.
5. Re-run the module check and compare completion and feedback patterns.

Feedback is evidence, not a popularity vote. A low-completion item needs a
diagnosis before it gets simplified or removed.

## 7. Weekly operating cadence

### Weekly planning

Choose one primary outcome and no more than three supporting tasks. The primary
outcome must be a visible product improvement, such as “Module 1 loads and is
usable end to end,” not “work on curriculum.” Assign an owner and acceptance
check to every task.

### Work sessions

Each session starts by reading `DevLog.txt` and ends with one of:

- a merged, tested change;
- a documented blocker with its next action; or
- a validated learner finding.

Keep the current branch and work state clear so another person can continue.

### Weekly review

Review:

- content items completed and their average word count;
- items loaded and verified successfully;
- learner feedback and unresolved confusion;
- open blockers and dependencies;
- production and legal readiness;
- the next week's single primary outcome.

Update `DevLog.txt` for every meaningful decision, completed feature, opened
PR, or resolved bug.

## 8. Definition of done

### A content item is done when

- it follows the contributor template and naming rules;
- its sources are approved and its claims have been human-reviewed;
- it passes the tone, example, safety, and usability review;
- it loads into the correct module and order;
- it renders correctly in Read and Guided views;
- its progress behavior works;
- its relationship to neighboring activities or checks is clear.

### A module is done when

- every planned item meets the item definition of done;
- its activities form a visible chain of learner artifacts;
- its check gates the next module correctly;
- a beginner can complete it using available tools;
- learner feedback has been collected and the highest-risk issues addressed.

### Launch is ready when

- Modules 0–6 and the committed stages are real, coherent, and loaded;
- the lesson, activity, progress, and gating journeys pass end to end;
- public copy describes Delta Core rather than the parked bot;
- Terms of Service and the minimum-age policy are published;
- production migrations, secrets, email, hosting, rollback, and monitoring are
  verified;
- a new user can sign up, onboard, learn, complete work, and return later;
- launch smoke tests pass on the production environment.

## 9. Decision rules

- If a task improves the curriculum and another improves internal polish, do
  the curriculum task first.
- If content and loader behavior disagree, fix the loader or the canonical
  content contract before writing more files.
- If an AI feature competes with lesson quality, defer the AI feature.
- If a marketing claim describes an unbuilt feature, remove or rewrite it.
- If a task cannot name its owner, acceptance check, and next dependency, it is
  not ready to enter the work queue.
- If a task is repeatedly blocked by Bhanu's review capacity, use the budget to
  delegate source preparation or first-pass writing, while keeping final
  editorial approval with Bhanu.

## 10. Immediate starting sequence

1. Merge the five lesson-delivery PRs in dependency order.
2. Generalize `seeds/load_content.py` for checks, stages, and all curriculum
   groups.
3. Add and load `content/module-0/0-check.md`.
4. Correct the public landing page's positioning and unsupported promises.
5. Add per-item learner feedback.
6. Build the approved source library and assign writing capacity.
7. Write, load, verify, and test Modules 1 and 2 before expanding the writing
   queue further.
8. Run launch-readiness work in parallel, with payments deferred until the
   planned Pro phase.
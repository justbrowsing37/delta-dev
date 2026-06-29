# Contributor Guide

## What contributors are helping build

Contributors are helping build the Delta Core curriculum. The main job is not bot work. The main job is making the learning experience strong, clear, and consistent.

## Priority work

- Write lessons.
- Write activities.
- Improve clarity.
- Keep examples concrete.
- Maintain a consistent voice and structure.

## Lesson format

Every lesson must follow this exact structure:

```
# [Title]

## The idea in one sentence

## Why this matters

## How it works

> **Key concept:** [...]

## What this looks like in the market

## Common mistake

## Next
```

Target length: 400–550 words. Aim for a 3–4 minute read.

## Activity format

Every activity must follow this exact structure:

```
# Activity [X.XA] — [Title]

## What you're doing

## What you need

## Your task

## What to look for

## Connects to
```

Activities must build on the previous activity in the module. The `Connects to` section should make the chain explicit.

## Tone rules

- Plain English.
- Second person ("you", not "traders" or "users").
- Active voice.
- No fluff openers (do not start with "In today's markets...").
- Sharp, not condescending.
- No advice language ("you should buy" is not acceptable).
- No fake hype.

## Examples

- Use NVDA or META as the default real-world tickers.
- Do not use hypothetical companies.
- Use real chart structure language (ranges, sweeps, entries, rejections).

## File naming

- Lessons: `X.Y-short-title.md` (e.g. `0.1-what-is-the-market.md`)
- Activities: `X.YA-short-title.md` (e.g. `0.1A-find-the-range.md`)

## File locations

- Curriculum content: `content/module-X/`
- Canonical docs: `docs/`
- App code: `app/`

## Submission standard

Good curriculum work is:
- structurally consistent (follows the template exactly),
- easy to follow on first read,
- concrete (uses real examples, not vague generalities),
- and useful to a beginner who knows nothing.

If a draft is vague, overly long, or sounds like generic finance content, it needs revision before it goes into the repo.

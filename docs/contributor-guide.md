# Contributor Guide

## What contributors are helping build

Contributors are helping build the Delta Core curriculum. The main job is not bot work. The main job is making the learning experience strong, clear, and consistent.

Delta One is a curriculum-first product. The learner coming in has never opened a brokerage account. They have heard the word "stock" but it means nothing concrete to them yet. Your job is to make it concrete — through examples they already understand, language they already use, and concepts that land before the jargon does.

---

## Priority work

- Write lessons.
- Write activities.
- Write module checks.
- Improve clarity.
- Keep examples grounded in brands the learner knows.
- Maintain a consistent voice and structure across every item.

---

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

Do not exceed 550 words. If you can't explain it in 550 words, the lesson is too broad — split it.

---

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

Activities must build on the previous activity in the module. The `Connects to` section should make the chain explicit — name the prior activity or lesson by number, not just by concept.

---

## Check format

Every module ends with a Check item. This is what gates the next module. It must follow this exact structure:

```
# Module X Check

## What you should be able to do now
(3–4 bullets. Specific skills, not vague goals.)

## Quick questions
(3–5 short prompts. Not multiple choice. Require genuine thought.)

## Chart task
(One real-chart application prompt. Must be doable without premium tools.)

## Before you move on
(Honest self-assessment. "If you can't do X without looking it up, go back to lesson Y.")
```

The check is not a quiz. It is a genuine self-assessment. Write it like you are talking to someone who is about to make real decisions with real money. Be honest.

---

## Tone rules

- Plain English. If a 16-year-old can't follow it, rewrite it.
- Second person ("you", not "traders" or "users" or "the learner").
- Active voice. Passive voice is almost always weaker — avoid it.
- No fluff openers. Do not start with "In today's markets...", "Trading can be...", or any throat-clearing sentence.
- Sharp, not condescending. Assume the learner is intelligent but uninformed. Never talk down.
- No advice language. "You should buy" is never acceptable. "This is how it works" always is.
- No fake hype. Do not imply trading is easy, exciting, or a path to wealth. It is a skill. Treat it like one.
- No jargon without explanation. Every term that is not plain English must be defined the first time it appears.
- No hedging. Do not write "some traders believe" or "it's often said that." State what is true, directly.

---

## Positioning and examples

This is the most important section in this guide. Read it carefully.

### The core rule

**Never introduce a company and a concept at the same time. Only one thing should be new.**

If the learner has to figure out what the company does AND what the market concept means, they are doing two jobs at once. One of them will fail. The concept loses.

The fix is simple: use companies the learner already has a relationship with. They have been to Starbucks. They own a Nike product. They have heard of Apple. The brand is already understood — so the market concept is the only new thing.

### Approved example brands

Use these by default:

| Brand | Why it works |
|---|---|
| **Starbucks** | Universal. Everyone has been. Everyone understands what they sell and roughly how the business works. |
| **Nike** | Strong brand story. Hype drops, collabs, limited releases — all useful for explaining demand, sentiment, and price moves. |
| **Apple** | Everyone owns a product. The upgrade cycle, the product launches, the brand loyalty — all map well to market concepts. |
| **Uniqlo** | Expanding into new markets, quiet but strong fundamentals, not hype-driven — good for long-term and macro concepts. |
| **McDonald's** | Everywhere, consistent, recession-proof reputation — useful for explaining defensive stocks, stability, volume. |
| **eBay / StockX** | Bidding mechanics, price discovery, buyers and sellers meeting at a clearing price — perfect for explaining how an exchange works. |
| **Netflix** | Subscription model, subscriber growth and churn, earnings sensitivity — useful for explaining growth stocks and expectations. |

You can use other brands if they are a better fit for a specific concept. The test is: does the learner already have a relationship with this brand? If you have to explain what the company does, pick a different one.

### What NOT to use

- **NVDA / Nvidia** — The learner does not know what a GPU is or why it matters. The brand has no emotional resonance for a beginner.
- **META / Facebook** — Negative associations. Abstract business model. Hard to explain why the stock moves.
- **Any ticker-first reference** — Do not write "SBUX" when you mean Starbucks. Use the real name. Tickers come after understanding.
- **Hypothetical companies** — Never. "Imagine a company called XYZ Corp" distances the learner from reality. Use real brands.
- **Niche or regional brands** — If there's any chance a learner hasn't heard of it, don't use it as the primary anchor.

### How to position an example

The example should come before the term, not after it.

**Wrong:**
> A liquidity sweep is when price moves beyond a key level to trigger stop orders before reversing. For example, imagine this happening on a Starbucks chart.

**Right:**
> You've seen this before. A shoe drops. Everyone puts in an alert at the price where it sold out last time. The price dips just below that level — triggering every alert, every panic sell — then bounces straight back up. That's a liquidity sweep. Price went where people were watching, took what was there, and reversed.

In the wrong version, the learner has to hold the definition in their head and then try to apply it. In the right version, the concept already makes sense before it has a name.

### Concept-to-brand mapping (reference)

Use this as a starting point, not a constraint:

| Concept | Suggested anchor |
|---|---|
| What is a stock? | Starbucks — you own a small piece of every cup sold |
| Owning a share / buybacks | Apple — fewer owners, your slice gets bigger |
| How an exchange works | eBay or StockX — bidding, listings, price clears when buyer meets seller |
| What moves a stock price? | Nike collab drop — demand spikes instantly, price follows |
| Market sentiment | Uniqlo expanding into a new city — everyone's talking about it before the numbers come in |
| Trading range / consolidation | Starbucks between earnings — nothing moves it, price sits in a band |
| Support and resistance | A store that always runs the same sale at the same price — price keeps returning to that level |
| Retail vs institutional | You buying 5 Nike shares vs a pension fund buying 2 million — same stock, completely different impact |
| Liquidity | A busy market stall at noon vs a quiet one at 3am — try selling at both |
| Stop hunt / engineered move | A flash sale that disappears the second you click buy — price dips, grabs stops, bounces |
| Price doesn't move straight | A queue at a popular restaurant — moves forward, stalls, surges, stalls again |
| The obvious trade is often wrong | Everyone lines up for the same limited drop and it's picked over by the time they arrive |

---

## File naming

- Lessons: `X.Y-short-title.md` (e.g. `0.1-what-is-a-stock.md`)
- Activities: `X.YA-short-title.md` (e.g. `0.1A-calculate-ownership.md`)
- Checks: `X-check.md` (e.g. `0-check.md`)

---

## File locations

- Curriculum content: `content/module-X/` or `content/stage-X/`
- Canonical docs: `docs/`
- App code: `app/`

Module 0 content is complete and live in `content/module-0/`. Do not modify it.

---

## Submission standard

Good curriculum work is:
- Structurally consistent — follows the template exactly, no improvised sections
- Easy to follow on first read — if you have to re-read a sentence to understand it, rewrite it
- Concrete — real brands, real mechanics, no vague generalities
- Honest — does not oversell trading, does not hide the difficulty
- Useful to a beginner who knows nothing and is about to make real decisions

If a draft is vague, overly long, sounds like generic finance content, or uses brands the learner won't recognise, it needs revision before it goes into the repo.

When in doubt, ask before you write. It is easier to clarify scope than to rewrite content.

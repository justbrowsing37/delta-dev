# Delta One

Delta One is a curriculum-first market learning product. The goal is to help beginners understand how markets move, how price behaves, and how to reason about market structure through lessons and applied activities.

The current product priority is simple:
- Build the curriculum well.
- Build the lesson delivery system.
- Make onboarding contributors easy.
- Keep the bot private and in the background.
- Keep AI as optional future work, not a launch dependency.

## Current product direction

Delta One is not being positioned as a public trading bot or signal service at launch.

At launch, the user-facing product is Delta Core:
- structured lessons,
- progressive activities that build on one another,
- lesson progress tracking,
- and a clean learning workspace for reading and working through concepts.

The bot still exists, but it is not the main promise of the product. It stays in the background as private infrastructure and as a possible future source of examples or case studies.

AI is also not a launch-critical feature. It may later support explanations, summaries, or guided help, but it is intentionally sidelined until the curriculum and lesson system are strong.

## Launch target

Target launch: January 1, 2027.

The launch standard is not "public bot sophistication."
The launch standard is:
- a clear curriculum,
- enough lesson depth to be genuinely useful,
- a functioning lesson viewer,
- progress tracking,
- contributor-friendly documentation,
- and stable hosting and onboarding.

## Repo structure

```text
DeltaOne/
├── app/                  # Flask app
├── content/              # Curriculum content in markdown
├── docs/                 # Canonical project documentation
├── seeds/                # Seed scripts
├── static/               # Frontend assets
├── tests/                # Tests
├── sweep_*.py            # Private bot / strategy infrastructure
└── README.md
```

## Canonical docs

- `docs/product-vision.md` — what Delta One is, what it is not, and what matters now.
- `docs/roadmap.md` — launch path centered on curriculum and lesson delivery.
- `docs/technical-spec.md` — current application and content architecture.
- `docs/curriculum.txt` — module and lesson/activity structure.
- `docs/contributor-guide.md` — how collaborators should write and submit curriculum work.

## Contributor focus

If you are joining the project to help, the priority is curriculum work first.

That means:
- writing lessons,
- writing activities,
- keeping tone and structure consistent,
- improving clarity,
- and helping the learning experience feel coherent from start to finish.

## Current status

- Waitlist site is live on Cloudflare Pages.
- Curriculum structure has been expanded to a lesson/activity pattern.
- Module 0 has been started in repo content files.
- Documentation has been rewritten to match the curriculum-first direction.

## Principle

Curriculum is the product.
Everything else supports it.

## Built by

Bhanu Sugguna — Founder
[LinkedIn](https://linkedin.com/in/bhanusugguna)

[Delta One on LinkedIn](https://linkedin.com/company/thedeltaone)

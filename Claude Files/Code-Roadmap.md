# Delta One Product Roadmap Plan

This document outlines the most valuable next builds for Delta One based on the current product direction: a curriculum-first market education experience.

## Guiding principle

The product should feel like a clear, high-quality learning experience before it expands into any bot, AI, or signal-based features.

## Priority order

The highest-value work should focus on the following areas in order:

1. Improve the lesson delivery experience
2. Strengthen curriculum content workflow
3. Improve onboarding and progress clarity
4. Add light product polish and contributor support
5. Keep bot and AI work secondary

---

## 1. Improve the lesson delivery experience

### Why this matters

The core promise of Delta One depends on users being able to move through lessons comfortably, understand what comes next, and feel progress as they learn.

### What to build

- Better module and lesson navigation
  - clearer left/right movement between lessons
  - better section anchors
  - stronger visual hierarchy
- Cleaner reading experience
  - improved typography and spacing
  - easier scanning of key concepts
  - more readable lesson layout
- Persistent progress state
  - remember where the user left off
  - surface completed lessons clearly
  - show module-level progress at a glance
- Smoother lesson transitions
  - transition from lesson to activity to check without friction
  - make the learning path feel intentional

### Expected outcome

Users should feel that the product is a coherent learning system rather than a collection of disconnected content pages.

---

## 2. Strengthen curriculum content workflow

### Why this matters

The repo already contains a strong conceptual curriculum direction, but the runtime experience can be made more coherent and maintainable.

### What to build

- Connect curriculum content more directly to the app
  - reduce friction between markdown content and the database-backed lesson system
  - make content easier to publish and maintain
- Add a content publishing path
  - support draft, published, and hidden states more clearly
  - make it easier to review new content before it appears to users
- Improve content authoring support
  - template-based lesson creation
  - structure validation for lessons, activities, and checks
  - clearer contributor expectations

### Expected outcome

Contributors can add or improve curriculum content with less confusion and less manual setup.

---

## 3. Improve onboarding and progress clarity

### Why this matters

New users need a clear path from signup to first meaningful learning experience.

### What to build

- Better first-run onboarding
  - explain what the product is and how to begin
  - reduce cognitive load for first-time users
- Clearer progression logic
  - show what is available now
  - show what unlocks next
  - explain the difference between foundation modules and later stages
- Stronger progress feedback
  - module completion states
  - milestone recognition
  - encouragement without overcomplicating the experience

### Expected outcome

A new user should understand quickly what Delta One is, what to do next, and how far they have progressed.

---

## 4. Add light product polish and contributor support

### Why this matters

The product should feel finished and reliable, especially for a learning experience where clarity matters more than flashy features.

### What to build

- A cleaner workspace shell
  - clearer sidebars and navigation
  - better module summaries
  - visually obvious learning state
- Better documentation inside the repo
  - onboarding docs for contributors
  - quick-start instructions for running the app
  - examples of expected lesson and activity structure
- Small UX refinements
  - more responsive layouts
  - fewer dead ends
  - smoother empty states

### Expected outcome

The app should feel more intentional, approachable, and maintainable.

---

## 5. Keep bot and AI work secondary

### Why this matters

Bot and AI features should support the product, not define it.

### What to build

- Keep AI as optional support infrastructure
  - explanation support
  - study assistance
  - guided reflection or review help
- Avoid building AI features before the core learning experience is strong
- Only add complexity if it clearly improves learner understanding

### Expected outcome

AI remains a useful layer in the background without pulling attention away from the curriculum.

---

## Recommended implementation sequence

### Phase 1 — Foundation experience

Focus on:
- lesson navigation
- progress visibility
- workspace usability
- clearer module flow

### Phase 2 — Content operations

Focus on:
- better content publishing workflow
- stronger content authoring support
- more direct connection between repository content and runtime experience

### Phase 3 — Onboarding and polish

Focus on:
- first-run onboarding
- contributor setup improvements
- user-facing clarity and product readiness

### Phase 4 — Optional enhancement layer

Focus on:
- AI explanations or educational support
- richer learner assistance
- advanced personalization only if it improves learning

---

## Suggested success criteria

A successful implementation should make the following true:

- a new user can understand the product within minutes,
- lessons flow naturally from one to the next,
- progress is visible and motivating,
- contributors can add curriculum content with less friction,
- and the app feels like a polished learning product rather than a prototype.

---

## Final recommendation

If you want the highest-impact next step, build the lesson delivery experience first. That is the most central part of the product and the easiest place to create immediate value for users.

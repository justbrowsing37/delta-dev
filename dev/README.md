# dev/ — Waitlist / Public Marketing Site

This folder is the **waitlist planet** — the public-facing marketing site that was previously on a separate repository.

## Intent

The external waitlist repo is being shut down. All waitlist site files live here going forward.
This folder deploys independently (e.g. Cloudflare Pages, Netlify, or Vercel) pointing at this directory.

## Files

Waitlist files committed from the external repo live here. The entrypoint is `index.html`.

## Structure

```
dev/
  index.html       — waitlist landing page
  style.css        — (if separate from inline styles)
  assets/          — any images, fonts, or static assets
  README.md        — this file
```

## Deploy

Point your static host's build root at `dev/`. No build step required — pure HTML/CSS/JS.

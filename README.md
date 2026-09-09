# aap-web

The All About Pools website. Static site, deployed from this repo. Replaces the
Wix site at allaboutpools.co.za.

## Why this setup

Wix has no content API for a template site, so every change meant "Jarvis drafts,
Anton pastes". This repo + a static host (Cloudflare Pages or Netlify) means a
push goes live in under a minute, no paste step. Free hosting, faster pages
(better for Google), full control of every meta tag and redirect.

## Stack

- **Plain static HTML/CSS right now** - no build step. Any static host serves the
  repo as-is.
- Move to a static generator (Eleventy or Astro) once there's more than a couple
  of pages, so the nav/header/footer aren't copy-pasted across files.
- Forms: the host's built-in form handler (Netlify Forms / Cloudflare) forwarding
  to Anton's inbox, or Formspree. Wire an autoresponder later for the lead magnet.

## Status (2026-09-09)

- `index.html` = homepage redesign mock-up v1 (built 6 Sep, self-contained).
  Images are still hot-linked from Wix's CDN - **must** be pulled local / onto a
  media host before launch.
- Not deployed yet. Not connected to a host. Domain still on Wix.

## To launch (with Anton)

1. He signs into Cloudflare Pages or Netlify and connects this repo (one-time,
   needs his login). Auto-deploy on push to `main`.
2. Finish the homepage: real trust-bar numbers (years trading, pools completed,
   guarantee terms), real reviews, final copy.
3. Build the rest: 3 service pages, about, contact, cleaned-up blog.
4. Localise the images (off Wix CDN).
5. Wire the contact form + email capture.
6. 301 redirects from the old Wix URLs so rankings carry over.
7. Repoint `allaboutpools.co.za` DNS from Wix to the host. Propagation ~1 hr.

Full audit + redesign notes: `jarvis-vault/02 - All About Pools/Website - audit and redesign.md`.

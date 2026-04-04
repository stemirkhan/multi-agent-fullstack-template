---
name: nuxt
description: Use when implementing Nuxt pages, layouts, route middleware, data loading, server/client boundaries, or app-level conventions in the frontend.
---

# Nuxt

Use this skill when a change depends on Nuxt-specific structure or runtime behavior.

## Responsibilities

- Keep pages and layouts thin and push reusable logic into composables and shared modules.
- Use Nuxt routing, async data, and runtime boundaries deliberately.
- Preserve SSR, hydration, and environment-specific correctness.

## Rules

- Keep page files focused on composition, params, and page-level concerns.
- Make server-only and client-only behavior explicit.
- Use useFetch or useAsyncData through stable, intention-revealing seams.
- Avoid mixing transport logic into presentation-only components.
- Keep route middleware and plugins narrow and purposeful.

## Verification

- Check route params, navigation, and middleware behavior.
- Check hydration-sensitive UI and auth-sensitive flows.
- Check loading, error, and refresh behavior for changed async-data seams.

## Handoff

Return:
- pages, layouts, middleware, or plugins changed
- data-loading seams touched
- server or client boundary notes
- tests run

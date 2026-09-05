---
name: antislop
description: Use when creating or refining user-facing UI and product copy, or when explicitly auditing them for generic AI patterns. Not for backend behavior or comment-only cleanup.
license: MIT
metadata:
  upstream: https://github.com/miqdadbadjuber/anti-slop
  upstream-commit: 44be68777e96d53d113edad33dbc4ab380f5d054
  upstream-path: skills/antislop/SKILL.md
  upstream-sha256: f45fb379c8dc19af543e90b94e2c860108fbd4fc523faa33a6c08d17bd33def7
---

# Antislop Core

For a matching task, read [the upstream core](references/upstream-core.md).
It contains the full design and copy filter, rule tiers, and delivery checks.
This integration contract governs how that bundled reference applies here.

## Integration Contract

- Only the core is installed. Skip the upstream First-Run Install Wizard.
  References to additional antislop skills describe optional upstream modules;
  do not install, require, or look for them, and do not rewrite project instructions.
- Load this skill for the current UI or product-copy task only. The upstream
  "Load always" description is not a session-wide loading instruction here.
- Honor a mode already chosen by the user. Otherwise use DURING for authorized
  creation or refinement and AFTER for an audit. Do not repeat a mode question
  when the task or previous instructions already determine the answer.
- User instructions, project instructions, and the existing design system take
  precedence over stylistic preferences in the reference. Existing design tokens,
  components, and brand guidance supply design direction; a separate design file
  is not required. Keep checks within the requested UI or copy scope.
- Keep audits read-only unless fixes are authorized. An AFTER audit may finish
  with FAIL findings; report them without applying changes. Do not demand
  approval of individual finding numbers when the user has already authorized
  the relevant fixes.
- Use the upstream delivery checks that apply to the changed output. Record
  actual evidence and any unverified items; never claim an unperformed browser
  check passed. Respect the host agent's reporting contract. Return audit findings
  in the response unless the user or project requests a report file.

## Accessibility Correction

In upstream R-25, the large-text threshold is mistakenly written as 18px.
Use 18pt (24 CSS px) for regular text, or 14pt (about 18.67 CSS px) for bold text:
large text requires 3:1 contrast, ordinary text 4.5:1.
See [WCAG contrast guidance](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html).

The reference is an unchanged copy of the pinned upstream file. This entrypoint
provides the scoped loading, completed-install handling, authorization and review
integration, and accessibility correction. Preserve the bundled [MIT license](LICENSE)
when redistributing it.

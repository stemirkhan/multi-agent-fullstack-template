---
name: web-design-guidelines
description: Use when building frontend UI with an existing design system, preserving accessibility, hierarchy, spacing, and visual coherence without inventing a new component system.
---

# Web Design Guidelines

Use this skill when the task is primarily visual, interaction-heavy, or presentation-focused.

## Responsibilities

- Reuse the existing design system before inventing new primitives.
- Preserve accessibility, visual hierarchy, and responsive behavior.
- Keep styling decisions coherent across pages and components.

## Rules

- Prefer extending existing components before creating new base primitives.
- Keep layout concerns outside small leaf components when possible.
- Preserve focus states, keyboard access, and readable contrast.
- Reuse design tokens, spacing, and typography conventions already present in the project.
- Avoid one-off visual patterns that only solve one screen awkwardly.

## Verification

- Check responsive behavior at constrained widths.
- Check keyboard and focus behavior for interactive UI.
- Check loading, empty, and error states for visual coherence.

## Handoff

Return:
- components or layouts introduced or extended
- accessibility-sensitive behavior touched
- styling or visual-system notes
- tests or visual checks run

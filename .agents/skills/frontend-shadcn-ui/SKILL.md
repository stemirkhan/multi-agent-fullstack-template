---
name: frontend-shadcn-ui
description: Use when building interfaces with shadcn/ui, composing Radix-based primitives, customizing ready-made components, or preserving accessibility while styling.
---

# Frontend shadcn/ui

Use this skill when the UI should be built primarily from ready-made accessible components instead of custom primitives.

## Default Bias

- Start with existing `shadcn/ui` components.
- Compose them with project-specific wrappers only when repeated patterns appear.
- Drop to raw `Radix UI` primitives only when `shadcn/ui` does not cover the needed interaction.
- Build custom primitives last.

## Preferred Usage Order

1. Existing project component
2. Existing `shadcn/ui` component
3. Extended `shadcn/ui` composition
4. Direct `Radix UI` primitive
5. New custom primitive

## Composition Rules

- Keep layout concerns outside leaf components where possible.
- Prefer composition over prop explosions.
- Preserve keyboard navigation, focus states, aria attributes, and portal behavior when customizing overlays.
- Reuse design tokens, spacing, radius, and typography conventions already present in the project.

## Styling Rules

- Keep Tailwind class composition readable; extract repeated variants.
- Prefer `cva` or the project's existing variant pattern for size, tone, and state variants.
- Avoid one-off class soup in route files when a reusable component is warranted.
- Preserve dark mode and responsive behavior if the project already supports them.

## Forms And Data UI

- Pair `Input`, `Select`, `Textarea`, `Checkbox`, `RadioGroup`, `Popover`, `Dialog`, and related controls with typed form logic instead of ad hoc state where forms are non-trivial.
- For tables, filters, and async states, keep loading, empty, error, and success states visually coherent.
- Do not bury query or mutation calls inside presentation-only component leaves.

## Accessibility Guardrails

- Do not break trigger-content relationships for dialogs, popovers, dropdowns, or tabs.
- Keep visible labels or accessible names for actionable controls.
- Verify focus return and escape behavior for overlays.
- Do not remove focus outlines unless they are replaced with an equivalent visible state.

## When To Create A New Component

Create a reusable component when:
- the same composition appears in multiple features
- variant logic is repeated
- accessibility wiring would otherwise be duplicated

Stay local when:
- the UI is feature-specific and unlikely to repeat
- abstraction would hide simple markup without reducing risk

## Handoff

Return:
- components introduced or extended
- reused `shadcn/ui` building blocks
- accessibility-sensitive behaviors touched
- styling or variant conventions introduced
- tests or visual checks run

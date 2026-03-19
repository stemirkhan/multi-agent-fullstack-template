---
name: frontend-forms-and-validation
description: Use when building forms with React Hook Form and Zod, mapping backend validation to UI, or structuring typed form workflows in the frontend.
---

# Frontend Forms And Validation

Use this skill when user input is non-trivial and needs typed schema validation, submission flow control, and clear backend error mapping.

## Responsibilities

- Keep form state, validation, and submission behavior explicit.
- Use `React Hook Form` and `Zod` as the default stack for non-trivial forms.
- Map backend validation and conflict errors into stable field or form-level feedback.

## Default Structure

- Zod schema for form shape and client-side validation.
- React Hook Form for state and field registration.
- Submit handler owned by the feature layer or mutation hook.
- UI components composed from existing input primitives and `shadcn/ui` form patterns.

## Rules

- Define one clear source of truth for field names and schema shape.
- Keep validation messages consistent and specific.
- Do not duplicate the same validation logic across random components.
- Use field-level validation for user guidance and backend error mapping for authoritative failures.
- Keep submission side effects explicit: reset, redirect, invalidate, or stay dirty.

## Backend Error Mapping

- Distinguish field errors from form-wide errors.
- Preserve backend semantics for conflict, forbidden, and validation failures.
- Avoid reducing all backend failures to one generic toast.
- If the backend returns machine-readable codes, use them deliberately.

## UX Guidance

- Disable or guard repeated submissions when appropriate.
- Show pending state clearly.
- Preserve user input on recoverable failures.
- Keep success handling intentional: inline success, redirect, modal close, or optimistic UI.

## Verification

- Test valid and invalid submission flows.
- Test mapping of backend validation errors to fields or form-level alerts.
- Test reset and dirty-state behavior when it matters.
- Test accessibility of labels, hints, errors, and focus movement on failure.

## Handoff

Return:
- schemas and forms added or changed
- field and backend error mapping notes
- submission flow behavior
- success and failure UX notes
- tests run

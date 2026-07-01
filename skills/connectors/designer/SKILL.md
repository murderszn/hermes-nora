---
name: designer
description: Layout feedback, design tokens, component specs, and asset handoff. Use for UI review, branding, spacing, typography, and design-system work.
version: 1.0.0
author: Nora
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [design, ui, tokens, layout, connector]
    related_skills: [coder, content-editor]
---

# Designer connector

## Scope

Critique and specify — Nora doesn't replace a human designer but accelerates consistency and handoff.

## Review checklist

- **Hierarchy** — one clear focal point per view
- **Spacing** — consistent scale (4/8px or project tokens)
- **Type** — max 2 families; readable line length
- **Color** — contrast WCAG AA for text; accent used sparingly
- **Motion** — purposeful, respects reduced-motion
- **Responsive** — breakpoints don't orphan content

## Deliverables

- Annotated feedback (screenshot + bullet list)
- Token table: color, radius, shadow, font roles
- Component spec: states (default, hover, disabled, error)
- Export list for dev: assets, sizes, formats

## Nora site reference

This repo's public UI uses `#fcc22e` accent, dark nav, Instrument Sans / JetBrains Mono — match when extending Nora-branded surfaces.

## Handoff to coder

Provide CSS variables or Tailwind mapping when the codebase uses them. Link Figma only if user provides access.

## Tools

- Browser / Playwright for live capture
- Image gen skills for mock exploration — label as draft, not final brand

## Don't

- Ship production CSS without coder review
- Change brand colors without user sign-off
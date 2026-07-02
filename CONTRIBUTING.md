# Contributing to Nora

Nora is MIT-licensed and community-shaped. The best contributions are the ones
that reflect what you actually deploy, not what looks good on a roadmap slide.

## Before you open an issue

1. Search open and closed issues — this repo moves fast and your ask may already
   be tracked.
2. For tooling problems, attach the output of `./scripts/doctor.sh` (or
   `doctor.ps1` on Windows) so we can see your environment.
3. Separate "I can't install" from "I think this design is wrong." Both matter,
   but they need different responses.

## Pull requests

Smaller is better. One connector, one skill, one copy change — that's a good PR.

1. Fork + branch from `main`.
2. If you touch a skill, test it by pointing a local Hermes `skills:` entry at
   your clone and running the affected workflow or a dry-run.
3. Don't commit secrets or live local config (`auth.json`, `.env`, etc.). Use
   `.env.example` and `.defaults.yaml` for fixtures.
4. Update the README or docs if the user-facing surface changed — a new connector
   should appear in the skills list and roadmap connector grid.
5. Open the PR with a one-line summary and a sentence about what you tested.

We merge PRs that are honest about what they touch and leave the repo cleaner
than they found it.

## Style

- Match the tone already in the repo: short sentences, plain language, no filler.
- Skills follow the existing `SKILL.md` template with frontmatter `name`,
  `description`, `version`, `author`, `license`, `platforms`, and `metadata`.
- Website copy lives in `website/` and should feel like the same voice as the
  persona in `hermes/SOUL.md`.

## License

By contributing you agree your work is MIT-licensed, the same as the rest of the repo.

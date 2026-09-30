---
name: ai-web-pet
description: Guide a web pet from an idea, an existing character image, or a real pet photo through character approval, external or native image generation, action design, transparent frame import, a minimal web player, and separate technical, visual, and user review.
---

# AI Web Pet

Build a user's intended character into a reviewable web pet. This v0 accepts externally generated, already transparent frames. It provides no generator API, automatic matting, automatic anchors, skeleton, desktop installer or automatic aesthetic approval.

## Start or resume

Read [creation.md](references/creation.md) for a new character; inspect existing character JSON and approvals when resuming. Preserve established user choices. Ask only for information blocking the next step; prefer concise choices with free text available.

Initialize an empty local project with `python scripts/pet.py init PATH`. Fill the generated templates; never mark their pending approvals as approved without explicit user evidence. Template JSON is the editing authority; render its human-readable Markdown with `python scripts/pet.py views PATH` before review.

The route is Input → Pet Brief → Character Bible → Character Lock → Reference Sheet / Generation Handoff → Action Brief → clips / manifest → Web Player → QA.

- Idea: interview missing identity/use/style fields, create a brief and Bible, request design candidates, obtain approval of one canonical image.
- Existing image: inspect the original, extract observed invariants, ask which must stay and which may change, then create Bible and Lock. An image alone is not an approved lock.
- Real pet: record recognizable markings and anatomy, agree stylization, review a candidate, then lock it. Do not invent hidden markings as observed facts.

Read [generation.md](references/generation.md) when requesting or receiving art. Use available native generation only when appropriate to the user's choice; otherwise write a handoff and wait for original files. No API access is required. Keep pending work resumable.

## Actions and playback

Only proceed to action production after the brief and character lock are explicitly approved. Read [actions.md](references/actions.md) for process, topology, contact and continuity requirements. Use the supplied Action Brief template. Keep existing accepted sources and revisions.

Read [format.md](references/format.md) before authoring clips. Import full-body RGBA PNG frames; record anchors manually. The source of truth is project.json plus character documents and actions/*/clip.json. Build creates an immutable content-addressed runtime manifest and browser preview; it never edits source frames or manufactures in-betweens.

```sh
python scripts/pet.py validate PATH
python scripts/pet.py build PATH
python -m http.server 8000 --directory PATH
```

Open the returned preview path through the local HTTP server. Play each complete action once, then test waiting and safe exit. The player supports only explicit actions and enter/loop/exit; business integration stays with the host.

## Review and finish

Read [qa.md](references/qa.md). Technical pass, visual review, and user acceptance are separate records bound to a build ID. A successful build is a candidate, never a release. Use the supplied QA template; do not populate approvals from silence. Display full motion at intended speed on dark/light/checker backgrounds and at 80–160 CSS px.

Report unresolved contact/anatomy/continuity defects. Repair the smallest coherent action rather than redesigning the character. This skill does not publish or package a product; user acceptance and any later integration/release require concrete evidence.

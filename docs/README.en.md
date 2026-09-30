# AI Web Pet — local v0 development candidate

Guide Idea / Existing Image / Real Pet Photo into an approved character and a minimal web pet. Original implementation; no legacy pet pipeline copied. Initial v0.1.0 candidate: software-tested; real second-character recording remains pending and is not a prerequisite for the first code release.

Install the folder in your Agent's skill directory, then invoke `$ai-web-pet`. Python 3.10+ and Pillow are required for local frame validation/build. The browser player uses native ES modules with no JS dependencies. Install Pillow in your own virtual environment (`python -m pip install Pillow`); record the installed version for reproducibility. No model API or paid generation service is bundled.

Run `python scripts/pet.py init /path/to/new-project`, fill the character templates with the Agent, review generated Markdown and explicitly approve the brief/lock. Use original external or native generation, supply already transparent RGBA frames, author clips per references/format.md, then validate/build. Serve the project through `python -m http.server 8000 --directory /path/to/project` and open the returned preview path under that server. file:// is not supported.

The runtime manifest is generated from source clips and character records. All build output goes to immutable preview/<hash> directories. This is a review build, not a delivery ZIP, automatic anchor system, behavior platform, or desktop installer.

Integration: copy a reviewed preview directory as static site resources; `import {loadPet} from './player.mjs'; const pet = await loadPet({element: document.querySelector('#pet'), manifest:'./manifest.json'});`. Call play(action,{once:true}), play(action) for a waitable family, requestStop() for safe exit, destroy() on unmount. Host business events are not mapped automatically. Publishing remains a separate user decision.

Tests: `python -m unittest discover -s tests -p 'test_*.py'`; `node --test tests/player.test.mjs`. Fixtures are synthetic geometry for software tests, not a finished pet or a visual acceptance example.

Known limits: source frames must already be aligned and transparent; one manual anchor per clip; no strips/WebP export, offline file-URL demo, automatic art review, lifecycle signing or evidence authentication. JSON approval evidence is supplied by the Agent/user and must be reviewed honestly. Second real character and user visual acceptance are still pending. Source and accompanying documentation are licensed under MIT; see ../LICENSE. Character assets, brand marks and user-supplied materials are not granted rights by this code license. Pillow is an externally installed dependency with its own license; see PROVENANCE.md.

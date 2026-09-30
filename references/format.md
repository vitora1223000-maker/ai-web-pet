# Executable v0 format (schema_version 0.1)

This deliberately smaller contract supersedes optional draft fields for the minimum implementation. project.json defines pet_id, host {width,height,anchor:{x,y}}, ariaLabel, default_action and actions. Every action is either {single:clipID} or {enter:clipID,loop:clipID,exit:clipID}. No behavior probabilities, business events or direction tables are implemented.

actions/<clipID>/clip.json defines id, lock_version, width, height, anchor {x,y}, frames [{id,path}], sequence [frameID], durationsMs [positive integer], reduced_motion_frame. All frames in one clip share size and anchor; clips may differ. Paths are relative to project root, must remain inside it, no absolute paths or traversal. Frame IDs are distinct; sequence may repeat them. Exactly one duration per sequence item. PNGs must be RGBA, contain both transparent and visible pixels, with at least a one-pixel clear border.

Example clip (fill with your own original RGBA files):

```json
{"id":"idle","lock_version":1,"width":240,"height":320,"anchor":{"x":120,"y":304},"frames":[{"id":"a","path":"actions/idle/frames/000.png"}],"sequence":["a","a"],"durationsMs":[300,500],"reduced_motion_frame":"a"}
```

Coordinates are pixels, origin top-left. Player places the frame at host.anchor minus clip.anchor. A scaled outer viewport preserves these coordinates. No auto anchor or per-frame fitting occurs. Export already aligned frames before import; alpha processing stays external.

Character approval: Brief revision is a positive integer with approval {decision:approved,revision:<same>,approved_at,evidence_ref,payload_sha256}. Lock approval uses version in that revision field. Run views to display the payload hash excluding approval; only after explicit user confirmation record that hash with evidence. Changed content fails validation. Lock bible_sha256 must match the Bible Content hash displayed by views; changes to the Bible invalidate the bound lock. Lock canonical is {path,sha256}; compute SHA-256 from original bytes. Copy Bible body_topology into Lock only after identity review. Editing a confirmed record requires a new revision and fresh evidence; CLI does not create approval records.

build generates preview/<content-hash>/manifest.json and copies referenced PNGs plus player/index. Runtime paths are relative to manifest URL; no JSON+JS duplication, no external resources. Build hash covers project, character records, clips, frame bytes and player/demo code. Existing builds are not overwritten. This is a local review build, not a release package or installer.

Generated browser manifest: schema_version,build_id,pet_id,ariaLabel,host,default_action,actions,clips. Clips preserve dimensions,anchor,sequence,durationsMs,fallback and frame ID→relative path mapping. Player supports loadPet({element,manifest}), play(action,{once}), requestStop(), destroy(), and state/complete events. Single actions play once (default idle loops); three-part actions loop until stopped or once:true. New play cancels previous callbacks. Reduced motion displays fallback; requestStop returns to static idle.

# Action performance

An action has preparation, initiation or weight transfer, main action/contact, reaction/hold, and recovery. Not every action needs each beat, but transitions must be physically drawn. A start and end image do not demonstrate a turn or roll. Slowing endpoints cannot replace missing movement.

Before art, name moving body part IDs, support points, visible contact target, occluded parts, gaze, gravity/lag of attachments, camera and baseline (or a space reference for flight). Check against the approved topology, never assume four limbs. The moving limb should actually touch its intended target. Not-applicable contact requires an explanation.

Use coherent action sequences with directly drawn intermediate poses; no optical flow, dissolves or morphing claimed as new animation. Repeated drawings are legitimate holds, not additional unique art. Keep grounded contacts stable; manual anchor coordinates must follow physical support, not per-frame bounding-box centering.

Waitable actions use enter, loop, exit clips. Once-actions can use a single clip. In v0 stop waits until the current clip completes, plays exit, then returns to default idle. Reverse playback is not a general replacement for an exit: gravity, contacts and gait must be reviewed explicitly.

Review complete playback once at intended timing. If a pose or seam fails, replace the smallest coherent source unit. Never overwrite accepted character or action files with a candidate.

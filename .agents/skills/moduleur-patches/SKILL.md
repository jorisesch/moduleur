---
name: moduleur-patches
description: Create, document, render, and maintain Shmoergh Moduleur synthesizer patches as compact editable definitions and vector overlays on the official patch sheet, with a consistent one-page description and explicit Brain firmware and mode.
---

# Moduleur patches

Use the repository's patch format and renderer; do not draw a new instrument or
embed a screenshot as the editable patch. Read [the format](references/format.md)
and [the panel map](references/panel.json) before creating or changing a patch.
Locate the repository's `patches/` and `downloads/` folders from the user's project;
when this skill is copied elsewhere, pass the project and background paths explicitly.

## Capture a reproducible patch

- Establish the intended sound, playing/clock source, external gear, and hardware
  layout. Use Le Controlleur as the usual suggestion, but explicitly record the
  actual firmware name, version (or `unknown`), and mode. Never assume which
  firmware is installed or silently flash it. Le Controlleur requires `Sequencer`
  or `MIDI to CV` as the mode; record tempo/clock or MIDI channel and output mapping.
- Include every physical cable, including MIDI, clock, output monitoring, and
  external devices. Include every active internal normalled connection as a
  distinct dashed connection. An input cannot simultaneously be physically patched
  and normalled. Never invent normalled wiring: check the official docs/schematics
  for the hardware revision. The upstream default-patch schematic contains an
  outdated-wiring warning; don't treat it as sole authority.
- Distinguish signal roles in the legend: `PITCH CV` for musical pitch, `MOD CV`
  for continuous parameter modulation, and `GATE/TRIG` for note on/off, triggers,
  and clocks. Pitch and gate are also control voltages; these labels describe
  function, not different cable types. Classify each connection by its use in
  the patch. Keep audio and MIDI distinct too; see the format reference for IDs.
- Every control on a used module must have a position or an explicit reason it is
  irrelevant. Mark critical controls, draw their knob pointers/slider handles,
  and give readable values. Percent means physical travel, not Hz or milliseconds.
  Label analog settings as starting points unless measured on the user's unit.
- Preserve the official patch sheet's artwork and printed labels, except for the
  user's requested removal of `HOG` from the lower-right footer in generated
  overlays. Keep the downloaded source intact. Do not infer
  control types or claim the sheet is outdated from its symbols or naming alone.
  This owner confirmed three knobs above two buttons beside MIDI In: use the
  `three-knobs-two-buttons` profile here. Firmware identifiers may differ from
  printed labels; explain firmware terminology on page one instead of relabeling
  the background. For another owner, confirm the physical layout or keep Brain
  values in the settings inset. Include firmware parameter values and setup
  steps even when resting knob positions are not meaningful.
- For unknown sound or hardware facts, ask a focused question or label the patch
  as an untested draft. Do not claim to have auditioned a patch from rendering it.
- Keep revision and audition status as internal definition metadata. Do not print
  slugs, revision tags, or audition-status labels on either patch-sheet page.
- Do not create a general Notes section or include personal hardware history.
  Put only reproducibility-critical constraints in Setup.

## Author and render

Store each patch as `patches/<slug>/patch.json`. If the repository includes
`patches/midi-pluck/patch.json`, use it as a format example; otherwise author the
required fields from the format reference. Change metadata, the full connection
list, controls, and description together.
Keep connection IDs stable when editing so printed references remain useful.

Install the one-time Python dependencies from `scripts/requirements.txt`, then
use `scripts/render_patch.py` to generate a transparent SVG and PDF overlay and a two-page PDF: one-page
brief first, annotated official sheet second. The renderer validates input and
pins the official background hash; it refuses a different template instead of
silently misaligning connections. Excess front-page content is an error, not an
invitation to shrink the text beyond readability or add extra description pages.

The renderer supports `classic`, `editorial`, `minimal`, `archive`, and
`industrial` through `--style`. Use the default `minimal` style for the checked-in `patch.pdf`.
Alternate styles write `patch-STYLE.pdf`; treat them as local previews unless
the user explicitly changes the repository default. Styling may change the
description page, but must not alter patch data, omit connections or controls,
or move coordinates on the annotated official panel.

Render the completed PDF to images using an available PDF renderer and inspect
both pages. Check cable endpoints, intersections, labels, control pointers,
external leads, normalled paths, and every front-page section. Route crowded
cables using `via` points and move labels using `label_at`; do not omit connections
for aesthetics. Run the validation command after edits. Measure output sizes.

## Maintain and share

The JSON is authoritative; regenerate outputs after changes. Do not hand-edit
only the generated PDF. Preserve original firmware/version and patch intent
unless the user asks to change them. Keep downloaded backgrounds and firmware
under ignored `downloads/`; the skill contains coordinates and a checksum, not
copies of upstream assets. Respect the repository's stated artifact policy.
Report what was verified structurally/visually and what still needs listening
on the instrument. Creation does not authorize committing or publishing.

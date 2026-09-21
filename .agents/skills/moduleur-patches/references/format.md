# Patch format v1

A patch is a UTF-8 JSON file, conventionally `patches/<slug>/patch.json`.
When present, `patches/midi-pluck/patch.json` demonstrates the complete format.

Required fields:

- `schema_version`: `1`.
- `id`, `title`, `revision`, `status` (`untested` or `auditioned`), `summary`.
  The renderer uses revision and status as internal provenance and does not print
  them on the finished patch sheet.
- `brain`: `firmware`, `version`, `mode`, `layout`, `settings` (list of strings).
  `layout` is `three-knobs-two-buttons` or `settings-inset`. The former places
  firmware pot X/Y/Z indicators on the confirmed upper three knobs, left to right.
  Original artwork and printed labels are preserved. Explain firmware naming on
  page one; do not treat terminology differences as errors in the official sheet.
  Le Controlleur modes are exactly `Sequencer` and `MIDI to CV`. If unused,
  record firmware/version as `not used` and mode `not used` explicitly.
- `description`: `sound`, `setup`, `play`, and `variations` (lists of short
  strings). Put essential operating constraints in `setup`; do not add a general
  notes section or personal hardware history.
- `external`: map of endpoint IDs to `{label, direction, x, y}`. IDs start with
  `external.`; directions `in` or `out` are relative to the external device.
  Coordinates are PDF points from the **top left** of the background, as in
  `panel.json`. Put these in the top or bottom empty margin, not over controls.
- `connections`: list of `{id, from, to, kind, signal, via?, label_at?}`.
  `kind`: `cable` or `normal`; `signal`: `audio`, `pitch`, `cv`, `gate`, `midi`.
  Port IDs come from `panel.json` or `external`. A source must be an output and a
  destination an input. Each destination appears once. External MIDI and monitor
  leads must be included. `via` is an optional list of `[x,y]` routing points;
  `label_at` optionally positions the numbered label. Junctions only occur at
  named endpoints; crossing lines never imply a connection. Multiple physical
  cables from one source require a declared external splitter/multiple rather
  than silently assuming stackable leads. A normal plus a physical output cable
  is allowed. `normal` routes are explicit assertions about active internal
  wiring, not automatically inferred from the template.
- `controls`: map of panel control IDs to either
  `{position: 0..1, value: "readable setting", critical: true/false}` or
  `{irrelevant: "specific reason this control does not affect the patch"}`.
  `position` is physical travel: 0 fully counterclockwise/bottom, 1 clockwise/top.
  The VCO waveform selector instead takes `{value: "TRI"|"SAW"|"SQR", critical: true}`.
  Every control of a module touched by any connection must be covered. Critical
  pointers/handles are heavier; all provided positions are displayed. Normal
  firmware controls may be configuration-only: explain why rather than assigning
  an invented knob angle. When Brain layout is unknown, use `settings-inset` and
  put parameter values in `brain.settings`; don't invent physical positions.
- `normalled_policy`: a concise statement of the active default wiring and how
  unused default paths are silenced or overridden. Do not claim the renderer
  can infer hardware wiring. Include internal VCA envelope connections.
- `sources`: list of human-readable source strings (URLs or repository paths).

The renderer rejects unknown keys/IDs, out-of-bounds coordinates, duplicate
inputs/IDs, output-to-output wiring, missing controls/firmware metadata, template
hash mismatch, and description-page overflow. These checks do not simulate
analog electronics or prove that a patch sounds good.

Outputs beside the JSON:

- `overlay.svg`: transparent vector paths, control marks, and labels at the exact
  template dimensions; no embedded background.
- `overlay.pdf`: one transparent page for merging over the official PDF.
- `patch.pdf`: description page first, annotated official sheet second.

All three outputs and the JSON may be committed. The downloaded template remains
ignored under `downloads/`. Attribution to Shmoergh stays visible in the output.

## Signal roles and footer treatment

Colors describe the connection's musical function, not incompatible cable types:
`pitch` = PITCH CV (note control, normally 1 V/oct at the VCO pitch input),
`cv` = MOD CV (continuous modulation, such as an envelope or LFO), and
`gate` = GATE/TRIG (timing, note on/off, triggers, or clocks). Pitch and gate are
also control voltages in the broad sense. Classify a signal by its use in the
patch: for example, a square LFO triggering an envelope is `gate`. Keep these
roles distinct for readability without suggesting that they require different
patch cables. Color alone does not establish voltage compatibility.

Generated overlays cover only the `HOG` word in the lower-right footer as requested
by the owner. The downloaded background remains unchanged; `MODULEUR`, the
remaining subtitle, and Shmoergh branding are preserved.

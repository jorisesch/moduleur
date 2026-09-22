# Moduleur patches

Each patch has one editable JSON definition and three small generated artifacts:

```text
patches/<name>/
├── patch.json       # Authoritative description, firmware, cables, and controls
├── overlay.svg      # Transparent vector overlay, without the official background
├── overlay.pdf      # One-page transparent PDF overlay, at the original sheet size
└── patch.pdf        # One-page description first; annotated official sheet second
```

Definitions, overlays, and finished PDFs are intended for Git. The official blank
sheet and firmware downloads remain ignored under `downloads/`. The example's
combined PDF is about 127 KB; its PDF overlay is about 6 KB and SVG about 14.5 KB.
There is no need for Git LFS at these sizes. Review sizes again if adding images.

## Use with Codex

Open this repository (`moduleur/`) as the Codex project. The shared skill lives at
[`.agents/skills/moduleur-patches/SKILL.md`](../.agents/skills/moduleur-patches/SKILL.md).
Repository skills are discovered by Codex when working inside the repository;
reopen the project/task if a newly added skill has not appeared yet. You can also
refer to its `SKILL.md` directly. [Official skill discovery documentation](https://learn.chatgpt.com/docs/build-skills).

Example request:

> Use $moduleur-patches to create a slow evolving bass patch using Le Controlleur
> in Sequencer mode. Show every cable and active normal, all critical controls,
> and put the firmware settings and performance guidance on the first page.

For maintenance, ask Codex to update an existing patch's definition and regenerate
its artifacts. Keep connection IDs stable where possible. Do not edit only a PDF.

To reuse outside this repository, copy the whole `moduleur-patches` skill folder
into the other project's `.agents/skills/`. Its renderer, map, and format reference
travel with it. Put definitions in that project's `patches/` directory and supply
`--background /path/to/moduleur-patch-sheet.pdf` to the skill's renderer if needed.
No personal Codex configuration or private account notes are included here.

## Build in one command

One-time setup: install Python 3.10+ and the two PDF packages. A virtual environment
is recommended. From the repository root:

```sh
python -m venv .venv
# macOS/Linux:
. .venv/bin/activate
# Windows PowerShell, instead:
# .venv\Scripts\Activate.ps1
python -m pip install -r patches/requirements.txt
```

On systems with only `python3`, use that command to create the environment. On
Windows, `py -3 -m venv .venv` is another option. Download the official background
once with `./downloads/refresh.sh` (Git Bash/WSL on Windows), or save the official
[patch-sheet PDF](https://www.shmoergh.com/content/files/2026/02/moduleur-patch-sheet.pdf)
to `downloads/patchsheets/moduleur-patch-sheet.pdf`.

Then build a patch:

```sh
python patches/build.py autonomous-argumentative
```

Run `python patches/build.py` to rebuild all patches. Use
`python patches/build.py alien-thunder --validate` to check a definition without
installing the PDF packages. No network access is needed once the background and
packages are present. Native Windows Python can render; no shell is required for
this build step. The download refresher remains independent and Python-free.

The default `minimal` build is the only finished PDF intended for Git. To preview another
first-page treatment, use `python patches/build.py alien-thunder --style editorial`.
Supported styles are `classic`, `editorial`, `minimal`, `archive`, and
`industrial`. Alternate builds are written as `patch-STYLE.pdf` and ignored by
Git; the annotated panel remains consistent across styles.

## Author a patch

Use [Autonomous Argumentative](autonomous-argumentative/patch.json) or
[Alien Thunder](alien-thunder/patch.json) as a format example. Copy one directory
to a new slug, remove its generated files, edit `patch.json`, then build the new
slug. Change the `id`, title, status, intent, firmware, mode, connection list,
controls, and description together. Remove inherited settings or claims that do
not apply to the new patch, and begin with `status` set to `untested`.

The [format reference](../.agents/skills/moduleur-patches/references/format.md)
describes all fields. Stable port/control IDs and top-left PDF-point coordinates
live in [panel.json](../.agents/skills/moduleur-patches/references/panel.json).
Connection paths can include explicit waypoints to avoid labels and knobs.

Every active physical cable and internal normal must be declared. Physical cables
are solid; normalled routes are dashed. Cable IDs match the first-page list.
The legend distinguishes **PITCH CV**, **MOD CV**, and **GATE/TRIG** by their role:
note pitch, continuous modulation, and timing/on-off events. Pitch and gate are
also control voltages; these are functional labels, not different cable types.
Crossings are not junctions. An input cannot be both patched and normalled.
If an output must feed two physical cables, explicitly include the splitter or
multiple instead of assuming one exists.

Every control on a used module needs a position or an explicit explanation of
why it does not matter. Critical controls get prominent orange indicators and
are listed on page one. Slider percentages describe bottom-to-top travel; knob
percentages describe counterclockwise-to-clockwise travel. They do not imply
calibrated frequency, milliseconds, or voltage. Use measured values when available.

## Brain hardware and firmware

Page one always identifies firmware, version, mode, layout, and operational
settings. For Le Controlleur the mode must be `Sequencer` or `MIDI to CV`.
Record MIDI channel/output mapping or clock/tempo/sequence settings, plus setup
steps. A firmware target is not a claim about what is currently installed.

The official patch sheet retains its symbols and printed control labels.
Generated sheets hide only `HOG` in the lower-right footer; the downloaded
original is untouched. The confirmed hardware layout has **three knobs above two
buttons beside MIDI In**. The `three-knobs-two-buttons` profile places firmware pot X/Y/Z
indicators on those upper knobs, left to right. Firmware terminology is explained
on page one rather than replacing the sheet's labels. Different naming does not
mean the drawing is outdated or incorrect.

If hardware is uncertain, use `settings-inset` and state firmware values on page
one rather than guessing knob geometry. The renderer does not yet offer a
verified physical map for other Brain layouts.

In MIDI-to-CV mode the knob positions may only matter while configuring stored
settings. The example explicitly states this instead of implying that arbitrary
resting knob angles reproduce those settings.

## Review, validation, and sharing

Rendering proves layout and structural consistency, not sound quality or physical
compatibility. Open both finished pages before committing. Check every cable
endpoint, control pointer, default connection, firmware setting, and external
lead. Audition a new patch on the instrument before changing `status` to
`auditioned`.

The renderer rejects invalid port directions, duplicate input connections,
missing controls, invalid modes, and front-page overflow. It pins the official
background by SHA-256 so a changed drawing cannot silently shift every overlay.
If Shmoergh replaces the PDF, inspect the new layout and update the panel map and
hash together. Keep source attribution visible; the background is Shmoergh's
work and the description and overlay are community-authored.

The finished PDF preserves the official page dimensions (about 272 x 336 mm).
Use your print dialog's fit-to-page option for A4/Letter. To merge an overlay
independently, use the original PDF dimensions and align at the top-left with no
extra scaling. `patch.pdf` already contains the correctly merged sheet.

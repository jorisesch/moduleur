# Shmoergh Moduleur patches

> Playable patches, precise wiring diagrams, and a reusable Codex authoring skill
> for the [Shmoergh Moduleur](https://www.shmoergh.com/moduleur/).

Each patch pairs a concise performance guide with an annotated official panel.
The repository also contains the tools needed to author more patches and preserve
local copies of Shmoergh's firmware, patch sheets, and source repositories.

**[Open Alien Thunder](patches/alien-thunder/patch.pdf)** ·
**[Open Autonomous Argumentative](patches/autonomous-argumentative/patch.pdf)** ·
**[Use the patch skill](.agents/skills/moduleur-patches/SKILL.md)** ·
**[Refresh downloads](downloads/README.md)** ·
**[Refresh source](upstream/README.md)**

## Included patch

### [Alien Thunder](patches/alien-thunder/patch.pdf)

A noise impact over a low metallic rumble, shaped into distant, otherworldly
thunder. The finished PDF opens with performance and setup guidance, followed by
the complete annotated patch sheet.

The [patch directory](patches/alien-thunder/) contains its editable JSON
definition, vector overlay, PDF overlay, and finished two-page PDF.

### [Autonomous Argumentative](patches/autonomous-argumentative/patch.pdf)

A self-running conversation of bright chirps, stepped whistles, and nervous
pitch warbles. Le Controlleur supplies pitch, filter movement, irregular timing,
and short gates while the Moduleur's built-in audio path carries the voice.

## Patch-authoring skill

The repository-scoped [Moduleur patch skill](.agents/skills/moduleur-patches/SKILL.md)
packages the authoring workflow, format reference, panel map, renderer, and Python
requirements. Codex discovers it automatically while working in this repository.

The skill records every active cable and internal normal, every critical control
position, and the Brain firmware and mode. It generates a compact vector overlay
and a two-page PDF using the minimal style by default. Additional presentation
styles are available through the renderer's `--style` option.

## At a glance

| Path | Purpose |
| --- | --- |
| [`patches/`](patches/) | Patch definitions, overlays, and finished PDFs |
| [`.agents/skills/moduleur-patches/`](.agents/skills/moduleur-patches/) | Shared patch-authoring skill |
| [`downloads/`](downloads/) | Local firmware and official patch sheets |
| [`upstream/`](upstream/) | Local clones of official source repositories |

## Local Shmoergh resources

Download the currently linked firmware and patch sheets, or verify the existing
collection:

```sh
./downloads/refresh.sh
./downloads/refresh.sh --verify
```

See [downloads/README.md](downloads/README.md) for supported platforms, source
URLs, preservation behavior, and recovery details. Existing files are retained
when the Shmoergh site is unavailable.

Official source repositories can be refreshed with:

```sh
./upstream/refresh.sh
```

See [upstream/README.md](upstream/README.md) for the repository list and refresh
behavior. The `hog` repository is intentionally excluded.

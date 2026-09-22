# Shmoergh Moduleur patches

> Playable patches, precise wiring diagrams, and a reusable Codex authoring skill
> for the [Shmoergh Moduleur](https://www.shmoergh.com/moduleur/).

The growing patch collection pairs concise performance guides with annotated
official panels. Each patch includes its editable definition, reusable vector
overlay, and finished two-page PDF.
The repository also contains the tools needed to author more patches and preserve
local copies of Shmoergh's firmware, patch sheets, and source repositories.

**[Browse patches](patches/)** ·
**[Use the patch skill](.agents/skills/moduleur-patches/SKILL.md)** ·
**[Refresh downloads](downloads/README.md)** ·
**[Refresh source](upstream/README.md)**

## Patches

| Patch | Character | Brain |
| --- | --- | --- |
| **[Alien Thunder](patches/alien-thunder/patch.pdf)** | Noise cracks over a low metallic rumble, then decays through a slowly moving resonant filter. | Le Controlleur · Sequencer |
| **[Autonomous Argumentative](patches/autonomous-argumentative/patch.pdf)** | A self-running conversation of bright chirps, stepped whistles, and nervous pitch warbles. | Le Controlleur · Sequencer |

Every patch directory contains `patch.json`, `overlay.svg`, `overlay.pdf`, and
`patch.pdf`. Open the finished PDF for setup, performance controls, complete
wiring, internal normals, and critical knob and slider positions.

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

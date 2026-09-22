#!/usr/bin/env python3
"""Build one patch by folder name, or all patches with no arguments."""
import argparse
from pathlib import Path
import runpy
import sys

ROOT = Path(__file__).resolve().parent
SCRIPT = ROOT.parent / '.agents/skills/moduleur-patches/scripts/render_patch.py'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('name', nargs='?', help='Folder name under patches/, e.g. alien-thunder')
    parser.add_argument('--validate', action='store_true', help='Check definitions without PDF dependencies')
    parser.add_argument('--style', choices=['classic','editorial','minimal','archive','industrial'],
                        default='minimal', help='Description style; alternates write patch-STYLE.pdf')
    args = parser.parse_args()
    if args.name:
        if Path(args.name).name != args.name or args.name in ('.', '..'):
            parser.error('Use a patch folder name, not a path')
        files = [ROOT / args.name / 'patch.json']
    else:
        files = sorted(ROOT.glob('*/patch.json'))
    if not files:
        parser.error('No patch definitions found')
    renderer = runpy.run_path(str(SCRIPT))
    try:
        for patch in files:
            renderer['build'](patch, ROOT.parent / 'downloads/patchsheets/moduleur-patch-sheet.pdf',
                              patch.parent, args.validate, args.style)
    except (ValueError, KeyError, TypeError, OSError, ImportError) as exc:
        sys.exit('Patch error: ' + str(exc))


if __name__ == '__main__':
    main()

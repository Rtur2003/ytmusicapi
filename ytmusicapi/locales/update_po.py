#!/usr/bin/env python3
"""Update PO files from POT template.

This script updates all translation .po files by merging changes from the base.pot template.
It replaces the functionality of update_po.sh with a pure Python implementation.

Usage:
    python update_po.py
"""

import subprocess
import sys
from pathlib import Path


def is_locale_dir(path: Path) -> bool:
    """Check if a directory is a locale directory (2-5 char name with LC_MESSAGES)."""
    if not path.is_dir():
        return False
    name_len = len(path.name)
    if not (2 <= name_len <= 5):
        return False
    return (path / "LC_MESSAGES").exists()


def update_po_file(locale_dir: Path, pot_file: Path) -> bool:
    """Update a single PO file using msgmerge.

    Args:
        locale_dir: Directory containing the locale (e.g., 'en', 'es')
        pot_file: Path to the base.pot template file

    Returns:
        True if successful, False otherwise
    """
    po_file = locale_dir / "LC_MESSAGES" / "base.po"
    if not po_file.exists():
        print(f"⚠ Skipping {locale_dir.name}: {po_file} does not exist")
        return True

    try:
        result = subprocess.run(
            [
                "msgmerge",
                "--update",
                str(po_file),
                str(pot_file),
                "--no-fuzzy-matching",
            ],
            capture_output=True,
            text=True,
            check=True,
        )
        print(f"✓ Updated {locale_dir.name}/LC_MESSAGES/base.po")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to update {locale_dir.name}: {e.stderr}", file=sys.stderr)
        return False
    except FileNotFoundError:
        print(
            "✗ Error: msgmerge command not found. Install gettext tools.",
            file=sys.stderr,
        )
        return False


def main() -> int:
    """Update all PO files from the POT template."""
    # Determine script location
    script_dir = Path(__file__).parent.resolve()
    pot_file = script_dir / "base.pot"

    if not pot_file.exists():
        print(f"✗ Error: {pot_file} not found", file=sys.stderr)
        return 1

    print(f"Updating PO files from {pot_file.name}...\n")

    # Find all locale directories
    locale_dirs = [d for d in script_dir.iterdir() if is_locale_dir(d)]

    if not locale_dirs:
        print("⚠ No locale directories found")
        return 0

    # Update each locale
    success_count = 0
    fail_count = 0

    for locale_dir in sorted(locale_dirs):
        if update_po_file(locale_dir, pot_file):
            success_count += 1
        else:
            fail_count += 1

    # Summary
    print(f"\n{'='*50}")
    print(f"✓ Updated: {success_count}")
    if fail_count > 0:
        print(f"✗ Failed: {fail_count}")
        return 1

    print("Done!")
    return 0


if __name__ == "__main__":
    sys.exit(main())

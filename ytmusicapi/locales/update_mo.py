#!/usr/bin/env python3
"""Compile PO files to MO files for translation.

This script compiles all translation .po files to binary .mo files.
It replaces the functionality of update_mo.sh with a pure Python implementation.

Usage:
    python update_mo.py
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


def compile_mo_file(locale_dir: Path) -> bool:
    """Compile a single PO file to MO format.

    Args:
        locale_dir: Directory containing the locale (e.g., 'en', 'es')

    Returns:
        True if successful, False otherwise
    """
    po_file = locale_dir / "LC_MESSAGES" / "base.po"
    mo_file = locale_dir / "LC_MESSAGES" / "base.mo"

    if not po_file.exists():
        print(f"⚠ Skipping {locale_dir.name}: {po_file} does not exist")
        return True

    try:
        result = subprocess.run(
            [
                "msgfmt",
                "-o",
                str(mo_file),
                str(po_file),
            ],
            capture_output=True,
            text=True,
            check=True,
        )
        print(f"✓ Compiled {locale_dir.name}/LC_MESSAGES/base.mo")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to compile {locale_dir.name}: {e.stderr}", file=sys.stderr)
        return False
    except FileNotFoundError:
        print(
            "✗ Error: msgfmt command not found. Install gettext tools.",
            file=sys.stderr,
        )
        return False


def main() -> int:
    """Compile all PO files to MO format."""
    # Determine script location
    script_dir = Path(__file__).parent.resolve()

    print("Compiling PO files to MO format...\n")

    # Find all locale directories
    locale_dirs = [d for d in script_dir.iterdir() if is_locale_dir(d)]

    if not locale_dirs:
        print("⚠ No locale directories found")
        return 0

    # Compile each locale
    success_count = 0
    fail_count = 0

    for locale_dir in sorted(locale_dirs):
        if compile_mo_file(locale_dir):
            success_count += 1
        else:
            fail_count += 1

    # Summary
    print(f"\n{'='*50}")
    print(f"✓ Compiled: {success_count}")
    if fail_count > 0:
        print(f"✗ Failed: {fail_count}")
        return 1

    print("Done!")
    return 0


if __name__ == "__main__":
    sys.exit(main())

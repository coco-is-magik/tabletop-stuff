#!/usr/bin/env python3
"""Defer PCGen RC10's two eager download bodies to task execution.

Default: print a unified diff without writing anything.
Use --apply to write the change after creating a non-overwriting backup.
This does NOT change the Java/JavaFX versions or remove task dependencies.
For compileJava-only recovery, the deferred download tasks can then be excluded
with: -x downloadJRE -x downloadJavaFXModules
Do not use those exclusions as a full test/runtime/packaging fix.

Source checked:
https://raw.githubusercontent.com/PCGen/pcgen/6.08.00RC10/build.gradle
"""
from __future__ import annotations

import argparse
import difflib
import os
from pathlib import Path
import re
import stat
import sys
import tempfile

MARKERS = (
    'task downloadJRE {',
    'task downloadJavaFXModules(dependsOn: downloadJRE) {',
    'compileJava.dependsOn(downloadJavaFXModules)',
)


def transform(text: str) -> str:
    """Wrap only the two recognized task bodies, refusing unexpected layouts."""
    newline = '\r\n' if '\r\n' in text else '\n'
    lines = text.splitlines(keepends=True)
    positions: list[int] = []
    for marker in MARKERS:
        found = [i for i, line in enumerate(lines) if line.strip() == marker]
        if len(found) != 1:
            raise ValueError(f'Expected exactly one line {marker!r}; found {len(found)}. '
                             'Inspect this locally modified build script manually.')
        positions.append(found[0])
    if positions != sorted(positions):
        raise ValueError('The expected task declarations are not in upstream order.')

    for index in (1, 0):
        start, boundary = positions[index], positions[index + 1]
        closing = boundary - 1
        while closing > start and not lines[closing].strip():
            closing -= 1
        if lines[closing].strip() != '}':
            raise ValueError(f'Unexpected ending for {MARKERS[index]!r}. No file was changed.')

        body = lines[start + 1:closing]
        meaningful = [line.strip() for line in body
                      if line.strip() and not line.lstrip().startswith('//')]
        if meaningful and meaningful[0] == 'doLast {':
            continue  # Already deferred; do not add a second wrapper.
        expected = 'def major = 16' if index == 0 else 'def major = "16"'
        if not meaningful or meaningful[0] != expected:
            raise ValueError(f'Unexpected body for {MARKERS[index]!r}. '
                             'Inspect this locally modified build script manually.')
        if any(re.search(r'\bdo(?:First|Last)\s*\{', line) for line in meaningful):
            raise ValueError('An existing task action was found in a download body. '
                             'Refusing to wrap it automatically.')

        # Keep the existing body untouched for a minimal, reviewable diff.
        lines.insert(closing, '    }' + newline)
        lines.insert(start + 1, '    doLast {' + newline)

    return ''.join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('build_file', type=Path, help='Path to the vendored build.gradle')
    parser.add_argument('--apply', action='store_true', help='Back up and apply the displayed diff')
    args = parser.parse_args()
    path = args.build_file
    try:
        if path.is_symlink() or not path.is_file():
            raise ValueError('The build file must be an existing regular file, not a symlink.')
        old_bytes = path.read_bytes()
        old = old_bytes.decode('utf-8')
        new = transform(old)
        if new == old:
            print('Both download task bodies already start with doLast; nothing changed.')
            return 0
        sys.stdout.writelines(difflib.unified_diff(
            old.splitlines(keepends=True), new.splitlines(keepends=True),
            fromfile=str(path), tofile=str(path) + ' (deferred downloads)'))
        if not args.apply:
            print('\nPreview only. Re-run with --apply to create a backup and write this change.')
            return 0

        if path.read_bytes() != old_bytes:
            raise ValueError('The build file changed during review; refusing to overwrite it.')
        backup = path.with_name(path.name + '.before-deferred-downloads')
        with backup.open('xb') as stream:
            stream.write(old_bytes)
        mode = stat.S_IMODE(path.stat().st_mode)
        os.chmod(backup, mode)
        fd, temporary_name = tempfile.mkstemp(prefix=path.name + '.', dir=path.parent)
        try:
            with os.fdopen(fd, 'wb') as stream:
                stream.write(new.encode('utf-8'))
                stream.flush()
                os.fsync(stream.fileno())
            os.chmod(temporary_name, mode)
            if path.read_bytes() != old_bytes:
                raise ValueError('The build file changed while preparing the patch; '
                                 'the original was not overwritten.')
            os.replace(temporary_name, path)
        finally:
            if os.path.exists(temporary_name):
                os.unlink(temporary_name)
        print(f'\nApplied. Backup: {backup}')
        return 0
    except (OSError, UnicodeError, ValueError) as exc:
        print(f'Error: {exc}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())

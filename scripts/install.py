#!/usr/bin/env python3
"""Install one declared template profile without silent overwrites."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

from distribution_lib import (
    DistributionError,
    InstallCommittedInterrupt,
    InstallConflict,
    REQUIRED_PROFILES,
    install_profile,
)


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Install a manifest-defined multi-agent template profile, verifying "
            "installed destination identities before commit. "
            "Existing .codex/config.toml remains user-owned and is never installed or replaced."
        )
    )
    parser.add_argument(
        "--profile",
        choices=REQUIRED_PROFILES,
        required=True,
        help="Artifact profile to install; full and frontend include the antislop core.",
    )
    parser.add_argument(
        "--target",
        type=Path,
        required=True,
        help="Existing or new target project directory.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate and print the exact copy plan without writing files.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Allow replacement of existing destination files after preflight.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        operations, conflicts = install_profile(
            REPOSITORY_ROOT,
            args.profile,
            args.target,
            dry_run=args.dry_run,
            force=args.force,
        )
    except InstallConflict as exc:
        print("Install blocked: existing files would be overwritten.", file=sys.stderr)
        for conflict in exc.conflicts:
            print(f"  CONFLICT {conflict.as_posix()}", file=sys.stderr)
        print("Re-run with --force only after reviewing every conflict.", file=sys.stderr)
        return 2
    except InstallCommittedInterrupt:
        print(
            "Install committed, but cleanup was interrupted. "
            "Installed files remain in place; temporary files may remain.",
            file=sys.stderr,
        )
        return 130
    except KeyboardInterrupt:
        print("Install interrupted; applied changes were rolled back.", file=sys.stderr)
        return 130
    except DistributionError as exc:
        print(f"Install blocked: {exc}", file=sys.stderr)
        return 2
    except OSError as exc:
        print(f"Install blocked by an operating-system error: {exc}", file=sys.stderr)
        return 2

    action = "DRY-RUN" if args.dry_run else "INSTALLED"
    print(f"{action} profile={args.profile} files={len(operations)}")
    if conflicts:
        print(
            f"would_overwrite={len(conflicts)}"
            if args.dry_run
            else f"overwritten={len(conflicts)}"
        )
    for operation in operations:
        source = operation.source.relative_to(REPOSITORY_ROOT)
        print(f"  COPY {source.as_posix()} -> {operation.destination.as_posix()}")
    if args.dry_run and conflicts and not args.force:
        print("Dry-run found existing files that would be overwritten.", file=sys.stderr)
        for conflict in conflicts:
            print(f"  CONFLICT {conflict.as_posix()}", file=sys.stderr)
        print("Re-run with --force only after reviewing every conflict.", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

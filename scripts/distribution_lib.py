"""Shared, standard-library-only helpers for template distribution."""

from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path
import shutil
import stat
import tempfile
import tomllib
from typing import Any, Iterable
import uuid


MANIFEST_PATH = Path("distribution/profiles.toml")
REQUIRED_PROFILES = ("full", "backend", "frontend")
REQUIRED_WORKFLOW_IDS = ("bugfix", "feature-delivery", "refactor")
PROFILE_AGENT_TEMPLATES = {
    "full": Path("templates/project-AGENTS.md"),
    "backend": Path("templates/project-AGENTS.backend.md"),
    "frontend": Path("templates/project-AGENTS.frontend.md"),
}


class DistributionError(RuntimeError):
    """Raised when a distribution manifest or install target is unsafe."""


class InstallCommittedInterrupt(KeyboardInterrupt):
    """Raised when cleanup is interrupted after the installation is committed."""


class InstallConflict(DistributionError):
    """Raised when an install would overwrite existing files."""

    def __init__(self, conflicts: Iterable[Path]) -> None:
        self.conflicts = tuple(sorted(conflicts, key=lambda path: path.as_posix()))
        joined = ", ".join(path.as_posix() for path in self.conflicts)
        super().__init__(f"refusing to overwrite existing paths: {joined}")


@dataclass(frozen=True)
class CopyOperation:
    source: Path
    destination: Path


@dataclass(frozen=True)
class _AppliedOperation:
    destination: Path
    parent_fd: int
    name: str
    backup_name: str | None
    installed_identity: tuple[int, int]


def _relative_path(value: object, label: str) -> Path:
    if not isinstance(value, str) or not value.strip():
        raise DistributionError(f"{label} must be a non-empty relative path")
    path = Path(value)
    if path == Path(".") or path.is_absolute() or ".." in path.parts:
        raise DistributionError(f"{label} escapes its root: {value!r}")
    return path


def _safe_source(root: Path, value: object, label: str) -> Path:
    relative = _relative_path(value, label)
    resolved_root = root.resolve()
    candidate = resolved_root / relative
    resolved = candidate.resolve()
    try:
        resolved.relative_to(resolved_root)
    except ValueError as exc:
        raise DistributionError(f"{label} escapes repository root: {value!r}") from exc
    if not resolved.exists():
        raise DistributionError(f"{label} does not exist: {relative.as_posix()}")
    return candidate


def load_manifest(root: Path, manifest_path: Path | None = None) -> dict[str, Any]:
    root = root.resolve()
    path = manifest_path or root / MANIFEST_PATH
    if not path.is_absolute():
        path = root / path
    path = path.resolve()
    try:
        path.relative_to(root)
    except ValueError as exc:
        raise DistributionError("manifest must live under repository root") from exc
    try:
        with path.open("rb") as stream:
            manifest = tomllib.load(stream)
    except (OSError, tomllib.TOMLDecodeError) as exc:
        raise DistributionError(f"cannot load manifest {path}: {exc}") from exc

    schema_version = manifest.get("schema_version")
    if type(schema_version) is not int or schema_version != 1:
        raise DistributionError("manifest schema_version must be 1")
    profiles = manifest.get("profiles")
    if not isinstance(profiles, dict):
        raise DistributionError("manifest must define a profiles table")
    missing = sorted(set(REQUIRED_PROFILES) - set(profiles))
    unexpected = sorted(set(profiles) - set(REQUIRED_PROFILES))
    if missing or unexpected:
        raise DistributionError(
            f"manifest profile tables mismatch; missing={missing}, unexpected={unexpected}"
        )
    for profile_name in REQUIRED_PROFILES:
        if not isinstance(profiles[profile_name], dict):
            raise DistributionError(
                f"profile {profile_name!r} must be declared as a table"
            )
    return manifest


def profile_names(root: Path, manifest_path: Path | None = None) -> tuple[str, ...]:
    manifest = load_manifest(root, manifest_path)
    return tuple(sorted(manifest["profiles"]))


def _string_list(profile: dict[str, Any], key: str, profile_name: str) -> list[str]:
    values = profile.get(key)
    if not isinstance(values, list) or not values:
        raise DistributionError(f"profile {profile_name!r} must define non-empty {key}")
    if not all(isinstance(value, str) and value.strip() for value in values):
        raise DistributionError(f"profile {profile_name!r} {key} must contain strings")
    if len(values) != len(set(values)):
        raise DistributionError(f"profile {profile_name!r} {key} contains duplicates")
    return values


def _expand_tree(source: Path, destination: Path, label: str) -> list[CopyOperation]:
    if source.is_symlink():
        raise DistributionError(f"{label} may not be a symlink: {source}")
    if source.is_file():
        return [CopyOperation(source, destination)]
    if not source.is_dir():
        raise DistributionError(f"{label} is not a file or directory: {source}")

    operations: list[CopyOperation] = []
    for child in sorted(source.rglob("*")):
        if child.is_symlink():
            raise DistributionError(f"{label} contains a symlink: {child}")
        if child.is_file():
            operations.append(
                CopyOperation(child, destination / child.relative_to(source))
            )
    if not operations:
        raise DistributionError(f"{label} contains no files: {source}")
    return operations


def _artifact_operations(
    root: Path,
    profile: dict[str, Any],
    profile_name: str,
    key: str,
) -> list[CopyOperation]:
    entries = profile.get(key, [])
    if not isinstance(entries, list) or not entries:
        raise DistributionError(
            f"profile {profile_name!r} must define non-empty {key}"
        )

    operations: list[CopyOperation] = []
    for index, entry in enumerate(entries):
        label = f"profile {profile_name!r} {key}[{index}]"
        if not isinstance(entry, dict):
            raise DistributionError(f"{label} must be a table")
        source = _safe_source(root, entry.get("source"), f"{label}.source")
        destination = _relative_path(entry.get("target"), f"{label}.target")
        operations.extend(_expand_tree(source, destination, label))
    return operations


def build_profile_plan(
    root: Path,
    profile_name: str,
    manifest_path: Path | None = None,
) -> list[CopyOperation]:
    """Build the exact file-copy plan declared for one install profile."""

    root = root.resolve()
    manifest = load_manifest(root, manifest_path)
    profiles = manifest["profiles"]
    profile = profiles.get(profile_name)
    if not isinstance(profile, dict):
        available = ", ".join(sorted(profiles))
        raise DistributionError(
            f"unknown profile {profile_name!r}; available profiles: {available}"
        )

    base_config = _safe_source(root, manifest.get("base_config"), "base_config")
    if not base_config.is_file():
        raise DistributionError("base_config must be a file")
    template = _safe_source(
        root,
        profile.get("agents_template"),
        f"profile {profile_name!r} agents_template",
    )
    if not template.is_file():
        raise DistributionError(f"profile {profile_name!r} template must be a file")
    expected_template = (root / PROFILE_AGENT_TEMPLATES[profile_name]).resolve()
    if template.resolve() != expected_template:
        raise DistributionError(
            f"profile {profile_name!r} must use "
            f"{PROFILE_AGENT_TEMPLATES[profile_name].as_posix()}"
        )

    operations = [
        CopyOperation(base_config, Path(".codex/config.toml")),
        CopyOperation(template, Path("AGENTS.md")),
    ]

    for agent in _string_list(profile, "agents", profile_name):
        source = _safe_source(
            root,
            f".codex/agents/{agent}.toml",
            f"profile {profile_name!r} agent {agent!r}",
        )
        if not source.is_file():
            raise DistributionError(f"agent source must be a file: {source}")
        operations.append(
            CopyOperation(source, Path(f".codex/agents/{agent}.toml"))
        )

    for skill in _string_list(profile, "skills", profile_name):
        source = _safe_source(
            root,
            f".agents/skills/{skill}",
            f"profile {profile_name!r} skill {skill!r}",
        )
        operations.extend(
            _expand_tree(
                source,
                Path(f".agents/skills/{skill}"),
                f"profile {profile_name!r} skill {skill!r}",
            )
        )

    stack_operations = _artifact_operations(root, profile, profile_name, "stack")
    expected_stack_targets = {Path("stack/default-stack.yaml")}
    actual_stack_targets = {operation.destination for operation in stack_operations}
    if actual_stack_targets != expected_stack_targets:
        raise DistributionError(
            f"profile {profile_name!r} stack targets mismatch; "
            f"expected={sorted(path.as_posix() for path in expected_stack_targets)}, "
            f"actual={sorted(path.as_posix() for path in actual_stack_targets)}"
        )
    expected_stack_source = (root / "stack/default-stack.yaml").resolve()
    if any(
        operation.source.resolve() != expected_stack_source
        for operation in stack_operations
    ):
        raise DistributionError(
            f"profile {profile_name!r} must copy the canonical stack/default-stack.yaml"
        )
    operations.extend(stack_operations)

    workflow_operations = _artifact_operations(
        root, profile, profile_name, "workflows"
    )
    expected_workflow_targets = {
        Path(f"workflows/{workflow_id}.yaml")
        for workflow_id in REQUIRED_WORKFLOW_IDS
    }
    actual_workflow_targets = {
        operation.destination for operation in workflow_operations
    }
    if actual_workflow_targets != expected_workflow_targets:
        raise DistributionError(
            f"profile {profile_name!r} workflow targets mismatch; "
            f"expected={sorted(path.as_posix() for path in expected_workflow_targets)}, "
            f"actual={sorted(path.as_posix() for path in actual_workflow_targets)}"
        )
    if profile_name == "full":
        expected_sources = {
            (root / f"workflows/{workflow_id}.yaml").resolve()
            for workflow_id in REQUIRED_WORKFLOW_IDS
        }
        actual_sources = {
            operation.source.resolve() for operation in workflow_operations
        }
        if actual_sources != expected_sources:
            raise DistributionError(
                "profile 'full' workflows must copy the canonical workflow files"
            )
    operations.extend(workflow_operations)

    destinations: dict[Path, Path] = {}
    for operation in operations:
        previous = destinations.get(operation.destination)
        if previous is not None:
            raise DistributionError(
                "profile "
                f"{profile_name!r} maps both {previous} and {operation.source} to "
                f"{operation.destination.as_posix()}"
            )
        destinations[operation.destination] = operation.source
    return sorted(operations, key=lambda operation: operation.destination.as_posix())


def normalize_target(target: Path) -> Path:
    target = target.expanduser()
    if not target.is_absolute():
        target = Path.cwd() / target
    target = target.absolute()
    if target.is_symlink():
        raise DistributionError("install target may not be a symlink")
    target = target.resolve(strict=False)
    if target.parent == target:
        raise DistributionError("install target may not be the filesystem root")
    if target.exists() and not target.is_dir():
        raise DistributionError(f"install target is not a directory: {target}")
    if not target.exists() and not target.parent.is_dir():
        raise DistributionError(
            f"install target parent must already exist: {target.parent}"
        )
    return target


def _unsafe_parent(target: Path, destination: Path) -> Path | None:
    current = target
    for part in destination.parts[:-1]:
        current = current / part
        if current.is_symlink():
            return current
        if current.exists() and not current.is_dir():
            return current
    return None


def preflight_install(
    target: Path,
    operations: Iterable[CopyOperation],
) -> tuple[Path, tuple[Path, ...]]:
    target = normalize_target(target)
    conflicts: list[Path] = []
    for operation in operations:
        unsafe_parent = _unsafe_parent(target, operation.destination)
        if unsafe_parent is not None:
            raise DistributionError(
                f"destination parent is not a safe directory: {unsafe_parent}"
            )
        destination = target / operation.destination
        if destination.exists() and destination.is_dir() and not destination.is_symlink():
            raise DistributionError(f"file destination is an existing directory: {destination}")
        if destination.exists() or destination.is_symlink():
            conflicts.append(operation.destination)
    return target, tuple(sorted(conflicts, key=lambda path: path.as_posix()))


_DIRECTORY_OPEN_FLAGS = (
    os.O_RDONLY
    | getattr(os, "O_DIRECTORY", 0)
    | getattr(os, "O_NOFOLLOW", 0)
)
_FILE_CREATE_FLAGS = (
    os.O_WRONLY
    | os.O_CREAT
    | os.O_EXCL
    | getattr(os, "O_NOFOLLOW", 0)
)


def _require_secure_install_primitives() -> None:
    required_dir_fd = (
        ("open", os.open),
        ("mkdir", os.mkdir),
        ("stat", os.stat),
        ("link", os.link),
        ("rename", os.rename),
        ("unlink", os.unlink),
        ("rmdir", os.rmdir),
        ("utime", os.utime),
    )
    missing = [
        name
        for name, function in required_dir_fd
        if function not in os.supports_dir_fd
    ]
    if not getattr(os, "O_DIRECTORY", 0):
        missing.append("O_DIRECTORY")
    if not getattr(os, "O_NOFOLLOW", 0):
        missing.append("O_NOFOLLOW")
    if missing:
        raise DistributionError(
            "secure installation requires POSIX dir_fd and no-follow filesystem "
            f"primitives; unavailable: {', '.join(sorted(set(missing)))}"
        )


def _open_absolute_directory(path: Path) -> int:
    if not path.is_absolute():
        raise DistributionError(f"secure directory path must be absolute: {path}")
    try:
        current_fd = os.open(path.anchor, _DIRECTORY_OPEN_FLAGS)
    except OSError as exc:
        raise DistributionError(
            f"cannot securely open directory anchor {path.anchor!r}: {exc}"
        ) from exc
    try:
        for part in path.parts[1:]:
            try:
                next_fd = os.open(part, _DIRECTORY_OPEN_FLAGS, dir_fd=current_fd)
            except OSError as exc:
                raise DistributionError(
                    f"cannot securely open directory component {part!r} in {path}: {exc}"
                ) from exc
            os.close(current_fd)
            current_fd = next_fd
        return current_fd
    except BaseException:
        os.close(current_fd)
        raise


def _open_destination_parent(
    root_fd: int,
    parent: Path,
    created_directories: set[Path],
) -> int:
    """Open a destination parent without following target-owned symlinks."""

    current_fd = os.dup(root_fd)
    current_relative = Path()
    try:
        for part in parent.parts:
            if part in {"", "."}:
                continue
            current_relative /= part
            try:
                next_fd = os.open(part, _DIRECTORY_OPEN_FLAGS, dir_fd=current_fd)
            except FileNotFoundError:
                try:
                    os.mkdir(part, mode=0o755, dir_fd=current_fd)
                except FileExistsError:
                    pass
                else:
                    created_directories.add(current_relative)
                try:
                    next_fd = os.open(part, _DIRECTORY_OPEN_FLAGS, dir_fd=current_fd)
                except OSError as exc:
                    raise DistributionError(
                        "destination parent became unsafe while creating "
                        f"{current_relative.as_posix()}: {exc}"
                    ) from exc
            except OSError as exc:
                raise DistributionError(
                    "destination parent is not a safe directory: "
                    f"{current_relative.as_posix()}: {exc}"
                ) from exc
            os.close(current_fd)
            current_fd = next_fd
        return current_fd
    except BaseException:
        os.close(current_fd)
        raise


def _open_existing_parent(root_fd: int, parent: Path) -> int:
    current_fd = os.dup(root_fd)
    current_relative = Path()
    try:
        for part in parent.parts:
            if part in {"", "."}:
                continue
            current_relative /= part
            try:
                next_fd = os.open(part, _DIRECTORY_OPEN_FLAGS, dir_fd=current_fd)
            except OSError as exc:
                raise DistributionError(
                    "cannot securely open rollback parent "
                    f"{current_relative.as_posix()}: {exc}"
                ) from exc
            os.close(current_fd)
            current_fd = next_fd
        return current_fd
    except BaseException:
        os.close(current_fd)
        raise


def _leaf_stat(parent_fd: int, name: str) -> os.stat_result | None:
    try:
        result = os.stat(name, dir_fd=parent_fd, follow_symlinks=False)
    except FileNotFoundError:
        return None
    if stat.S_ISDIR(result.st_mode):
        raise DistributionError(f"file destination is an existing directory: {name}")
    if not (stat.S_ISREG(result.st_mode) or stat.S_ISLNK(result.st_mode)):
        raise DistributionError(f"file destination has unsupported type: {name}")
    return result


def _unique_sibling_name(parent_fd: int, name: str, purpose: str) -> str:
    for _ in range(100):
        candidate = f".{name}.template-{purpose}-{uuid.uuid4().hex}"
        try:
            os.stat(candidate, dir_fd=parent_fd, follow_symlinks=False)
        except FileNotFoundError:
            return candidate
    raise DistributionError(f"cannot allocate a temporary sibling for {name}")


def _copy_to_secure_temp(parent_fd: int, name: str, source: Path) -> str:
    temporary_name = _unique_sibling_name(parent_fd, name, "new")
    descriptor: int | None = None
    try:
        descriptor = os.open(
            temporary_name,
            _FILE_CREATE_FLAGS,
            0o600,
            dir_fd=parent_fd,
        )
        source_stat = source.stat()
        with source.open("rb") as source_stream, os.fdopen(
            descriptor, "wb", closefd=True
        ) as destination_stream:
            descriptor = None
            shutil.copyfileobj(source_stream, destination_stream)
            destination_stream.flush()
            os.fchmod(destination_stream.fileno(), stat.S_IMODE(source_stat.st_mode))
            os.fsync(destination_stream.fileno())
        os.utime(
            temporary_name,
            ns=(source_stat.st_atime_ns, source_stat.st_mtime_ns),
            dir_fd=parent_fd,
            follow_symlinks=False,
        )
        return temporary_name
    except BaseException:
        if descriptor is not None:
            os.close(descriptor)
        try:
            os.unlink(temporary_name, dir_fd=parent_fd)
        except FileNotFoundError:
            pass
        raise


def _backup_destination(parent_fd: int, name: str) -> str | None:
    existing = _leaf_stat(parent_fd, name)
    if existing is None:
        return None
    backup_name = _unique_sibling_name(parent_fd, name, "backup")
    try:
        os.link(
            name,
            backup_name,
            src_dir_fd=parent_fd,
            dst_dir_fd=parent_fd,
            follow_symlinks=False,
        )
    except OSError as exc:
        raise DistributionError(f"cannot create rollback backup for {name}: {exc}") from exc
    return backup_name


def _path_identity(parent_fd: int, name: str) -> tuple[int, int]:
    result = os.stat(name, dir_fd=parent_fd, follow_symlinks=False)
    return result.st_dev, result.st_ino


def _fd_identity(descriptor: int) -> tuple[int, int]:
    result = os.fstat(descriptor)
    return result.st_dev, result.st_ino


def _optional_path_identity(path: Path) -> tuple[int, int] | None:
    try:
        result = os.stat(path, follow_symlinks=False)
    except FileNotFoundError:
        return None
    return result.st_dev, result.st_ino


def _verify_install_root(
    target: Path,
    target_parent_fd: int,
    root_fd: int,
    expected_parent_identity: tuple[int, int],
) -> None:
    parent_identity = _fd_identity(target_parent_fd)
    root_identity = _fd_identity(root_fd)
    path_parent_identity = _optional_path_identity(target.parent)
    path_target_identity = _optional_path_identity(target)
    try:
        linked_target_identity = _path_identity(target_parent_fd, target.name)
    except FileNotFoundError as exc:
        raise DistributionError(
            "install target was removed or renamed during installation"
        ) from exc
    if (
        parent_identity != expected_parent_identity
        or path_parent_identity != expected_parent_identity
        or linked_target_identity != root_identity
        or path_target_identity != root_identity
    ):
        raise DistributionError(
            "install target identity changed during installation; refusing to split "
            "the profile across directory roots"
        )


def _installed_identity(parent_fd: int, name: str) -> tuple[int, int]:
    return _path_identity(parent_fd, name)


def _commit_staged_file(
    parent_fd: int,
    name: str,
    staged_source: Path,
    *,
    force: bool,
) -> tuple[str | None, tuple[int, int]]:
    temporary_name = _copy_to_secure_temp(parent_fd, name, staged_source)
    expected_identity = _path_identity(parent_fd, temporary_name)
    backup_name: str | None = None
    committed = False
    try:
        if not force:
            try:
                os.link(
                    temporary_name,
                    name,
                    src_dir_fd=parent_fd,
                    dst_dir_fd=parent_fd,
                    follow_symlinks=False,
                )
                committed = True
            except FileExistsError as exc:
                raise InstallConflict((Path(name),)) from exc
        else:
            backup_name = _backup_destination(parent_fd, name)
            if backup_name is None:
                try:
                    os.link(
                        temporary_name,
                        name,
                        src_dir_fd=parent_fd,
                        dst_dir_fd=parent_fd,
                        follow_symlinks=False,
                    )
                    committed = True
                except FileExistsError:
                    # A destination appeared after the check. Back it up before replacing it.
                    backup_name = _backup_destination(parent_fd, name)
                    if backup_name is None:
                        raise DistributionError(
                            f"destination changed repeatedly during forced install: {name}"
                        )
                    os.replace(
                        temporary_name,
                        name,
                        src_dir_fd=parent_fd,
                        dst_dir_fd=parent_fd,
                    )
                    temporary_name = ""
                    committed = True
            else:
                os.replace(
                    temporary_name,
                    name,
                    src_dir_fd=parent_fd,
                    dst_dir_fd=parent_fd,
                )
                temporary_name = ""
                committed = True
        identity = _installed_identity(parent_fd, name)
        if temporary_name:
            os.unlink(temporary_name, dir_fd=parent_fd)
            temporary_name = ""
        return backup_name, identity
    except BaseException as exc:
        local_rollback_error: OSError | None = None
        if committed:
            try:
                if _path_identity(parent_fd, name) != expected_identity:
                    raise OSError(
                        f"destination changed concurrently before local rollback: {name}"
                    )
                if backup_name is None:
                    os.unlink(name, dir_fd=parent_fd)
                else:
                    os.replace(
                        backup_name,
                        name,
                        src_dir_fd=parent_fd,
                        dst_dir_fd=parent_fd,
                    )
                    backup_name = None
            except OSError as rollback_exc:
                local_rollback_error = rollback_exc
        if backup_name is not None and not committed:
            try:
                os.unlink(backup_name, dir_fd=parent_fd)
            except OSError as rollback_exc:
                local_rollback_error = rollback_exc
        if local_rollback_error is not None:
            raise DistributionError(
                f"commit failed for {name}: {exc}; local rollback failed: "
                f"{local_rollback_error}"
            ) from exc
        raise
    finally:
        if temporary_name:
            try:
                os.unlink(temporary_name, dir_fd=parent_fd)
            except FileNotFoundError:
                pass


def _rollback(applied: list[_AppliedOperation]) -> list[str]:
    errors: list[str] = []
    for operation in reversed(applied):
        try:
            current = _installed_identity(operation.parent_fd, operation.name)
            if current != operation.installed_identity:
                raise DistributionError(
                    f"destination changed concurrently: {operation.destination.as_posix()}"
                )
            if operation.backup_name is None:
                os.unlink(operation.name, dir_fd=operation.parent_fd)
            else:
                os.replace(
                    operation.backup_name,
                    operation.name,
                    src_dir_fd=operation.parent_fd,
                    dst_dir_fd=operation.parent_fd,
                )
        except (OSError, DistributionError) as exc:
            errors.append(f"{operation.destination.as_posix()}: {exc}")
    return errors


def _remove_created_directories(
    root_fd: int,
    created_directories: set[Path],
) -> list[str]:
    errors: list[str] = []
    for relative in sorted(
        created_directories,
        key=lambda path: (len(path.parts), path.as_posix()),
        reverse=True,
    ):
        parent_fd: int | None = None
        try:
            parent_fd = _open_existing_parent(root_fd, relative.parent)
            os.rmdir(relative.name, dir_fd=parent_fd)
        except FileNotFoundError:
            pass
        except (OSError, DistributionError) as exc:
            errors.append(f"{relative.as_posix()}: {exc}")
        finally:
            if parent_fd is not None:
                os.close(parent_fd)
    return errors


def _stage_operations(
    operations: list[CopyOperation],
    staging_root: Path,
) -> list[Path]:
    staged: list[Path] = []
    for index, operation in enumerate(operations):
        destination = staging_root / f"{index:04d}"
        shutil.copy2(operation.source, destination)
        staged.append(destination)
    return staged


def _close_install_descriptors(
    applied: list[_AppliedOperation],
    root_fd: int | None,
    target_parent_fd: int | None,
) -> None:
    interrupted: KeyboardInterrupt | None = None
    descriptors = [operation.parent_fd for operation in applied]
    descriptors.extend(
        descriptor
        for descriptor in (root_fd, target_parent_fd)
        if descriptor is not None
    )
    for descriptor in descriptors:
        try:
            os.close(descriptor)
        except OSError:
            pass
        except KeyboardInterrupt as exc:
            # close() may have released the descriptor already; do not retry it.
            # Finish closing the other descriptors before propagating the interrupt.
            interrupted = exc
    if interrupted is not None:
        raise interrupted


def install_profile(
    root: Path,
    profile_name: str,
    target: Path,
    *,
    dry_run: bool = False,
    force: bool = False,
    manifest_path: Path | None = None,
) -> tuple[list[CopyOperation], tuple[Path, ...]]:
    try:
        operations = build_profile_plan(root, profile_name, manifest_path)
        target, conflicts = preflight_install(target, operations)
    except DistributionError:
        raise
    except OSError as exc:
        raise DistributionError(f"install preflight failed: {exc}") from exc
    if conflicts and not force and not dry_run:
        raise InstallConflict(conflicts)
    if dry_run:
        return operations, conflicts

    _require_secure_install_primitives()

    expected_parent_identity = _optional_path_identity(target.parent)
    if expected_parent_identity is None:
        raise DistributionError(
            f"install target parent disappeared before installation: {target.parent}"
        )
    expected_target_identity = _optional_path_identity(target)
    applied: list[_AppliedOperation] = []
    created_directories: set[Path] = set()
    target_created = False
    actual_conflicts: set[Path] = set()
    commit_complete = False
    target_parent_fd: int | None = None
    root_fd: int | None = None
    try:
        with tempfile.TemporaryDirectory(prefix="template-install-") as temporary:
            staged = _stage_operations(operations, Path(temporary))
            target_parent_fd = _open_absolute_directory(target.parent)
            if _fd_identity(target_parent_fd) != expected_parent_identity:
                raise DistributionError(
                    "install target parent identity changed after preflight"
                )
            if expected_target_identity is None:
                try:
                    os.mkdir(target.name, mode=0o755, dir_fd=target_parent_fd)
                except FileExistsError as exc:
                    raise DistributionError(
                        "install target appeared concurrently after preflight"
                    ) from exc
                target_created = True
            elif _path_identity(target_parent_fd, target.name) != expected_target_identity:
                raise DistributionError(
                    "install target identity changed after preflight"
                )

            try:
                root_fd = os.open(
                    target.name,
                    _DIRECTORY_OPEN_FLAGS,
                    dir_fd=target_parent_fd,
                )
            except OSError as exc:
                raise DistributionError(
                    f"cannot securely open install target {target}: {exc}"
                ) from exc
            if (
                expected_target_identity is not None
                and _fd_identity(root_fd) != expected_target_identity
            ):
                raise DistributionError(
                    "install target identity changed while it was being opened"
                )
            _verify_install_root(
                target,
                target_parent_fd,
                root_fd,
                expected_parent_identity,
            )

            for operation, staged_source in zip(operations, staged, strict=True):
                _verify_install_root(
                    target,
                    target_parent_fd,
                    root_fd,
                    expected_parent_identity,
                )
                parent_fd = _open_destination_parent(
                    root_fd,
                    operation.destination.parent,
                    created_directories,
                )
                try:
                    backup_name, identity = _commit_staged_file(
                        parent_fd,
                        operation.destination.name,
                        staged_source,
                        force=force,
                    )
                except InstallConflict as exc:
                    os.close(parent_fd)
                    raise InstallConflict((operation.destination,)) from exc
                except BaseException:
                    os.close(parent_fd)
                    raise
                if backup_name is not None:
                    actual_conflicts.add(operation.destination)
                applied.append(
                    _AppliedOperation(
                        destination=operation.destination,
                        parent_fd=parent_fd,
                        name=operation.destination.name,
                        backup_name=backup_name,
                        installed_identity=identity,
                    )
                )

            _verify_install_root(
                target,
                target_parent_fd,
                root_fd,
                expected_parent_identity,
            )
            commit_complete = True
            cleanup_errors: list[str] = []
            for operation in applied:
                if operation.backup_name is not None:
                    try:
                        os.unlink(operation.backup_name, dir_fd=operation.parent_fd)
                    except OSError as exc:
                        cleanup_errors.append(
                            f"{operation.destination.as_posix()}: {exc}"
                        )
            if cleanup_errors:
                raise DistributionError(
                    "install committed, but rollback-backup cleanup failed: "
                    + "; ".join(cleanup_errors)
                )
        return operations, tuple(
            sorted(actual_conflicts, key=lambda path: path.as_posix())
        )
    except BaseException as exc:
        if commit_complete:
            if isinstance(exc, KeyboardInterrupt):
                raise InstallCommittedInterrupt(
                    "install committed, but cleanup was interrupted"
                ) from exc
            if isinstance(exc, SystemExit):
                raise
            if isinstance(exc, DistributionError):
                raise
            raise DistributionError(
                f"install committed, but post-commit cleanup failed: {exc}"
            ) from exc
        rollback_errors = _rollback(applied)
        if root_fd is not None:
            rollback_errors.extend(
                _remove_created_directories(root_fd, created_directories)
            )
        if target_created:
            try:
                if target_parent_fd is None:
                    raise DistributionError("install target parent descriptor is unavailable")
                if root_fd is not None and (
                    _path_identity(target_parent_fd, target.name)
                    != _fd_identity(root_fd)
                ):
                    raise DistributionError(
                        "install target identity changed before rollback cleanup"
                    )
                os.rmdir(target.name, dir_fd=target_parent_fd)
            except FileNotFoundError:
                pass
            except (OSError, DistributionError) as rollback_exc:
                rollback_errors.append(f"{target}: {rollback_exc}")
        if rollback_errors:
            raise DistributionError(
                f"install failed: {exc}; rollback incomplete: {'; '.join(rollback_errors)}"
            ) from exc
        if isinstance(exc, DistributionError):
            raise
        if isinstance(exc, (KeyboardInterrupt, SystemExit)):
            raise
        raise DistributionError(f"install failed and was rolled back: {exc}") from exc
    finally:
        try:
            _close_install_descriptors(applied, root_fd, target_parent_fd)
        except KeyboardInterrupt as exc:
            if commit_complete:
                raise InstallCommittedInterrupt(
                    "install committed, but cleanup was interrupted"
                ) from exc
            raise

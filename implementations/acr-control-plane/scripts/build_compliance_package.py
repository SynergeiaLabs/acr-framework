#!/usr/bin/env python3
"""Build a versioned compliance package for the ACR control plane release."""
from __future__ import annotations

import argparse
import hashlib
import json
import tarfile
from datetime import datetime, timezone
from pathlib import Path


INCLUDED_FILES = [
    "README.md",
    "docs/provenance-and-verification.md",
    "docs/enterprise-roadmap.md",
    "docs/failure-load-dr-validation-2026-04-08.md",
    "docs/deployment.md",
    "docs/production_install.md",
    "docs/compliance/README.md",
    "docs/compliance/threat-model.md",
    "docs/compliance/shared-responsibility-matrix.md",
    "docs/compliance/control-mapping.md",
    "docs/compliance/evidence-package.md",
    "docs/compliance/external-assessment-scope.md",
]


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_manifest(
    *,
    implementation_dir: Path,
    version: str,
    source_ref: str,
    package_basename: str,
) -> tuple[dict, bytes]:
    files: list[dict[str, object]] = []
    for rel in INCLUDED_FILES:
        path = implementation_dir / rel
        if not path.exists():
            raise FileNotFoundError(f"Required compliance package file is missing: {path}")
        files.append(
            {
                "path": rel,
                "bytes": path.stat().st_size,
                "sha256": sha256_file(path),
            }
        )

    manifest = {
        "package_name": package_basename,
        "version": version,
        "source_ref": source_ref,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "files": files,
    }
    manifest_bytes = json.dumps(manifest, indent=2, sort_keys=True).encode() + b"\n"
    return manifest, manifest_bytes


def create_archive(
    *,
    implementation_dir: Path,
    package_basename: str,
    archive_path: Path,
    manifest_bytes: bytes,
) -> None:
    archive_path.parent.mkdir(parents=True, exist_ok=True)
    with tarfile.open(archive_path, "w:gz") as archive:
        for rel in INCLUDED_FILES:
            source = implementation_dir / rel
            archive.add(source, arcname=f"{package_basename}/{rel}")

        manifest_info = tarfile.TarInfo(name=f"{package_basename}/package-manifest.json")
        manifest_info.size = len(manifest_bytes)
        archive.addfile(manifest_info, fileobj=_BytesReader(manifest_bytes))


class _BytesReader:
    def __init__(self, payload: bytes) -> None:
        self._payload = payload
        self._offset = 0

    def read(self, size: int = -1) -> bytes:
        if size < 0:
            size = len(self._payload) - self._offset
        chunk = self._payload[self._offset : self._offset + size]
        self._offset += len(chunk)
        return chunk


def write_checksums(paths: list[Path], destination: Path) -> None:
    lines = [f"{sha256_file(path)}  {path.name}" for path in paths]
    destination.write_text("\n".join(lines) + "\n")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--implementation-dir",
        required=True,
        help="Path to implementations/acr-control-plane",
    )
    parser.add_argument(
        "--version",
        required=True,
        help="Release version or tag, for example v1.1.0",
    )
    parser.add_argument(
        "--source-ref",
        required=True,
        help="Git commit SHA or other immutable source reference",
    )
    parser.add_argument(
        "--output-dir",
        default="dist/compliance",
        help="Directory where the package, manifest, and checksums will be written",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    implementation_dir = Path(args.implementation_dir).resolve()
    output_dir = Path(args.output_dir).resolve()
    package_basename = f"acr-control-plane-compliance-package-{args.version}"

    _, manifest_bytes = build_manifest(
        implementation_dir=implementation_dir,
        version=args.version,
        source_ref=args.source_ref,
        package_basename=package_basename,
    )

    output_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = output_dir / f"{package_basename}.manifest.json"
    manifest_path.write_bytes(manifest_bytes)

    archive_path = output_dir / f"{package_basename}.tar.gz"
    create_archive(
        implementation_dir=implementation_dir,
        package_basename=package_basename,
        archive_path=archive_path,
        manifest_bytes=manifest_bytes,
    )

    checksum_path = output_dir / f"{package_basename}.sha256"
    write_checksums([archive_path, manifest_path], checksum_path)

    summary = {
        "package": str(archive_path),
        "manifest": str(manifest_path),
        "checksums": str(checksum_path),
        "package_sha256": sha256_file(archive_path),
    }
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()

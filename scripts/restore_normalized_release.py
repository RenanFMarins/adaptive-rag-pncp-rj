"""Baixa e instala atomicamente uma release normalizada sanitizada.

O fluxo não confia apenas no transporte HTTPS: os anexos são conferidos
contra ``SHA256SUMS.txt`` e o manifesto antes de o SQLite ser publicado no
caminho de destino.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import sqlite3
import tempfile
from typing import BinaryIO, Mapping
from urllib.parse import quote
from urllib.request import Request, urlopen


DEFAULT_REPOSITORY = "RenanFMarins/adaptive-rag-pncp-rj"
DEFAULT_TAG = "base-normalizada-pncp-rj-20261020-v1"
DEFAULT_DESTINATION = Path("data/normalized/pncp_rj_normalized.db")
MANIFEST_NAME = "release_manifest.json"
CHECKSUMS_NAME = "SHA256SUMS.txt"
DOWNLOAD_CHUNK_BYTES = 1024 * 1024
MINIMUM_FREE_BYTES = 512 * 1024 * 1024
FALLBACK_EXPANSION_FACTOR = 6

REQUIRED_TABLES = {
    "orgao",
    "unidade",
    "fornecedor",
    "contratacao",
    "contratacao_item",
    "resultado_item",
    "contrato",
    "empenho",
    "ata_registro_preco",
    "pca",
    "pca_item",
    "pca_contratacao_link",
    "normalization_lineage",
    "normalization_issue",
    "sanitization_metadata",
}

_REPOSITORY_RE = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


class RestoreError(RuntimeError):
    """Falha segura e explicável durante a restauração."""


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(DOWNLOAD_CHUNK_BYTES):
            digest.update(chunk)
    return digest.hexdigest()


def _asset_url(repository: str, tag: str, filename: str) -> str:
    if not _REPOSITORY_RE.fullmatch(repository):
        raise RestoreError("Repositório inválido; use o formato proprietário/nome")
    if Path(filename).name != filename or not filename:
        raise RestoreError("Nome de anexo inválido")
    owner, name = repository.split("/", 1)
    return (
        "https://github.com/"
        f"{quote(owner, safe='')}/{quote(name, safe='')}/releases/download/"
        f"{quote(tag, safe='')}/{quote(filename, safe='')}"
    )


def _download(url: str, destination: Path, *, timeout: float = 60.0) -> None:
    request = Request(url, headers={"User-Agent": "adaptive-rag-pncp-rj-restore/1"})
    try:
        with urlopen(request, timeout=timeout) as response:  # noqa: S310
            with destination.open("xb") as output:
                shutil.copyfileobj(response, output, DOWNLOAD_CHUNK_BYTES)
    except Exception as exc:
        destination.unlink(missing_ok=True)
        raise RestoreError(
            f"Falha ao baixar o anexo {destination.name}: {type(exc).__name__}"
        ) from exc


def _copy_local(source: Path, destination: Path) -> None:
    if not source.is_file():
        raise RestoreError(f"Anexo local ausente: {source.name}")
    try:
        with source.open("rb") as input_stream, destination.open("xb") as output:
            shutil.copyfileobj(input_stream, output, DOWNLOAD_CHUNK_BYTES)
    except Exception as exc:
        destination.unlink(missing_ok=True)
        raise RestoreError(
            f"Falha ao copiar o anexo local {source.name}: {type(exc).__name__}"
        ) from exc


def _parse_checksums(path: Path) -> dict[str, str]:
    checksums: dict[str, str] = {}
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError) as exc:
        raise RestoreError("Arquivo de checksums inválido") from exc

    for line in lines:
        if not line.strip():
            continue
        parts = line.split(maxsplit=1)
        if len(parts) != 2:
            raise RestoreError("Linha inválida em SHA256SUMS.txt")
        digest, filename = parts
        filename = filename.lstrip("*")
        if not _SHA256_RE.fullmatch(digest) or Path(filename).name != filename:
            raise RestoreError("Entrada insegura ou inválida em SHA256SUMS.txt")
        if filename in checksums:
            raise RestoreError(f"Checksum duplicado para {filename}")
        checksums[filename] = digest
    return checksums


def _read_manifest(path: Path, expected_tag: str) -> dict[str, object]:
    try:
        manifest = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise RestoreError("Manifesto da release inválido") from exc
    if not isinstance(manifest, dict):
        raise RestoreError("Manifesto da release deve ser um objeto JSON")
    if manifest.get("release_tag") != expected_tag:
        raise RestoreError("Tag do manifesto difere da release solicitada")
    return manifest


def _artifact_metadata(manifest: Mapping[str, object]) -> tuple[str, int, str, str]:
    artifact = manifest.get("artifact")
    if not isinstance(artifact, dict):
        raise RestoreError("Manifesto não possui metadados do artefato")
    filename = artifact.get("filename")
    size = artifact.get("size_bytes")
    compressed_sha = artifact.get("sha256_compressed")
    uncompressed_sha = artifact.get("sha256_uncompressed")
    if not isinstance(filename, str) or Path(filename).name != filename:
        raise RestoreError("Nome do artefato inválido no manifesto")
    if not isinstance(size, int) or size <= 0:
        raise RestoreError("Tamanho do artefato inválido no manifesto")
    if not isinstance(compressed_sha, str) or not _SHA256_RE.fullmatch(compressed_sha):
        raise RestoreError("SHA-256 compactado inválido no manifesto")
    if not isinstance(uncompressed_sha, str) or not _SHA256_RE.fullmatch(
        uncompressed_sha
    ):
        raise RestoreError("SHA-256 descompactado inválido no manifesto")
    return filename, size, compressed_sha, uncompressed_sha


def _verify_file(path: Path, expected_digest: str, expected_size: int | None = None) -> None:
    if expected_size is not None and path.stat().st_size != expected_size:
        raise RestoreError(f"Tamanho inesperado para {path.name}")
    if _sha256(path) != expected_digest:
        raise RestoreError(f"SHA-256 divergente para {path.name}")


def _required_free_bytes(compressed_size: int) -> int:
    return compressed_size * FALLBACK_EXPANSION_FACTOR + MINIMUM_FREE_BYTES


def _preflight_space(directory: Path, compressed_size: int) -> None:
    available = shutil.disk_usage(directory).free
    required = _required_free_bytes(compressed_size)
    if available < required:
        raise RestoreError(
            "Espaço insuficiente para baixar, descompactar e validar a base: "
            f"disponível={available} bytes; recomendado={required} bytes"
        )


def _decompress(source: Path, destination: Path) -> None:
    try:
        with gzip.open(source, "rb") as compressed, destination.open("xb") as output:
            shutil.copyfileobj(compressed, output, DOWNLOAD_CHUNK_BYTES)
    except Exception as exc:
        destination.unlink(missing_ok=True)
        raise RestoreError(f"Arquivo compactado inválido: {type(exc).__name__}") from exc


def _validate_database(path: Path, manifest: Mapping[str, object]) -> None:
    connection: sqlite3.Connection | None = None
    try:
        connection = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
        connection.execute("PRAGMA query_only = ON")
        tables = {
            str(row[0])
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table'"
            )
        }
        missing = sorted(REQUIRED_TABLES - tables)
        if missing:
            raise RestoreError("Tabelas obrigatórias ausentes: " + ", ".join(missing))

        integrity = connection.execute("PRAGMA integrity_check").fetchone()
        if integrity is None or integrity[0] != "ok":
            raise RestoreError("PRAGMA integrity_check não retornou ok")
        if connection.execute("PRAGMA foreign_key_check").fetchone() is not None:
            raise RestoreError("Banco restaurado possui violações de chave estrangeira")

        counts = manifest.get("counts")
        if not isinstance(counts, dict):
            raise RestoreError("Manifesto não possui contagens por tabela")
        for table in sorted(REQUIRED_TABLES - {"sanitization_metadata"}):
            expected = counts.get(table)
            if not isinstance(expected, int) or expected < 0:
                raise RestoreError(f"Contagem inválida para {table} no manifesto")
            observed = int(connection.execute(f'SELECT COUNT(*) FROM "{table}"').fetchone()[0])
            if observed != expected:
                raise RestoreError(
                    f"Contagem divergente para {table}: esperado={expected}; obtido={observed}"
                )

        sanitization = manifest.get("sanitization")
        if not isinstance(sanitization, dict):
            raise RestoreError("Manifesto não possui política de sanitização")
        metadata = connection.execute(
            "SELECT policy_version, key_fingerprint FROM sanitization_metadata"
        ).fetchone()
        if metadata is None or metadata != (
            sanitization.get("policy_version"),
            sanitization.get("key_fingerprint"),
        ):
            raise RestoreError("Metadados de sanitização divergem do manifesto")
    except sqlite3.Error as exc:
        raise RestoreError(f"SQLite restaurado inválido: {type(exc).__name__}") from exc
    finally:
        if connection is not None:
            connection.close()


def restore_release(
    *,
    repository: str,
    tag: str,
    destination: str | Path,
    force: bool = False,
    source_directory: str | Path | None = None,
) -> Path:
    """Restaura uma release validada e retorna o caminho publicado."""

    destination_path = Path(destination).expanduser().resolve()
    if destination_path.exists() and not force:
        raise RestoreError(
            f"Destino já existe; use --force para substituir: {destination_path}"
        )
    destination_path.parent.mkdir(parents=True, exist_ok=True)
    local_source = (
        Path(source_directory).expanduser().resolve()
        if source_directory is not None
        else None
    )

    with tempfile.TemporaryDirectory(
        prefix=".normalized-restore-", dir=destination_path.parent
    ) as temporary_name:
        temporary = Path(temporary_name)

        def acquire(filename: str) -> Path:
            target = temporary / filename
            if local_source is None:
                _download(_asset_url(repository, tag, filename), target)
            else:
                _copy_local(local_source / filename, target)
            return target

        checksums_path = acquire(CHECKSUMS_NAME)
        checksums = _parse_checksums(checksums_path)
        manifest_path = acquire(MANIFEST_NAME)
        manifest_digest = checksums.get(MANIFEST_NAME)
        if manifest_digest is None:
            raise RestoreError("Checksum do manifesto não foi publicado")
        _verify_file(manifest_path, manifest_digest)
        manifest = _read_manifest(manifest_path, tag)
        filename, size, compressed_sha, uncompressed_sha = _artifact_metadata(manifest)
        if checksums.get(filename) != compressed_sha:
            raise RestoreError("Checksum do artefato diverge entre manifesto e SHA256SUMS")

        _preflight_space(destination_path.parent, size)
        archive_path = acquire(filename)
        _verify_file(archive_path, compressed_sha, size)

        restored_path = temporary / "normalized-restored.db"
        _decompress(archive_path, restored_path)
        _verify_file(restored_path, uncompressed_sha)
        _validate_database(restored_path, manifest)
        os.replace(restored_path, destination_path)
    return destination_path


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Baixa, valida e instala a base normalizada sanitizada."
    )
    parser.add_argument("--repository", default=DEFAULT_REPOSITORY)
    parser.add_argument("--tag", default=DEFAULT_TAG)
    parser.add_argument("--destination", default=str(DEFAULT_DESTINATION))
    parser.add_argument(
        "--source-directory",
        help="Usa anexos já baixados em vez da rede; todos ainda são validados",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Substitui atomicamente um destino existente somente após validação",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        restored = restore_release(
            repository=args.repository,
            tag=args.tag,
            destination=args.destination,
            force=args.force,
            source_directory=args.source_directory,
        )
    except RestoreError as exc:
        print(f"Restauração recusada: {exc}")
        return 1
    print(f"Base normalizada restaurada e validada em: {restored}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

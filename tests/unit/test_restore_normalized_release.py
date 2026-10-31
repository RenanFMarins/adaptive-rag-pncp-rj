from __future__ import annotations

import gzip
import hashlib
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import patch

from scripts.restore_normalized_release import (
    CHECKSUMS_NAME,
    MANIFEST_NAME,
    REQUIRED_TABLES,
    RestoreError,
    _asset_url,
    restore_release,
)


TAG = "base-normalizada-test-v1"
ARCHIVE = "normalized.sqlite.gz"
POLICY = "pncp-public-v1"
FINGERPRINT = "f" * 64


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


class RestoreNormalizedReleaseTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.release = self.root / "release"
        self.release.mkdir()
        self.destination = self.root / "data" / "normalized.db"
        self.manifest = self._build_release()

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def _build_release(self) -> dict[str, object]:
        database = self.root / "source.db"
        connection = sqlite3.connect(database)
        for table in sorted(REQUIRED_TABLES - {"sanitization_metadata"}):
            connection.execute(f'CREATE TABLE "{table}" (id INTEGER PRIMARY KEY)')
        connection.execute(
            "CREATE TABLE sanitization_metadata ("
            "policy_version TEXT PRIMARY KEY, key_fingerprint TEXT NOT NULL)"
        )
        connection.execute(
            "INSERT INTO sanitization_metadata VALUES (?, ?)",
            (POLICY, FINGERPRINT),
        )
        connection.execute("INSERT INTO orgao(id) VALUES (1)")
        connection.commit()
        connection.close()

        archive = self.release / ARCHIVE
        with database.open("rb") as source, gzip.open(archive, "wb") as output:
            output.write(source.read())

        counts = {
            table: 1 if table == "orgao" else 0
            for table in REQUIRED_TABLES - {"sanitization_metadata"}
        }
        manifest: dict[str, object] = {
            "schema_version": 1,
            "release_tag": TAG,
            "artifact": {
                "filename": ARCHIVE,
                "size_bytes": archive.stat().st_size,
                "sha256_compressed": sha256(archive),
                "sha256_uncompressed": sha256(database),
            },
            "sanitization": {
                "policy_version": POLICY,
                "key_fingerprint": FINGERPRINT,
            },
            "counts": counts,
        }
        manifest_path = self.release / MANIFEST_NAME
        manifest_path.write_text(
            json.dumps(manifest, ensure_ascii=False), encoding="utf-8"
        )
        (self.release / CHECKSUMS_NAME).write_text(
            f"{sha256(archive)}  {ARCHIVE}\n"
            f"{sha256(manifest_path)}  {MANIFEST_NAME}\n",
            encoding="utf-8",
        )
        return manifest

    def restore(self, *, force: bool = False) -> Path:
        return restore_release(
            repository="owner/repository",
            tag=TAG,
            destination=self.destination,
            force=force,
            source_directory=self.release,
        )

    def test_restores_validated_database_from_local_assets(self) -> None:
        restored = self.restore()

        self.assertEqual(restored, self.destination.resolve())
        self.assertTrue(restored.is_file())
        with sqlite3.connect(f"file:{restored}?mode=ro", uri=True) as connection:
            self.assertEqual(connection.execute("PRAGMA integrity_check").fetchone()[0], "ok")
            self.assertEqual(connection.execute("SELECT COUNT(*) FROM orgao").fetchone()[0], 1)

    def test_refuses_existing_destination_without_force(self) -> None:
        self.destination.parent.mkdir(parents=True)
        self.destination.write_bytes(b"preservar")

        with self.assertRaisesRegex(RestoreError, "Destino já existe"):
            self.restore()

        self.assertEqual(self.destination.read_bytes(), b"preservar")

    def test_failure_does_not_replace_existing_destination(self) -> None:
        self.destination.parent.mkdir(parents=True)
        self.destination.write_bytes(b"preservar")
        checksums = self.release / CHECKSUMS_NAME
        checksums.write_text(
            checksums.read_text(encoding="utf-8").replace(
                self.manifest["artifact"]["sha256_compressed"], "0" * 64
            ),
            encoding="utf-8",
        )

        with self.assertRaisesRegex(RestoreError, "diverge"):
            self.restore(force=True)

        self.assertEqual(self.destination.read_bytes(), b"preservar")

    def test_refuses_database_count_mismatch(self) -> None:
        manifest_path = self.release / MANIFEST_NAME
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["counts"]["orgao"] = 2
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        archive = self.release / ARCHIVE
        (self.release / CHECKSUMS_NAME).write_text(
            f"{sha256(archive)}  {ARCHIVE}\n"
            f"{sha256(manifest_path)}  {MANIFEST_NAME}\n",
            encoding="utf-8",
        )

        with self.assertRaisesRegex(RestoreError, "Contagem divergente"):
            self.restore()

        self.assertFalse(self.destination.exists())

    def test_refuses_when_disk_space_is_insufficient(self) -> None:
        with patch(
            "scripts.restore_normalized_release.shutil.disk_usage"
        ) as disk_usage:
            disk_usage.return_value.free = 1
            with self.assertRaisesRegex(RestoreError, "Espaço insuficiente"):
                self.restore()

        self.assertFalse(self.destination.exists())

    def test_asset_url_is_encoded_and_repository_is_validated(self) -> None:
        url = _asset_url("RenanFMarins/adaptive-rag-pncp-rj", "release/v1", ARCHIVE)
        self.assertIn("release%2Fv1", url)
        with self.assertRaisesRegex(RestoreError, "Repositório inválido"):
            _asset_url("https://example.invalid/repo", TAG, ARCHIVE)
        with self.assertRaisesRegex(RestoreError, "Nome de anexo inválido"):
            _asset_url("owner/repo", TAG, "../secret")


if __name__ == "__main__":
    unittest.main()

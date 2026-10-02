import sqlite3
import tempfile
import unittest
from pathlib import Path

from app.core.database.connection import get_connection


class ConnectionTests(unittest.TestCase):
    def test_connection_uses_row_factory_and_foreign_keys(self):
        with tempfile.TemporaryDirectory() as directory:
            url = f"sqlite:///{Path(directory) / 'app.db'}"
            connection = get_connection(url)
            try:
                row = connection.execute(
                    "SELECT 1 AS value"
                ).fetchone()
                pragma = connection.execute(
                    "PRAGMA foreign_keys"
                ).fetchone()[0]
            finally:
                connection.close()

            self.assertIsInstance(row, sqlite3.Row)
            self.assertEqual(row["value"], 1)
            self.assertEqual(pragma, 1)


if __name__ == "__main__":
    unittest.main()

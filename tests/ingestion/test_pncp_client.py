import io
import json
import unittest
from unittest.mock import patch
from urllib.error import HTTPError, URLError

from src.ingestion.pncp_client import PNCPClient, PNCPClientError


class FakeResponse:
    def __init__(self, payload):
        self.payload = json.dumps(payload).encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False

    def read(self):
        return self.payload


class PNCPClientTests(unittest.TestCase):
    @patch("src.ingestion.pncp_client.urlopen")
    def test_get_uses_configured_base_and_returns_json(self, urlopen):
        urlopen.return_value = FakeResponse({"items": [{"id": "1"}]})
        client = PNCPClient(base_url="https://pncp.example")

        payload = client.get("/api/contratos", {"uf": "RJ", "pagina": 1})

        self.assertEqual(payload, {"items": [{"id": "1"}]})
        request = urlopen.call_args.args[0]
        self.assertEqual(
            request.full_url,
            "https://pncp.example/api/contratos?uf=RJ&pagina=1",
        )
        self.assertEqual(urlopen.call_args.kwargs["timeout"], 30.0)

    @patch("src.ingestion.pncp_client.urlopen")
    def test_get_translates_http_and_transport_errors(self, urlopen):
        client = PNCPClient(base_url="https://pncp.example")
        urlopen.side_effect = HTTPError(
            "https://pncp.example/api", 503, "unavailable", {}, io.BytesIO()
        )
        with self.assertRaises(PNCPClientError):
            client.get("/api")

        urlopen.side_effect = URLError("offline")
        with self.assertRaises(PNCPClientError):
            client.get("/api")


if __name__ == "__main__":
    unittest.main()

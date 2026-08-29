import os
from typing import Any, Dict, List

import requests

DEFAULT_BASE_URL = "https://askcos.mit.edu"
DEFAULT_TIMEOUT = 20.0


class AskcosAPIClient:
    """Minimal ASKCOS v2 API client for metadata discovery and connectivity checks.

    This client intentionally performs no chemistry prediction work by default.
    It only reads the published FastAPI/OpenAPI schema and enumerates the relevant
    retrosynthesis, tree-search, forward-prediction, and context endpoints.
    """

    def __init__(
        self,
        base_url: str | None = None,
        token: str | None = None,
        timeout: float = DEFAULT_TIMEOUT,
    ) -> None:
        self.base_url = (base_url or os.getenv("ASKCOS_BASE_URL") or DEFAULT_BASE_URL).rstrip("/")
        self.timeout = timeout
        self.token = token or os.getenv("ASKCOS_TOKEN")
        self.session = requests.Session()
        if self.token:
            self.session.headers.update({"Authorization": f"Bearer {self.token}"})

    def _url(self, path: str) -> str:
        if not path.startswith("/"):
            path = f"/{path}"
        return f"{self.base_url}{path}"

    def fetch_openapi(self) -> Dict[str, Any]:
        """Fetch the public OpenAPI schema from the ASKCOS deployment."""
        try:
            response = self.session.get(self._url("/openapi.json"), timeout=self.timeout)
            response.raise_for_status()
            schema = response.json()
            if not isinstance(schema, dict):
                raise ValueError("OpenAPI schema did not deserialize to a JSON object.")
            return schema
        except requests.RequestException as exc:
            raise RuntimeError(f"Failed to fetch ASKCOS OpenAPI schema from {self.base_url}: {exc}") from exc
        except ValueError as exc:
            raise RuntimeError(f"Failed to parse ASKCOS OpenAPI schema from {self.base_url}: {exc}") from exc

    def list_relevant_endpoints(self) -> Dict[str, List[str]]:
        """Return the routes relevant to retrosynthesis and synthesis planning."""
        schema = self.fetch_openapi()
        paths = schema.get("paths", {})
        if not isinstance(paths, dict):
            raise RuntimeError("OpenAPI schema is missing the 'paths' section.")

        relevant: Dict[str, List[str]] = {
            "tree_search": sorted(path for path in paths if path.startswith("/api/tree-search/")),
            "retro": sorted(path for path in paths if path.startswith("/api/retro/")),
            "forward": sorted(path for path in paths if path.startswith("/api/forward/")),
            "context": sorted(path for path in paths if path.startswith("/api/context/")),
            "admin": sorted(path for path in paths if path.startswith("/api/admin/")),
        }
        return relevant

    def check_connectivity(self) -> Dict[str, Any]:
        """Probe connectivity without invoking any chemistry prediction endpoint."""
        try:
            response = self.session.get(self._url("/openapi.json"), timeout=self.timeout)
            response.raise_for_status()
            schema = response.json()
            return {
                "base_url": self.base_url,
                "reachable": True,
                "status_code": response.status_code,
                "title": schema.get("info", {}).get("title"),
                "version": schema.get("info", {}).get("version"),
                "relevant_endpoints": self.list_relevant_endpoints(),
            }
        except requests.RequestException as exc:
            return {
                "base_url": self.base_url,
                "reachable": False,
                "error": str(exc),
                "relevant_endpoints": {},
            }
        except ValueError as exc:
            return {
                "base_url": self.base_url,
                "reachable": False,
                "error": f"OpenAPI parse error: {exc}",
                "relevant_endpoints": {},
            }


if __name__ == "__main__":
    client = AskcosAPIClient()
    print(client.check_connectivity())

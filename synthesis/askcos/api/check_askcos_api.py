#!/usr/bin/env python3
"""Simple ASKCOS connectivity verifier.

This script checks the OpenAPI metadata and prints the key retrosynthesis-related
routes. It does not submit molecules or call predictive endpoints.
"""

from askcos_client import AskcosAPIClient


def main() -> int:
    client = AskcosAPIClient()
    print(f"Base URL: {client.base_url}")
    try:
        schema = client.fetch_openapi()
        print(f"OpenAPI accessible: yes")
        print(f"API title: {schema.get('info', {}).get('title')}")
        print(f"API version: {schema.get('info', {}).get('version')}")
    except RuntimeError as exc:
        print(f"OpenAPI accessible: no")
        print(f"Error: {exc}")
        return 1

    endpoints = client.list_relevant_endpoints()
    for group, routes in endpoints.items():
        print(f"{group}:")
        for route in routes:
            print(f"  - {route}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

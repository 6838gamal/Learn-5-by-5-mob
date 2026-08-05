"""Thin async httpx client that proxies every request to the backend API.

Usage:
    client = ApiClient(base_url, access_token)
    data   = await client.get("/lessons/today")
    result = await client.post("/auth/login", json={...})
"""

import httpx
from typing import Any


class ApiError(Exception):
    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail
        super().__init__(f"API {status_code}: {detail}")


class ApiClient:
    def __init__(self, base_url: str, access_token: str | None = None):
        headers: dict[str, str] = {"Content-Type": "application/json", "Accept": "application/json"}
        if access_token:
            headers["Authorization"] = f"Bearer {access_token}"
        self._client = httpx.AsyncClient(base_url=base_url, headers=headers, timeout=30)

    # ------------------------------------------------------------------ #
    # Low-level helpers                                                    #
    # ------------------------------------------------------------------ #
    async def _raise_for_status(self, response: httpx.Response) -> dict:
        if response.status_code >= 400:
            try:
                detail = response.json().get("detail", response.text)
            except Exception:
                detail = response.text
            raise ApiError(response.status_code, detail)
        try:
            return response.json()
        except Exception:
            return {}

    async def get(self, path: str, params: dict | None = None) -> Any:
        r = await self._client.get(path, params=params)
        return await self._raise_for_status(r)

    async def post(self, path: str, json: Any = None, data: dict | None = None) -> Any:
        r = await self._client.post(path, json=json, data=data)
        return await self._raise_for_status(r)

    async def patch(self, path: str, json: Any = None) -> Any:
        r = await self._client.patch(path, json=json)
        return await self._raise_for_status(r)

    async def delete(self, path: str) -> Any:
        r = await self._client.delete(path)
        return await self._raise_for_status(r)

    async def aclose(self):
        await self._client.aclose()

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        await self.aclose()

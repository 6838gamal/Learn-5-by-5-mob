"""Thin async httpx client that proxies every request to the backend API."""

import httpx
from typing import Any


class ApiError(Exception):
    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail
        super().__init__(f"API {status_code}: {detail}")


class ApiClient:
    def __init__(self, base_url: str, access_token: str | None = None):
        # Only Accept header in defaults — Content-Type is set per-method so
        # multipart/form-data uploads let httpx set the boundary automatically.
        base_headers: dict[str, str] = {"Accept": "application/json"}
        if access_token:
            base_headers["Authorization"] = f"Bearer {access_token}"
        self._client = httpx.AsyncClient(base_url=base_url, headers=base_headers, timeout=60)

    async def _raise_for_status(self, response: httpx.Response) -> dict:
        if response.status_code >= 400:
            try:
                detail = response.json().get("detail", response.text)
            except Exception:
                detail = response.text
            raise ApiError(response.status_code, str(detail))
        try:
            return response.json()
        except Exception:
            return {}

    async def get(self, path: str, params: dict | None = None) -> Any:
        r = await self._client.get(path, params=params)
        return await self._raise_for_status(r)

    async def post(self, path: str, json: Any = None) -> Any:
        """Send a JSON body POST."""
        r = await self._client.post(
            path, json=json,
            headers={"Content-Type": "application/json"},
        )
        return await self._raise_for_status(r)

    async def post_form(
        self,
        path: str,
        data: dict | None = None,
        files: dict | None = None,
    ) -> Any:
        """Send a multipart/form-data or urlencoded POST.

        httpx will set the correct Content-Type (including boundary for
        multipart) automatically when ``files`` is provided.
        """
        r = await self._client.post(path, data=data, files=files)
        return await self._raise_for_status(r)

    async def patch(self, path: str, json: Any = None) -> Any:
        r = await self._client.patch(
            path, json=json,
            headers={"Content-Type": "application/json"},
        )
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

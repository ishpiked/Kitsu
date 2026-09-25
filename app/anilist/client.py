from typing import Any
import httpx
from app.config.settings import settings


class AniListError(Exception):
    def __init__(self, message: str, status_code: int | None = None, errors: list[dict] | None = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.errors = errors


class AniListRateLimitError(AniListError):
    def __init__(self, retry_after: int | None = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.retry_after = retry_after


class AniListClient:
    def __init__(self):
        self._client: httpx.AsyncClient | None = None
        self._base_url = "https://graphql.anilist.co"
        self._timeout = httpx.Timeout(30.0, connect=10.0)

    async def __aenter__(self) -> "AniListClient":
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.close()

    async def start(self) -> None:
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self._base_url,
                timeout=self._timeout,
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                },
            )

    async def close(self) -> None:
        if self._client:
            await self._client.aclose()
            self._client = None

    async def _request(self, query: str, variables: dict | None = None, headers: dict | None = None) -> dict[str, Any]:
        if not self._client:
            await self.start()

        payload = {"query": query}
        if variables:
            payload["variables"] = variables

        request_headers = {}
        if headers:
            request_headers.update(headers)

        try:
            response = await self._client.post("", json=payload, headers=request_headers)
        except httpx.TimeoutException as e:
            raise AniListError("Request timeout", status_code=408) from e
        except httpx.RequestError as e:
            raise AniListError(f"Request failed: {e}", status_code=500) from e

        if response.status_code == 429:
            retry_after = response.headers.get("Retry-After")
            raise AniListRateLimitError(
                "Rate limited",
                status_code=429,
                retry_after=int(retry_after) if retry_after else None,
            )

        if response.status_code >= 500:
            raise AniListError(f"Server error: {response.status_code}", status_code=response.status_code)

        try:
            data = response.json()
        except ValueError as e:
            raise AniListError("Invalid JSON response", status_code=response.status_code) from e

        if "errors" in data:
            errors = data["errors"]
            messages = [err.get("message", "Unknown error") for err in errors]
            raise AniListError("; ".join(messages), status_code=response.status_code, errors=errors)

        return data.get("data", {})

    async def health_check(self) -> bool:
        try:
            query = """
            query {
                SiteStatistics {
                    users
                }
            }
            """
            await self._request(query)
            return True
        except AniListError:
            return False

    async def execute_query(self, query: str, variables: dict | None = None) -> dict[str, Any]:
        return await self._request(query, variables)

    async def execute_mutation(self, query: str, variables: dict | None = None, access_token: str | None = None) -> dict[str, Any]:
        headers = {}
        if access_token:
            headers["Authorization"] = f"Bearer {access_token}"
        return await self._request(query, variables, headers)


async def get_anilist_client() -> AniListClient:
    client = AniListClient()
    await client.start()
    return client


async def close_anilist_client(client: AniListClient) -> None:
    await client.close()
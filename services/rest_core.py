import httpx


class RestCore:
    """Async HTTP client wrapper for REST API operations."""

    def __init__(self, BASE_URL: str):
        self.BASE_URL = BASE_URL
        self.client = httpx.AsyncClient()

    async def get(self, endpoint, params=None, headers=None):
        """Send GET request to endpoint."""
        return await self.client.get(
            self.BASE_URL + endpoint, params=params, headers=headers
        )

    async def basic_auth(self, endpoint, username, password):
        """Send POST request with basic authentication."""
        return await self.client.post(
            self.BASE_URL + endpoint, auth=(username, password)
        )

    async def post(self, endpoint, data=None, headers=None):
        """Send POST request to endpoint."""
        return await self.client.post(
            self.BASE_URL + endpoint, json=data, headers=headers
        )

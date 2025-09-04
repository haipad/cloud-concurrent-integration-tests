import asyncio
from typing import Dict, List

import httpx
from models.models import Token
from services.rest_core import RestCore

import time


class TokenService(RestCore):
    _BASE_URL = "http://localhost:8000"
    _tokens: Dict[str, Token] = {}
    _lock = None
    _instance = None
    MAX_RETRIES = 2

    def __init__(self, BASE_URL: str = _BASE_URL):
        super().__init__(BASE_URL)
    
    @classmethod
    async def get_instance(cls):
        if cls._instance is None:
            cls._instance = TokenService()
            cls._lock = asyncio.Lock()
        return cls._instance

    async def get_current_token(self, user, password) -> str:
        if user not in self._tokens or (time.time() - self._tokens[user].creation_ts) >= self._tokens[user].expiry_sec:
            async with TokenService._lock:
                # Double-check after acquiring lock
                if user not in self._tokens or (time.time() - self._tokens[user].creation_ts) >= self._tokens[user].expiry_sec:                    
                    # Perform authentication
                    response = await self.authenticate(user, password)
                    self._tokens[user] = Token(
                            access_token=response.json()["access_token"],
                            expiry_sec=response.json()["expires_in"],
                            creation_ts=time.time()
                        )
                    return self._tokens[user].access_token
                else:
                    return self._tokens[user].access_token
        else:
            return self._tokens[user].access_token

    async def authenticate(self, user, password, retry=0) -> str:
        if retry >= self.MAX_RETRIES:
            raise Exception(f"Failed to fetch token. Maximum authentication retries {self.MAX_RETRIES} exceeded")
        
        if user not in self._tokens:
            print(f"Performing authentication for the user {user}")
        else:
            print(f"Expired Token for {user}. Refreshing!!")
        
        response = await self.basic_auth("/token", user, password)
        
        if response.status_code == httpx.codes.OK:
            return response
        elif response.status_code == httpx.codes.TOO_MANY_REQUESTS:
            # Retry if 429 status code is returned
            rem_time = response.headers.get("Retry-After", "60")
            print(f"Token for the user already exist in the server (probably from previous session). Waiting for {rem_time} seconds to retry!")
            await asyncio.sleep(int(rem_time))
            return await self.authenticate(user, password, retry + 1)
        else:
            raise Exception("Failed to fetch token")

import aiohttp
from aws_iam_auth import AWSIamAuth
import json


class AppSyncClient:
    def __init__(
        self,
        endpoint: str,
        auth: AWSIamAuth = None,
    ):
        self.endpoint = endpoint
        self.auth = auth
        self.headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

    def __request_body(self, query: str, variables: dict = None) -> dict:
        json = {"query": query}

        if variables:
            json["variables"] = variables

        return json

    async def execute_async(
        self,
        query: str,
        variables: dict = None,
        headers: dict = {},
    ):

        request_body = self.__request_body(query=query, variables=variables)

        if self.auth:
            auth_headers = self.auth.generate_auth_headers(
                method="POST",
                content_type=self.headers["Content-Type"],
                body=json.dumps(request_body).encode(),
            )
            self.headers = {**self.headers, **auth_headers}

        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.endpoint,
                json=request_body,
                headers={**self.headers, **headers},
            ) as response:
                return await response.json()

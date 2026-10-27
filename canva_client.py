from __future__ import annotations

import json
from typing import Any
from urllib.parse import urlencode

import requests


class CanvaAPIError(RuntimeError):
    def __init__(self, message: str, status_code: int | None = None, payload: Any = None):
        super().__init__(message)
        self.status_code = status_code
        self.payload = payload


class CanvaClient:
    def __init__(
        self,
        client_id: str,
        client_secret: str,
        redirect_uri: str,
        access_token: str | None = None,
        refresh_token: str | None = None,
        base_url: str = "https://api.canva.com/rest/v1",
    ) -> None:
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.base_url = base_url.rstrip("/")
        self.oauth_base = "https://www.canva.com/api/oauth"

    def get_authorize_url(self, scopes: str = "app:read", state: str | None = None) -> str:
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "scope": scopes,
            "state": state or "streamlit-demo",
        }
        return f"{self.oauth_base}/authorize?{urlencode(params)}"

    def exchange_code_for_token(self, code: str) -> dict[str, Any]:
        response = requests.post(
            f"{self.oauth_base}/token",
            data={
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "code": code,
                "grant_type": "authorization_code",
                "redirect_uri": self.redirect_uri,
            },
            timeout=30,
        )
        return self._handle_token_response(response)

    def refresh_access_token(self) -> dict[str, Any]:
        if not self.refresh_token:
            raise CanvaAPIError("Refresh token is missing.")

        response = requests.post(
            f"{self.oauth_base}/token",
            data={
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "grant_type": "refresh_token",
                "refresh_token": self.refresh_token,
            },
            timeout=30,
        )
        token_data = self._handle_token_response(response)
        self.access_token = token_data.get("access_token")
        self.refresh_token = token_data.get("refresh_token") or self.refresh_token
        return token_data

    def request(self, method: str, path: str, *, data: Any | None = None, params: dict[str, Any] | None = None) -> Any:
        if not self.access_token:
            raise CanvaAPIError("No Canva access token is available.")

        url = f"{self.base_url}/{path.lstrip('/')}"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Accept": "application/json",
        }
        if data is not None:
            headers["Content-Type"] = "application/json"
            json_body = json.dumps(data)
        else:
            json_body = None

        response = requests.request(
            method=method.upper(),
            url=url,
            headers=headers,
            params=params,
            data=json_body,
            timeout=30,
        )
        try:
            payload = response.json()
        except ValueError:
            payload = response.text

        if response.status_code >= 400:
            raise CanvaAPIError(
                f"Canva API request failed with status {response.status_code}.",
                response.status_code,
                payload,
            )

        return payload

    @staticmethod
    def _handle_token_response(response: requests.Response) -> dict[str, Any]:
        try:
            payload = response.json()
        except ValueError:
            payload = {"raw_response": response.text}

        if response.status_code >= 400:
            raise CanvaAPIError(
                f"Canva OAuth request failed with status {response.status_code}.",
                response.status_code,
                payload,
            )
        return payload

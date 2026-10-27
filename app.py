from __future__ import annotations

import json
import os
from typing import Any

import streamlit as st

from canva_client import CanvaAPIError, CanvaClient

st.set_page_config(page_title="Canva API Demo", page_icon="🎨", layout="wide")


def load_config() -> dict[str, Any]:
    secrets = st.secrets.get("canva", {}) if hasattr(st, "secrets") else {}
    config = {
        "client_id": os.getenv("CANVA_CLIENT_ID") or secrets.get("client_id", ""),
        "client_secret": os.getenv("CANVA_CLIENT_SECRET") or secrets.get("client_secret", ""),
        "redirect_uri": os.getenv("CANVA_REDIRECT_URI") or secrets.get("redirect_uri", "http://localhost:8501"),
        "access_token": os.getenv("CANVA_ACCESS_TOKEN") or secrets.get("access_token", ""),
        "refresh_token": os.getenv("CANVA_REFRESH_TOKEN") or secrets.get("refresh_token", ""),
        "base_url": os.getenv("CANVA_BASE_URL") or secrets.get("base_url", "https://api.canva.com/rest/v1"),
    }
    return config


def get_client() -> CanvaClient:
    config = load_config()
    return CanvaClient(
        client_id=config["client_id"],
        client_secret=config["client_secret"],
        redirect_uri=config["redirect_uri"],
        access_token=config["access_token"] or st.session_state.get("access_token"),
        refresh_token=config["refresh_token"] or st.session_state.get("refresh_token"),
        base_url=config["base_url"],
    )


def persist_tokens(token_payload: dict[str, Any]) -> None:
    st.session_state["access_token"] = token_payload.get("access_token")
    st.session_state["refresh_token"] = token_payload.get("refresh_token") or st.session_state.get("refresh_token")
    st.session_state["token_payload"] = token_payload


st.title("Canva REST API + Streamlit Demo")

config = load_config()
if not config["client_id"] or not config["client_secret"]:
    st.warning(
        "Add your Canva client ID and client secret under Streamlit secrets as [canva] or set CANVA_CLIENT_ID / CANVA_CLIENT_SECRET."
    )

with st.sidebar:
    st.header("Configuration")
    st.caption("Use the same values configured in the Canva app dashboard.")
    st.text_input("Client ID", key="client_id", value=config["client_id"])
    st.text_input("Client Secret", key="client_secret", value=config["client_secret"], type="password")
    st.text_input("Redirect URI", key="redirect_uri", value=config["redirect_uri"])
    st.text_input("Base URL", key="base_url", value=config["base_url"])

    if st.button("Save config to session"):
        st.session_state["config"] = {
            "client_id": st.session_state["client_id"],
            "client_secret": st.session_state["client_secret"],
            "redirect_uri": st.session_state["redirect_uri"],
            "base_url": st.session_state["base_url"],
        }
        st.success("Settings updated for this session.")

params = st.query_params
if "code" in params:
    code = params["code"]
    try:
        client = CanvaClient(
            client_id=st.session_state.get("client_id") or config["client_id"],
            client_secret=st.session_state.get("client_secret") or config["client_secret"],
            redirect_uri=st.session_state.get("redirect_uri") or config["redirect_uri"],
            base_url=st.session_state.get("base_url") or config["base_url"],
        )
        token_payload = client.exchange_code_for_token(code)
        persist_tokens(token_payload)
        st.success("Authentication successful. You can now call the Canva API.")
        st.query_params.clear()
    except CanvaAPIError as exc:
        st.error(f"Authentication failed: {exc}")

if st.button("Authorize with Canva"):
    if not (st.session_state.get("client_id") or config["client_id"]) or not (st.session_state.get("client_secret") or config["client_secret"]):
        st.warning("Set the client ID and secret first.")
        st.stop()

    client = CanvaClient(
        client_id=st.session_state.get("client_id") or config["client_id"],
        client_secret=st.session_state.get("client_secret") or config["client_secret"],
        redirect_uri=st.session_state.get("redirect_uri") or config["redirect_uri"],
        base_url=st.session_state.get("base_url") or config["base_url"],
    )
    authorize_url = client.get_authorize_url(scopes="app:read")
    st.link_button("Open Canva OAuth page", authorize_url)

if st.session_state.get("access_token"):
    st.success("Canva access token available.")
    st.code(json.dumps({"access_token": st.session_state["access_token"][:12] + "..."}, indent=2))

    st.subheader("Call the Canva REST API")
    method = st.selectbox("HTTP method", ["GET", "POST", "PUT", "DELETE"])
    endpoint = st.text_input("Endpoint path", value="users/me")
    json_body = st.text_area("JSON body", value="{}")

    if st.button("Invoke API"):
        try:
            payload = json.loads(json_body) if json_body.strip() else None
            response = get_client().request(method, endpoint, data=payload)
            st.subheader("Response")
            st.json(response)
        except Exception as exc:  # pragma: no cover - UI feedback
            st.error(f"Request failed: {exc}")

    st.subheader("Browser-side fetch example")
    js_snippet = f"""
    const token = "{st.session_state.get('access_token', '')}";
    fetch("https://api.canva.com/rest/v1/{endpoint}", {{
      method: "{method}",
      headers: {{
        "Authorization": `Bearer ${token}`,
        "Content-Type": "application/json"
      }},
      body: {json_body if json_body.strip() else 'undefined'}
    }})
      .then((response) => response.json())
      .then((data) => console.log(data))
      .catch((error) => console.error(error));
    """
    st.code(js_snippet, language="javascript")
else:
    st.info("Authenticate with Canva to enable API requests.")

st.caption(
    "This app is a starter pattern for Shopify/Canva OAuth + REST requests. For production, store the tokens server-side and validate the redirect state."
)

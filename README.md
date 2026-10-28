# Canva REST API + Streamlit Starter

# Considerations - please read

-Takes time to set up 
-Troubleshooting API and authentication
-Half a day job maybe 
-Can use Canva in app - via chatgpt - Claude integrations combined with ffempeg for animations - might be easier than Streamlit + canva API combination

This repo contains a minimal Streamlit app that demonstrates:

- Canva OAuth authorization code flow
- session-based token handling
- calling the Canva REST API from Python
- generating a browser-side `fetch()` example for front-end use

## Files

- `app.py` — main Streamlit UI and auth flow
- `canva_client.py` — Canva OAuth + REST helper client
- `.streamlit/config.toml` — Streamlit server settings
- `.streamlit/secrets.toml.example` — reference for Cloud secrets
- `requirements.txt` — Python dependencies

## Local run

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## Canva app setup

1. Create a Canva app in the Canva developer console.
2. Configure OAuth redirect URIs.
3. Copy your Client ID and Client Secret.
4. For local testing, set redirect URI to `http://localhost:8501`.
5. For Streamlit Community Cloud, set redirect URI to the deployed app URL, for example:
   `https://<your-app-name>.streamlit.app`

## Streamlit Community Cloud secrets

In Streamlit Cloud, go to Settings → Secrets and add:

```toml
[canva]
client_id = "..."
client_secret = "..."
redirect_uri = "https://<your-app-name>.streamlit.app"
access_token = ""
refresh_token = ""
base_url = "https://api.canva.com/rest/v1"
```

## Important notes

- Streamlit Community Cloud does not allow a dynamic localhost callback.
- Keep the redirect URI identical in Canva settings and the app config.
- For production, store tokens server-side and validate `state` during OAuth.
- The browser-side examples in the app show how to attach a bearer token with `fetch()`.

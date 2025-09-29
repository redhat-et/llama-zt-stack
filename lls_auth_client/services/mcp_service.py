# lls_auth_client/services/mcp_service.py

from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.responses import JSONResponse
import jwt, logging

app = FastAPI(title="Weather MCP Server")

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp-service")

# Dummy secret for signing/validating tokens
SECRET = "super-secret-key"
ALGORITHM = "HS256"

# Define supported scopes
SCOPES = ["weather:current", "weather:forecast"]

# ---- Metadata endpoint ----
@app.get("/.well-known/oauth-protected-resource")
async def metadata():
    return {
        "resource": "http://localhost:8001",
        "authorization_servers": ["http://localhost:8002"],  # dummy value
        "jwks_uri": "http://localhost:8002/.well-known/jwks.json",
        "scopes_supported": SCOPES,
        "bearer_methods_supported": ["header"],
    }

# ---- Token validation + scope enforcement ----
def validate_token(authorization: str = Header(..., alias="Authorization")):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid token format")
    token = authorization.split(" ")[1]

    try:
        payload = jwt.decode(token, SECRET, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

    return payload

def requires_scope(required_scope: str):
    def wrapper(payload=Depends(validate_token)):
        token_scopes = payload.get("scope", "").split()
        if required_scope not in token_scopes:
            logger.warning(
                f"❌ Access denied. Required: {required_scope}, Got: {token_scopes}"
            )
            raise HTTPException(
                status_code=403,
                detail=f"Insufficient scope. Required: {required_scope}, Got: {token_scopes}",
            )
        logger.info(
            f"✅ Access granted. Required: {required_scope}, Got: {token_scopes}"
        )
        return payload
    return wrapper

# ---- Tool: Current weather ----
@app.get("/tools/current")
async def get_current_weather(user=Depends(requires_scope("weather:current"))):
    return {"temp_celsius": 22, "condition": "Sunny"}

# ---- Tool: Forecast ----
@app.get("/tools/forecast")
async def get_weather_forecast(user=Depends(requires_scope("weather:forecast"))):
    return {
        "forecast": [
            {"day": "tomorrow", "temp_celsius": 20, "condition": "Cloudy"},
            {"day": "day_after", "temp_celsius": 18, "condition": "Rain"},
            {"day": "in_3_days", "temp_celsius": 21, "condition": "Partly Cloudy"},
        ]
    }

import hashlib
import json
import os

from fastapi import Header, HTTPException


TENANTS_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "tenants")


async def verify_api_key(x_api_key: str = Header(...)) -> str:
    """Verify the API key and return the associated tenant_id."""
    key_hash = hashlib.sha256(x_api_key.encode()).hexdigest()

    if not os.path.isdir(TENANTS_DIR):
        raise HTTPException(status_code=401, detail="Invalid API key")

    for filename in os.listdir(TENANTS_DIR):
        if not filename.endswith(".json"):
            continue
        path = os.path.join(TENANTS_DIR, filename)
        with open(path, "r") as f:
            data = json.load(f)
        if data.get("api_key_hash") == key_hash:
            return data["tenant_id"]

    raise HTTPException(status_code=401, detail="Invalid API key")


def validate_widget_access(tenant_data: dict, origin: str | None) -> str | None:
    """Validate widget access based on tenant security settings.

    Returns None if access is allowed, or an error message string if denied.
    """
    # Check origin if enforcement is enabled
    if tenant_data.get("enforce_origin_check"):
        allowed = tenant_data.get("allowed_origins", [])
        if not allowed:
            return "No allowed origins configured but origin check is enforced"
        if not origin:
            return "Origin header required"
        if origin not in allowed:
            return f"Origin '{origin}' not allowed"

    return None


def validate_widget_api_key(tenant_data: dict, widget_key: str | None) -> str | None:
    """Validate the X-Widget-Key header against the tenant's stored hash.

    Returns None if valid (or no key required), or an error message if denied.
    """
    widget_key_hash = tenant_data.get("widget_api_key_hash")
    if not widget_key_hash:
        return None  # No key configured, skip check

    if not widget_key:
        return "Widget API key required"

    provided_hash = hashlib.sha256(widget_key.encode()).hexdigest()
    if provided_hash != widget_key_hash:
        return "Invalid widget API key"

    return None


def build_csp_header(tenant_data: dict) -> str | None:
    """Build Content-Security-Policy frame-ancestors value from allowed_origins.

    Returns the header value string, or None if no origins configured.
    """
    origins = tenant_data.get("allowed_origins", [])
    if not origins:
        return None
    return "frame-ancestors " + " ".join(origins)

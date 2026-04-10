import hashlib
import json
import os
import secrets

from fastapi import APIRouter, Depends, Header, HTTPException, Request
from fastapi.responses import JSONResponse

from app.models.schemas import TenantConfig
from app.routers.admin_auth import verify_admin_token
from app.auth import validate_widget_access, validate_widget_api_key, build_csp_header

router = APIRouter(prefix="/api/tenants", tags=["Tenants"])

TENANTS_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data", "tenants")
os.makedirs(TENANTS_DIR, exist_ok=True)


def _get_tenant_path(tenant_id: str) -> str:
    return os.path.join(TENANTS_DIR, f"{tenant_id}.json")


@router.post("/create", dependencies=[Depends(verify_admin_token)])
async def create_tenant(config: TenantConfig):
    """Create or update a tenant configuration."""
    path = _get_tenant_path(config.tenant_id)
    with open(path, "w") as f:
        json.dump(config.model_dump(), f, indent=2)
    return {"message": f"Tenant '{config.tenant_id}' configured successfully"}


@router.get("/{tenant_id}")
async def get_tenant(tenant_id: str, request: Request, x_widget_key: str | None = Header(None)):
    """Get tenant configuration. Public — used by the widget."""
    path = _get_tenant_path(tenant_id)
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail=f"Tenant '{tenant_id}' not found")
    with open(path, "r") as f:
        data = json.load(f)

    # Validate origin
    origin = request.headers.get("origin")
    origin_error = validate_widget_access(data, origin)
    if origin_error:
        raise HTTPException(status_code=403, detail=origin_error)

    # Validate widget API key
    key_error = validate_widget_api_key(data, x_widget_key)
    if key_error:
        raise HTTPException(status_code=401, detail=key_error)

    # Build response — exclude sensitive hashes
    config = TenantConfig(**data)
    response_data = config.model_dump()
    response_data.pop("api_key_hash", None)
    response_data.pop("widget_api_key_hash", None)

    response = JSONResponse(content=response_data)

    # Add CSP header
    csp = build_csp_header(data)
    if csp:
        response.headers["Content-Security-Policy"] = csp

    return response


@router.put("/{tenant_id}", dependencies=[Depends(verify_admin_token)])
async def update_tenant(tenant_id: str, updates: dict):
    """Update tenant configuration. Tenant ID is immutable."""
    path = _get_tenant_path(tenant_id)
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail=f"Tenant '{tenant_id}' not found")

    with open(path, "r") as f:
        data = json.load(f)

    # Prevent tenant_id from being changed
    updates.pop("tenant_id", None)
    # Don't allow overwriting key hashes via this endpoint
    updates.pop("api_key_hash", None)
    updates.pop("widget_api_key_hash", None)

    data.update(updates)

    # Validate the merged config
    config = TenantConfig(**data)
    with open(path, "w") as f:
        json.dump(config.model_dump(), f, indent=2)

    return {"message": f"Tenant '{tenant_id}' updated successfully"}


@router.post("/{tenant_id}/api-key", dependencies=[Depends(verify_admin_token)])
async def generate_api_key(tenant_id: str):
    """Generate an API key for a tenant. Protected by admin JWT auth."""

    path = _get_tenant_path(tenant_id)
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail=f"Tenant '{tenant_id}' not found")

    api_key = f"fai_{secrets.token_urlsafe(32)}"
    key_hash = hashlib.sha256(api_key.encode()).hexdigest()

    with open(path, "r") as f:
        data = json.load(f)
    data["api_key_hash"] = key_hash
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

    return {
        "tenant_id": tenant_id,
        "api_key": api_key,
        "message": "Save this key now — it cannot be retrieved again.",
    }


@router.post("/{tenant_id}/widget-api-key", dependencies=[Depends(verify_admin_token)])
async def generate_widget_api_key(tenant_id: str):
    """Generate a widget API key for a tenant. Protected by admin JWT auth."""
    path = _get_tenant_path(tenant_id)
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail=f"Tenant '{tenant_id}' not found")

    widget_key = f"wk_{secrets.token_urlsafe(32)}"
    key_hash = hashlib.sha256(widget_key.encode()).hexdigest()

    with open(path, "r") as f:
        data = json.load(f)
    data["widget_api_key_hash"] = key_hash
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

    return {
        "tenant_id": tenant_id,
        "widget_api_key": widget_key,
        "message": "Save this key now — it cannot be retrieved again.",
    }


@router.get("/", dependencies=[Depends(verify_admin_token)])
async def list_tenants():
    """List all configured tenants."""
    tenants = []
    for f in os.listdir(TENANTS_DIR):
        if f.endswith(".json"):
            with open(os.path.join(TENANTS_DIR, f), "r") as fh:
                data = json.load(fh)
                tenants.append({
                    "tenant_id": data.get("tenant_id"),
                    "display_name": data.get("display_name"),
                    "help_mode_enabled": data.get("help_mode_enabled"),
                    "data_mode_enabled": data.get("data_mode_enabled"),
                })
    return {"tenants": tenants}

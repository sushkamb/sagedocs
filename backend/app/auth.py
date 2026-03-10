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

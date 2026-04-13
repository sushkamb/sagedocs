# Widget Embedding Security — Design Spec

**Date:** 2026-04-10
**Status:** Approved

## Overview

Add security mechanisms for SageDocs widget embedding: domain whitelisting per tenant, widget API keys, CSP frame-ancestors headers, and tenant configuration editing in the admin dashboard.

## Schema Changes

Add to `TenantConfig` in `backend/app/models/schemas.py`:

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `allowed_origins` | `list[str]` | `[]` | Domains allowed to embed the widget (e.g. `https://myapp.com`) |
| `enforce_origin_check` | `bool` | `False` | When `False`, origin validation is skipped (dev-friendly) |
| `widget_api_key_hash` | `Optional[str]` | `None` | SHA-256 hash of widget API key |

## New API Endpoints

### `PUT /api/tenants/{tenant_id}` (Admin JWT required)

Update any tenant configuration fields. Tenant ID is immutable.

### `POST /api/tenants/{tenant_id}/widget-api-key` (Admin JWT required)

Generate a new widget API key. Returns the raw key once (prefix `wk_`). Only the SHA-256 hash is stored.

## Security Validation

Applied to `GET /api/tenants/{tenant_id}` and all `/api/chat/*` endpoints:

### 1. Origin Check

- If `enforce_origin_check` is `True`: validate the `Origin` request header against the tenant's `allowed_origins` list. Reject with 403 if no match.
- If `enforce_origin_check` is `False`: skip validation.
- `allowed_origins` entries must include protocol (e.g. `https://example.com`).

### 2. Widget API Key

- If tenant has `widget_api_key_hash` set: require `X-Widget-Key` header. Validate via SHA-256 hash comparison. Reject with 401 if missing or invalid.
- If no widget key configured: skip validation.

### 3. CSP frame-ancestors Header

- If `allowed_origins` is non-empty: add `Content-Security-Policy: frame-ancestors <space-separated origins>` to the response.
- If empty: omit header.

## Widget Changes

- New `widgetApiKey` option in `SageDocs.init()` config.
- Sent as `X-Widget-Key` header on all requests (config fetch + chat).

## Admin Dashboard Changes

### Edit Tenant

- Clicking a tenant in the list opens a form pre-filled with all current configuration.
- Same form as create, but in edit mode. Submits via `PUT /api/tenants/{tenant_id}`.
- Tenant ID field is read-only in edit mode.

### Expanded Form Fields

All existing fields plus:

- **Allowed Origins**: textarea, one origin per line.
- **Enforce Origin Check**: toggle switch.
- **Widget API Key**: generate button. Displays key once after generation.

### Create Flow

Also includes the new security fields.

## Validation Rules

- `allowed_origins` entries must include protocol.
- Widget API key format: `wk_{urlsafe_base64_32_bytes}` (distinguishable from admin `fai_` keys).
- Tenant ID is immutable after creation.

## Test File

Create `test/widget-test.html` with widget initialization including `widgetApiKey` parameter for local testing.

## Files Modified

- `backend/app/models/schemas.py` — new fields on TenantConfig
- `backend/app/routers/tenants.py` — PUT endpoint, widget-api-key endpoint, origin/key validation, CSP headers
- `backend/app/routers/chat.py` — origin/key validation, CSP headers
- `widget/sagedocs-widget.js` — widgetApiKey support in init and API calls
- `admin/index.html` — edit tenant flow, expanded form fields
- `test/widget-test.html` — new test file
- `docs/DESIGN.md` — updated documentation
- `CLAUDE.md` — updated if needed

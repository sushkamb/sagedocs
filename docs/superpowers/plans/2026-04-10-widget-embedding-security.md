# Widget Embedding Security Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add domain whitelisting, widget API keys, and CSP headers to secure widget embedding, plus tenant editing in the admin dashboard.

**Architecture:** Security validation is implemented as a shared helper function called from both the tenant config GET and chat endpoints. The widget sends an optional `X-Widget-Key` header. The admin dashboard gets an edit mode for the tenant modal.

**Tech Stack:** Python/FastAPI, vanilla JS

---

### Task 1: Add Security Fields to TenantConfig Schema

**Files:**
- Modify: `backend/app/models/schemas.py:36-53`

- [ ] **Step 1: Add new fields to TenantConfig**

Add three fields after `api_key_hash`:

```python
class TenantConfig(BaseModel):
    tenant_id: str
    display_name: str
    welcome_message: str = "Hi! How can I help you?"
    placeholder_text: str = "Ask me anything..."
    starter_questions: list[str] = []
    widget_position: str = "bottom-right"
    primary_color: str = "#0066cc"
    logo_url: Optional[str] = None
    help_mode_enabled: bool = True
    data_mode_enabled: bool = False
    llm_model: Optional[str] = None
    system_prompt: Optional[str] = None
    help_temperature: Optional[float] = None
    data_temperature: Optional[float] = None
    rag_top_k: Optional[int] = None
    similarity_threshold: Optional[float] = None
    api_key_hash: Optional[str] = None
    # Widget embedding security
    allowed_origins: list[str] = []
    enforce_origin_check: bool = False
    widget_api_key_hash: Optional[str] = None
```

- [ ] **Step 2: Verify existing tenants still load**

Run: `cd /Applications/XAMPP/xamppfiles/htdocs/personal/sagedocs/backend && source venv/bin/activate && python -c "from app.models.schemas import TenantConfig; t = TenantConfig(tenant_id='test', display_name='Test'); print(t.allowed_origins, t.enforce_origin_check, t.widget_api_key_hash)"`

Expected: `[] False None`

- [ ] **Step 3: Commit**

```bash
git add backend/app/models/schemas.py
git commit -m "feat: add security fields to TenantConfig schema"
```

---

### Task 2: Add Widget Security Validation Helper

**Files:**
- Modify: `backend/app/auth.py`

- [ ] **Step 1: Add widget security validation function**

Add this function to `backend/app/auth.py` after the existing `verify_api_key` function:

```python
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

    # Check widget API key if tenant has one set
    widget_key_hash = tenant_data.get("widget_api_key_hash")
    if widget_key_hash:
        # Caller must provide the key — this function only validates the tenant config side.
        # The actual header extraction happens in the endpoint.
        pass

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
```

- [ ] **Step 2: Verify imports are present**

The file already imports `hashlib`. Confirm no new imports needed.

- [ ] **Step 3: Commit**

```bash
git add backend/app/auth.py
git commit -m "feat: add widget security validation helpers"
```

---

### Task 3: Secure the Tenant Config GET Endpoint

**Files:**
- Modify: `backend/app/routers/tenants.py`

- [ ] **Step 1: Add imports and update get_tenant endpoint**

Add these imports at the top of `tenants.py`:

```python
from fastapi import APIRouter, Depends, Header, HTTPException, Request
from fastapi.responses import JSONResponse

from app.auth import validate_widget_access, validate_widget_api_key, build_csp_header
```

Replace the existing `get_tenant` endpoint:

```python
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
```

- [ ] **Step 2: Verify the endpoint loads without errors**

Run: `cd /Applications/XAMPP/xamppfiles/htdocs/personal/sagedocs/backend && source venv/bin/activate && python -c "from app.routers.tenants import router; print('OK')"`

Expected: `OK`

- [ ] **Step 3: Commit**

```bash
git add backend/app/routers/tenants.py
git commit -m "feat: add origin and widget key validation to tenant config endpoint"
```

---

### Task 4: Secure the Chat Endpoints

**Files:**
- Modify: `backend/app/routers/chat.py`

- [ ] **Step 1: Add security validation to chat router**

Add imports at the top of `chat.py`:

```python
import json
import logging
import os
import uuid

from fastapi import APIRouter, Header, HTTPException, Request
from fastapi.responses import JSONResponse

from app.models.schemas import ChatRequest, ChatResponse
from app.services.rag_engine import RAGEngine
from app.services.query_engine import QueryEngine
from app.routers.analytics import log_question
from app.auth import validate_widget_access, validate_widget_api_key, build_csp_header
```

Add a helper to load tenant data and validate, placed after the engine instantiations:

```python
TENANTS_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data", "tenants")


def _load_and_validate_tenant(tenant_id: str, origin: str | None, widget_key: str | None) -> dict:
    """Load tenant config and validate widget access. Returns tenant data dict."""
    path = os.path.join(TENANTS_DIR, f"{tenant_id}.json")
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail=f"Tenant '{tenant_id}' not found")

    with open(path, "r") as f:
        data = json.load(f)

    origin_error = validate_widget_access(data, origin)
    if origin_error:
        raise HTTPException(status_code=403, detail=origin_error)

    key_error = validate_widget_api_key(data, widget_key)
    if key_error:
        raise HTTPException(status_code=401, detail=key_error)

    return data
```

- [ ] **Step 2: Update the main chat endpoint**

Replace the `chat` endpoint:

```python
@router.post("/")
async def chat(request: ChatRequest, req: Request, x_widget_key: str | None = Header(None)):
    """Main chat endpoint — routes to help mode or data mode based on intent."""

    origin = req.headers.get("origin")
    tenant_data = _load_and_validate_tenant(request.tenant, origin, x_widget_key)

    session_id = request.session_id or str(uuid.uuid4())
    logger.info("Chat request: tenant=%s mode=%s message=%r",
                request.tenant,
                "unified" if (request.account_number and request.token) else "help",
                request.message[:120])

    if request.account_number and request.token:
        result = await _unified_chat(request)
    else:
        result = rag_engine.query(request.tenant, request.message)

    answered = bool(result.get("sources")) or bool(result.get("reply"))
    log_question(request.tenant, request.message, answered)

    logger.info("Chat response: answered=%s sources=%d reply_len=%d",
                answered, len(result.get("sources", [])), len(result.get("reply", "")))

    response = JSONResponse(content={
        "reply": result["reply"],
        "sources": result.get("sources", []),
        "images": result.get("images", []),
        "session_id": session_id,
    })

    csp = build_csp_header(tenant_data)
    if csp:
        response.headers["Content-Security-Policy"] = csp

    return response
```

- [ ] **Step 3: Update the help-only endpoint**

Replace the `chat_help` endpoint:

```python
@router.post("/help")
async def chat_help(request: ChatRequest, req: Request, x_widget_key: str | None = Header(None)):
    """Help mode only — answers from documentation."""

    origin = req.headers.get("origin")
    tenant_data = _load_and_validate_tenant(request.tenant, origin, x_widget_key)

    session_id = request.session_id or str(uuid.uuid4())
    result = rag_engine.query(request.tenant, request.message)

    answered = bool(result.get("sources"))
    log_question(request.tenant, request.message, answered)

    response = JSONResponse(content={
        "reply": result["reply"],
        "sources": result.get("sources", []),
        "images": result.get("images", []),
        "session_id": session_id,
    })

    csp = build_csp_header(tenant_data)
    if csp:
        response.headers["Content-Security-Policy"] = csp

    return response
```

- [ ] **Step 4: Update the data-only endpoint**

Replace the `chat_data` endpoint:

```python
@router.post("/data")
async def chat_data(request: ChatRequest, req: Request, x_widget_key: str | None = Header(None)):
    """Data mode only — answers by querying host app API."""

    if not request.account_number or not request.token:
        raise HTTPException(status_code=400, detail="account_number and token are required for data queries")

    origin = req.headers.get("origin")
    tenant_data = _load_and_validate_tenant(request.tenant, origin, x_widget_key)

    session_id = request.session_id or str(uuid.uuid4())

    result = await query_engine.query(
        tenant=request.tenant,
        question=request.message,
        account_number=request.account_number,
        token=request.token,
    )

    answered = bool(result.get("reply"))
    log_question(request.tenant, request.message, answered)

    response = JSONResponse(content={
        "reply": result["reply"],
        "sources": result.get("sources", []),
        "images": result.get("images", []),
        "session_id": session_id,
    })

    csp = build_csp_header(tenant_data)
    if csp:
        response.headers["Content-Security-Policy"] = csp

    return response
```

- [ ] **Step 5: Commit**

```bash
git add backend/app/routers/chat.py
git commit -m "feat: add widget security validation to chat endpoints"
```

---

### Task 5: Add PUT Tenant and Widget API Key Endpoints

**Files:**
- Modify: `backend/app/routers/tenants.py`

- [ ] **Step 1: Add the PUT update endpoint**

Add after the `get_tenant` endpoint in `tenants.py`:

```python
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
```

- [ ] **Step 2: Add the widget API key generation endpoint**

Add after the existing `generate_api_key` endpoint:

```python
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
```

- [ ] **Step 3: Commit**

```bash
git add backend/app/routers/tenants.py
git commit -m "feat: add PUT tenant update and widget API key generation endpoints"
```

---

### Task 6: Update Widget JS to Send X-Widget-Key Header

**Files:**
- Modify: `widget/sagedocs-widget.js`

- [ ] **Step 1: Add widgetApiKey to init defaults**

In the `init` function, add `widgetApiKey` to the defaults object (after the `target` line):

```javascript
this.config = Object.assign({
    tenant: "",
    accountNumber: "",
    token: "",
    theme: "light",
    position: "bottom-right",
    apiUrl: "",
    welcomeMessage: "Hi! How can I help you?",
    placeholder: "Ask me anything...",
    starterQuestions: [],
    inline: false,
    target: null,
    widgetApiKey: ""
}, options);
```

- [ ] **Step 2: Add helper method for building headers**

Add a new method to the SageDocs object (after the `destroy` method):

```javascript
_buildHeaders: function () {
    var headers = { "Content-Type": "application/json" };
    if (this.config.widgetApiKey) {
        headers["X-Widget-Key"] = this.config.widgetApiKey;
    }
    return headers;
},
```

- [ ] **Step 3: Update _fetchTenantConfig to send widget key**

Replace the fetch call in `_fetchTenantConfig`:

```javascript
_fetchTenantConfig: function () {
    var self = this;
    if (!this.config.tenant) return;

    var fetchOpts = {};
    if (this.config.widgetApiKey) {
        fetchOpts.headers = { "X-Widget-Key": this.config.widgetApiKey };
    }

    fetch(this.config.apiUrl + "/api/tenants/" + this.config.tenant, fetchOpts)
        .then(function (r) { return r.ok ? r.json() : null; })
        .then(function (data) {
            if (data) {
                self.config.welcomeMessage = data.welcome_message || self.config.welcomeMessage;
                self.config.placeholder = data.placeholder_text || self.config.placeholder;
                self.config.starterQuestions = data.starter_questions || self.config.starterQuestions;
                self._updateWelcome();
            }
        })
        .catch(function () { /* tenant config not found, use defaults */ });
},
```

- [ ] **Step 4: Update _sendMessage to send widget key**

Replace the fetch call in `_sendMessage`:

```javascript
fetch(this.config.apiUrl + "/api/chat/", {
    method: "POST",
    headers: self._buildHeaders(),
    body: JSON.stringify(body)
})
```

- [ ] **Step 5: Commit**

```bash
git add widget/sagedocs-widget.js
git commit -m "feat: add widgetApiKey support to widget JS"
```

---

### Task 7: Update Admin Dashboard — Edit Tenant Modal

**Files:**
- Modify: `admin/index.html`

This is the largest task. The admin dashboard needs:
1. The modal to support edit mode (pre-filled fields, tenant ID read-only)
2. New security fields added to the modal
3. An edit button for each tenant in the tenant selector area
4. The create/save button to call POST (create) or PUT (update) based on mode

- [ ] **Step 1: Update the modal HTML**

Replace the entire `<!-- CREATE TENANT MODAL -->` section (lines 74-148) with:

```html
<!-- TENANT MODAL (Create / Edit) -->
<div class="modal-overlay" id="tenantModal">
    <div class="modal">
        <div class="modal-header">
            <h2 id="tenantModalTitle">Create Tenant</h2>
            <button class="modal-close" id="tenantModalClose">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
            </button>
        </div>
        <div class="modal-body">
            <div id="tenantCreateStatus" class="modal-status"></div>

            <div class="form-row">
                <div class="form-group">
                    <label class="form-label">Tenant ID</label>
                    <input type="text" id="newTenantId" class="form-input" placeholder="e.g. chirocloud" />
                    <div class="form-hint">Lowercase, no spaces. Used as the API key.</div>
                </div>
                <div class="form-group">
                    <label class="form-label">Display Name</label>
                    <input type="text" id="newTenantName" class="form-input" placeholder="e.g. ChiroCloud" />
                </div>
            </div>

            <div class="form-group">
                <label class="form-label">Welcome Message</label>
                <input type="text" id="newTenantWelcome" class="form-input" placeholder="Hi! How can I help you?" />
            </div>

            <div class="form-group">
                <label class="form-label">Placeholder Text</label>
                <input type="text" id="newTenantPlaceholder" class="form-input" placeholder="Ask me anything..." />
            </div>

            <div class="form-group">
                <label class="form-label">Starter Questions</label>
                <textarea id="newTenantStarters" class="form-input" rows="3" placeholder="One question per line"></textarea>
                <div class="form-hint">One question per line. These appear as quick-action buttons in the widget.</div>
            </div>

            <div class="form-group">
                <label class="form-label">Primary Color</label>
                <div class="color-input-wrap">
                    <input type="color" id="newTenantColorPicker" value="#0066cc" />
                    <input type="text" id="newTenantColor" class="form-input" value="#0066cc" placeholder="#0066cc" />
                </div>
            </div>

            <div class="form-group">
                <label class="form-label">Modes</label>
                <div class="toggle-row">
                    <div>
                        <div class="toggle-label">Help Mode</div>
                        <div class="toggle-desc">RAG over uploaded documentation</div>
                    </div>
                    <label class="toggle-switch">
                        <input type="checkbox" id="newTenantHelp" checked />
                        <span class="toggle-slider"></span>
                    </label>
                </div>
                <div class="toggle-row">
                    <div>
                        <div class="toggle-label">Data Mode</div>
                        <div class="toggle-desc">LLM function calling against APIs</div>
                    </div>
                    <label class="toggle-switch">
                        <input type="checkbox" id="newTenantData" />
                        <span class="toggle-slider"></span>
                    </label>
                </div>
            </div>

            <div class="form-group">
                <label class="form-label">Similarity Threshold</label>
                <input type="number" id="newTenantThreshold" class="form-input" placeholder="0.65" min="0" max="1" step="0.05" />
                <div class="form-hint">Max cosine distance for RAG results (0-1). Lower = stricter matching. Leave blank for default (0.65).</div>
            </div>

            <hr style="border:none; border-top:1px solid var(--border); margin:16px 0;" />

            <div style="font-weight:600; margin-bottom:12px;">Widget Security</div>

            <div class="form-group">
                <label class="form-label">Allowed Origins</label>
                <textarea id="newTenantOrigins" class="form-input" rows="3" placeholder="https://myapp.com&#10;http://localhost:3000"></textarea>
                <div class="form-hint">One origin per line. Include protocol (e.g. https://example.com).</div>
            </div>

            <div class="form-group">
                <div class="toggle-row">
                    <div>
                        <div class="toggle-label">Enforce Origin Check</div>
                        <div class="toggle-desc">When off, origin validation is skipped (useful for development)</div>
                    </div>
                    <label class="toggle-switch">
                        <input type="checkbox" id="newTenantEnforceOrigin" />
                        <span class="toggle-slider"></span>
                    </label>
                </div>
            </div>

            <div class="form-group" id="widgetKeyGroup" style="display:none;">
                <label class="form-label">Widget API Key</label>
                <div id="widgetKeyStatus" style="font-size:13px; color:var(--text-muted); margin-bottom:8px;">
                    A widget API key is configured for this tenant.
                </div>
                <button class="btn btn-secondary" id="generateWidgetKeyBtn" type="button">Generate New Widget API Key</button>
                <div id="widgetKeyDisplay" style="display:none; margin-top:8px;">
                    <div style="font-size:12px; color:#ef4444; font-weight:500; margin-bottom:4px;">Save this key now — it cannot be retrieved again:</div>
                    <code id="widgetKeyValue" style="display:block; padding:8px 12px; background:var(--bg-secondary); border-radius:6px; font-size:13px; word-break:break-all;"></code>
                </div>
            </div>
        </div>
        <div class="modal-footer">
            <button class="btn btn-secondary" id="tenantModalCancel">Cancel</button>
            <button class="btn btn-primary" id="tenantSaveBtn">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
                <span id="tenantSaveBtnText">Create Tenant</span>
            </button>
        </div>
    </div>
</div>
```

- [ ] **Step 2: Add Edit button next to tenant selector**

Replace the `sidebar-tenant-row` div (lines 31-38) with:

```html
<div class="sidebar-tenant-row">
    <select id="tenantSelect">
        <option value="">Select tenant...</option>
    </select>
    <button class="btn-add-tenant" id="btnEditTenant" title="Edit tenant settings" style="display:none;">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>
    </button>
    <button class="btn-add-tenant" id="btnAddTenant" title="Create new tenant">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
    </button>
</div>
```

- [ ] **Step 3: Replace the entire `<script>` section**

Replace everything inside `<script>...</script>` (lines 268-689) with the updated JavaScript that supports create/edit modes. The full replacement:

```javascript
// ═══ THEME TOGGLE ═══
function updateThemeUI(theme) {
    var isDark = theme === "dark";
    document.getElementById("themeIconSun").style.display = isDark ? "block" : "none";
    document.getElementById("themeIconMoon").style.display = isDark ? "none" : "block";
    document.getElementById("themeLabel").textContent = isDark ? "Light Mode" : "Dark Mode";
}

document.addEventListener("DOMContentLoaded", function () {
    var current = document.documentElement.getAttribute("data-theme") || "light";
    updateThemeUI(current);

    document.getElementById("themeToggle").addEventListener("click", function () {
        var isDark = document.documentElement.getAttribute("data-theme") === "dark";
        var next = isDark ? "light" : "dark";
        if (next === "dark") {
            document.documentElement.setAttribute("data-theme", "dark");
        } else {
            document.documentElement.removeAttribute("data-theme");
        }
        localStorage.setItem("sagedocs-theme", next);
        updateThemeUI(next);
    });
});

var API_BASE = window.location.origin;
var ADMIN_TOKEN = sessionStorage.getItem("sagedocs_admin_token");

// ═══ AUTH CHECK ═══
if (!ADMIN_TOKEN) {
    window.location.href = "/admin/login.html";
} else {
    fetch(API_BASE + "/api/admin/verify", {
        headers: { "Authorization": "Bearer " + ADMIN_TOKEN }
    }).then(function (r) {
        if (!r.ok) {
            sessionStorage.removeItem("sagedocs_admin_token");
            window.location.href = "/admin/login.html";
        }
    }).catch(function () {
        sessionStorage.removeItem("sagedocs_admin_token");
        window.location.href = "/admin/login.html";
    });
}

function authHeaders(extra) {
    var h = { "Authorization": "Bearer " + ADMIN_TOKEN };
    if (extra) { for (var k in extra) h[k] = extra[k]; }
    return h;
}

function authFetch(url, opts) {
    opts = opts || {};
    opts.headers = authHeaders(opts.headers);
    return fetch(url, opts).then(function (r) {
        if (r.status === 401) {
            sessionStorage.removeItem("sagedocs_admin_token");
            window.location.href = "/admin/login.html";
        }
        return r;
    });
}

var currentTenant = "";
var tenantModalMode = "create"; // "create" or "edit"

var pageTitles = {
    documents: { title: "Documents", subtitle: "Upload and manage help documentation" },
    test: { title: "Test Chat", subtitle: "Test your AI assistant responses" },
    analytics: { title: "Analytics", subtitle: "Track question coverage and content gaps" }
};

// ═══ LOGOUT ═══
document.getElementById("logoutBtn").addEventListener("click", function () {
    sessionStorage.removeItem("sagedocs_admin_token");
    window.location.href = "/admin/login.html";
});

// ═══ NAV SWITCHING ═══
document.querySelectorAll(".nav-item[data-tab]").forEach(function (btn) {
    btn.addEventListener("click", function () {
        document.querySelectorAll(".nav-item[data-tab]").forEach(function (b) { b.classList.remove("active"); });
        document.querySelectorAll(".tab-content").forEach(function (c) { c.classList.remove("active"); });
        btn.classList.add("active");
        var tab = btn.dataset.tab;
        document.getElementById("tab-" + tab).classList.add("active");
        document.getElementById("pageTitle").textContent = pageTitles[tab].title;
        document.getElementById("pageSubtitle").textContent = pageTitles[tab].subtitle;
    });
});

// ═══ UPLOAD AREA ═══
var uploadArea = document.getElementById("uploadArea");

uploadArea.addEventListener("click", function () {
    document.getElementById("fileInput").click();
});

uploadArea.addEventListener("dragover", function (e) {
    e.preventDefault();
    this.classList.add("drag-over");
});

uploadArea.addEventListener("dragleave", function () {
    this.classList.remove("drag-over");
});

uploadArea.addEventListener("drop", function (e) {
    e.preventDefault();
    this.classList.remove("drag-over");
    if (e.dataTransfer.files.length > 0) {
        document.getElementById("fileInput").files = e.dataTransfer.files;
        document.getElementById("fileInput").dispatchEvent(new Event("change"));
    }
});

document.getElementById("fileInput").addEventListener("change", function () {
    var file = this.files[0];
    var placeholder = document.getElementById("uploadPlaceholder");
    var fileInfo = document.getElementById("uploadFileInfo");

    if (file) {
        var sizeStr = file.size > 1048576 ? (file.size / 1048576).toFixed(1) + " MB" : (file.size / 1024).toFixed(1) + " KB";
        document.getElementById("uploadFileName").textContent = file.name;
        document.getElementById("uploadFileSize").textContent = sizeStr;
        placeholder.style.display = "none";
        fileInfo.style.display = "block";
        uploadArea.classList.add("has-file");
    } else {
        placeholder.style.display = "block";
        fileInfo.style.display = "none";
        uploadArea.classList.remove("has-file");
    }
    setUploadStatus("", "");
});

// ═══ TENANTS ═══
function loadTenants() {
    return authFetch(API_BASE + "/api/tenants/")
        .then(function (r) { return r.json(); })
        .then(function (data) {
            var sel = document.getElementById("tenantSelect");
            var prev = sel.value;
            sel.innerHTML = '<option value="">Select tenant...</option>';
            (data.tenants || []).forEach(function (t) {
                var opt = document.createElement("option");
                opt.value = t.tenant_id;
                opt.textContent = t.display_name || t.tenant_id;
                sel.appendChild(opt);
            });
            if (prev) {
                sel.value = prev;
            }
            return data.tenants || [];
        });
}

loadTenants();

document.getElementById("tenantSelect").addEventListener("change", function () {
    currentTenant = this.value;
    document.getElementById("btnEditTenant").style.display = currentTenant ? "flex" : "none";
    if (currentTenant) {
        loadDocuments();
        loadAnalytics();
        mountTestChat(currentTenant);
    }
});

// ═══ TENANT MODAL (Create / Edit) ═══
var tenantModal = document.getElementById("tenantModal");

function resetTenantModal() {
    setTenantCreateStatus("", "");
    document.getElementById("newTenantId").value = "";
    document.getElementById("newTenantId").readOnly = false;
    document.getElementById("newTenantId").style.opacity = "1";
    document.getElementById("newTenantId").dataset.manual = "";
    document.getElementById("newTenantName").value = "";
    document.getElementById("newTenantWelcome").value = "";
    document.getElementById("newTenantPlaceholder").value = "";
    document.getElementById("newTenantStarters").value = "";
    document.getElementById("newTenantColor").value = "#0066cc";
    document.getElementById("newTenantColorPicker").value = "#0066cc";
    document.getElementById("newTenantHelp").checked = true;
    document.getElementById("newTenantData").checked = false;
    document.getElementById("newTenantThreshold").value = "";
    document.getElementById("newTenantOrigins").value = "";
    document.getElementById("newTenantEnforceOrigin").checked = false;
    document.getElementById("widgetKeyGroup").style.display = "none";
    document.getElementById("widgetKeyDisplay").style.display = "none";
    document.getElementById("widgetKeyValue").textContent = "";
}

function openTenantModal(mode, tenantData) {
    tenantModalMode = mode;
    resetTenantModal();

    if (mode === "edit" && tenantData) {
        document.getElementById("tenantModalTitle").textContent = "Edit Tenant";
        document.getElementById("tenantSaveBtnText").textContent = "Save Changes";

        document.getElementById("newTenantId").value = tenantData.tenant_id;
        document.getElementById("newTenantId").readOnly = true;
        document.getElementById("newTenantId").style.opacity = "0.6";
        document.getElementById("newTenantName").value = tenantData.display_name || "";
        document.getElementById("newTenantWelcome").value = tenantData.welcome_message || "";
        document.getElementById("newTenantPlaceholder").value = tenantData.placeholder_text || "";
        document.getElementById("newTenantStarters").value = (tenantData.starter_questions || []).join("\n");
        document.getElementById("newTenantColor").value = tenantData.primary_color || "#0066cc";
        document.getElementById("newTenantColorPicker").value = tenantData.primary_color || "#0066cc";
        document.getElementById("newTenantHelp").checked = tenantData.help_mode_enabled !== false;
        document.getElementById("newTenantData").checked = !!tenantData.data_mode_enabled;
        document.getElementById("newTenantThreshold").value = tenantData.similarity_threshold != null ? tenantData.similarity_threshold : "";
        document.getElementById("newTenantOrigins").value = (tenantData.allowed_origins || []).join("\n");
        document.getElementById("newTenantEnforceOrigin").checked = !!tenantData.enforce_origin_check;

        // Show widget key section in edit mode
        document.getElementById("widgetKeyGroup").style.display = "block";
        if (tenantData.widget_api_key_hash) {
            document.getElementById("widgetKeyStatus").textContent = "A widget API key is configured for this tenant.";
        } else {
            document.getElementById("widgetKeyStatus").textContent = "No widget API key configured.";
        }
    } else {
        document.getElementById("tenantModalTitle").textContent = "Create Tenant";
        document.getElementById("tenantSaveBtnText").textContent = "Create Tenant";
    }

    tenantModal.classList.add("open");
    if (mode === "create") {
        setTimeout(function () { document.getElementById("newTenantId").focus(); }, 150);
    } else {
        setTimeout(function () { document.getElementById("newTenantName").focus(); }, 150);
    }
}

function closeTenantModal() {
    tenantModal.classList.remove("open");
}

document.getElementById("btnAddTenant").addEventListener("click", function () {
    openTenantModal("create");
});

document.getElementById("btnEditTenant").addEventListener("click", function () {
    if (!currentTenant) return;
    // Fetch full tenant config for editing
    authFetch(API_BASE + "/api/tenants/" + currentTenant)
        .then(function (r) { return r.json(); })
        .then(function (data) {
            openTenantModal("edit", data);
        });
});

document.getElementById("tenantModalClose").addEventListener("click", closeTenantModal);
document.getElementById("tenantModalCancel").addEventListener("click", closeTenantModal);

tenantModal.addEventListener("click", function (e) {
    if (e.target === tenantModal) closeTenantModal();
});

document.addEventListener("keydown", function (e) {
    if (e.key === "Escape" && tenantModal.classList.contains("open")) closeTenantModal();
});

// Sync color picker <-> text input
document.getElementById("newTenantColorPicker").addEventListener("input", function () {
    document.getElementById("newTenantColor").value = this.value;
});

document.getElementById("newTenantColor").addEventListener("input", function () {
    if (/^#[0-9a-fA-F]{6}$/.test(this.value)) {
        document.getElementById("newTenantColorPicker").value = this.value;
    }
});

// Auto-slug tenant ID from display name (only in create mode)
document.getElementById("newTenantName").addEventListener("input", function () {
    if (tenantModalMode === "create") {
        var idField = document.getElementById("newTenantId");
        if (!idField.dataset.manual) {
            idField.value = this.value.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");
        }
    }
});

document.getElementById("newTenantId").addEventListener("input", function () {
    this.dataset.manual = "1";
});

function setTenantCreateStatus(msg, type) {
    var el = document.getElementById("tenantCreateStatus");
    if (!type) { el.className = "modal-status"; el.textContent = ""; return; }
    el.textContent = msg;
    el.className = "modal-status " + type;
}

// ═══ GENERATE WIDGET API KEY ═══
document.getElementById("generateWidgetKeyBtn").addEventListener("click", function () {
    var btn = this;
    var tenantId = document.getElementById("newTenantId").value.trim();
    if (!tenantId) return;

    if (!confirm("Generate a new widget API key? This will invalidate any existing widget key.")) return;

    btn.disabled = true;
    btn.classList.add("btn-loading");

    authFetch(API_BASE + "/api/tenants/" + tenantId + "/widget-api-key", { method: "POST" })
        .then(function (r) {
            if (!r.ok) throw new Error("Failed (HTTP " + r.status + ")");
            return r.json();
        })
        .then(function (data) {
            document.getElementById("widgetKeyDisplay").style.display = "block";
            document.getElementById("widgetKeyValue").textContent = data.widget_api_key;
            document.getElementById("widgetKeyStatus").textContent = "A widget API key is configured for this tenant.";
        })
        .catch(function (err) {
            setTenantCreateStatus("Error generating widget key: " + err.message, "error");
        })
        .finally(function () {
            btn.disabled = false;
            btn.classList.remove("btn-loading");
        });
});

// ═══ SAVE TENANT (Create or Update) ═══
document.getElementById("tenantSaveBtn").addEventListener("click", function () {
    var btn = this;
    var tenantId = document.getElementById("newTenantId").value.trim();
    var displayName = document.getElementById("newTenantName").value.trim();

    if (!tenantId || !displayName) {
        setTenantCreateStatus("Tenant ID and Display Name are required.", "error");
        return;
    }

    if (tenantModalMode === "create" && !/^[a-z0-9][a-z0-9-]*[a-z0-9]$|^[a-z0-9]$/.test(tenantId)) {
        setTenantCreateStatus("Tenant ID must be lowercase letters, numbers, and hyphens only.", "error");
        return;
    }

    var startersRaw = document.getElementById("newTenantStarters").value.trim();
    var starters = startersRaw ? startersRaw.split("\n").map(function (s) { return s.trim(); }).filter(Boolean) : [];

    var originsRaw = document.getElementById("newTenantOrigins").value.trim();
    var origins = originsRaw ? originsRaw.split("\n").map(function (s) { return s.trim(); }).filter(Boolean) : [];

    var payload = {
        tenant_id: tenantId,
        display_name: displayName,
        welcome_message: document.getElementById("newTenantWelcome").value.trim() || "Hi! How can I help you?",
        placeholder_text: document.getElementById("newTenantPlaceholder").value.trim() || "Ask me anything...",
        starter_questions: starters,
        primary_color: document.getElementById("newTenantColor").value.trim() || "#0066cc",
        help_mode_enabled: document.getElementById("newTenantHelp").checked,
        data_mode_enabled: document.getElementById("newTenantData").checked,
        similarity_threshold: document.getElementById("newTenantThreshold").value ? parseFloat(document.getElementById("newTenantThreshold").value) : null,
        allowed_origins: origins,
        enforce_origin_check: document.getElementById("newTenantEnforceOrigin").checked
    };

    btn.disabled = true;
    btn.classList.add("btn-loading");

    var url, method;
    if (tenantModalMode === "edit") {
        url = API_BASE + "/api/tenants/" + tenantId;
        method = "PUT";
    } else {
        url = API_BASE + "/api/tenants/create";
        method = "POST";
    }

    authFetch(url, {
        method: method,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
    })
    .then(function (r) {
        if (!r.ok) throw new Error("Failed (HTTP " + r.status + ")");
        return r.json();
    })
    .then(function () {
        var verb = tenantModalMode === "edit" ? "updated" : "created";
        setTenantCreateStatus("Tenant '" + displayName + "' " + verb + " successfully.", "success");
        loadTenants().then(function () {
            document.getElementById("tenantSelect").value = tenantId;
            currentTenant = tenantId;
            document.getElementById("btnEditTenant").style.display = "flex";
        });
        setTimeout(closeTenantModal, 1200);
    })
    .catch(function (err) {
        setTenantCreateStatus("Error: " + err.message, "error");
    })
    .finally(function () {
        btn.disabled = false;
        btn.classList.remove("btn-loading");
        document.getElementById("newTenantId").dataset.manual = "";
    });
});

// ═══ DOCUMENTS ═══
function getFileExt(filename) {
    var ext = filename.split(".").pop().toLowerCase();
    if (ext === "htm") ext = "html";
    return ext;
}

function loadDocuments() {
    authFetch(API_BASE + "/api/documents/list?tenant=" + currentTenant)
        .then(function (r) { return r.json(); })
        .then(function (data) {
            var list = document.getElementById("docList");
            var docs = data.documents || [];
            if (docs.length === 0) {
                list.innerHTML = '<li class="empty-state"><svg class="empty-state-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg><div class="empty-state-text">No documents indexed yet</div><div class="empty-state-hint">Upload a document above to get started</div></li>';
                return;
            }
            list.innerHTML = "";
            docs.forEach(function (doc) {
                var ext = getFileExt(doc.filename);
                var li = document.createElement("li");
                li.className = "doc-item";
                li.innerHTML =
                    '<div class="doc-item-left">' +
                        '<div class="doc-icon ' + ext + '">' + ext + '</div>' +
                        '<div><div class="doc-title">' + doc.title + '</div>' +
                        '<div class="doc-meta">' + doc.filename + ' &middot; ' + doc.chunk_count + ' chunks</div></div>' +
                    '</div>' +
                    '<button class="btn btn-ghost" onclick="deleteDoc(\'' + doc.filename + '\')">Delete</button>';
                list.appendChild(li);
            });
        });
}

function deleteDoc(filename) {
    if (!confirm("Delete " + filename + "?")) return;
    authFetch(API_BASE + "/api/documents/delete?tenant=" + currentTenant + "&filename=" + filename, { method: "DELETE" })
        .then(function () { loadDocuments(); });
}

// ═══ UPLOAD ═══
function setUploadStatus(message, type) {
    var el = document.getElementById("uploadStatus");
    if (!type) { el.className = "upload-status"; el.innerHTML = ""; return; }
    var spinner = type === "processing" ? '<span class="spinner-sm"></span>' : '';
    el.innerHTML = spinner + message;
    el.className = "upload-status " + type;
}

function resetUploadForm() {
    document.getElementById("docTitle").value = "";
    document.getElementById("fileInput").value = "";
    document.getElementById("uploadPlaceholder").style.display = "block";
    document.getElementById("uploadFileInfo").style.display = "none";
    uploadArea.classList.remove("has-file");
}

document.getElementById("uploadBtn").addEventListener("click", function () {
    var btn = this;
    var file = document.getElementById("fileInput").files[0];
    var title = document.getElementById("docTitle").value.trim();
    if (!file || !title || !currentTenant) {
        setUploadStatus("Please select a tenant, enter a title, and choose a file.", "error");
        return;
    }
    var fd = new FormData();
    fd.append("file", file);
    fd.append("tenant", currentTenant);
    fd.append("title", title);

    btn.disabled = true;
    btn.classList.add("btn-loading");
    setUploadStatus("Uploading and indexing document. This may take a minute if it contains images...", "processing");

    authFetch(API_BASE + "/api/documents/upload", { method: "POST", body: fd })
        .then(function (r) {
            if (!r.ok) throw new Error("Upload failed (HTTP " + r.status + ")");
            return r.json();
        })
        .then(function (data) {
            setUploadStatus(data.message || "Document uploaded and indexed successfully.", "success");
            resetUploadForm();
            loadDocuments();
        })
        .catch(function (err) {
            setUploadStatus("Error: " + err.message, "error");
        })
        .finally(function () {
            btn.disabled = false;
            btn.classList.remove("btn-loading");
        });
});

// ═══ TEST CHAT (mounts the embeddable SageDocs widget inline) ═══
function mountTestChat(tenant) {
    if (!tenant || typeof SageDocs === "undefined") return;
    SageDocs.init({
        tenant: tenant,
        apiUrl: API_BASE,
        inline: true,
        target: "#testChatHost"
    });
}

// ═══ ANALYTICS ═══
function loadAnalytics() {
    authFetch(API_BASE + "/api/analytics/summary?tenant=" + currentTenant)
        .then(function (r) { return r.json(); })
        .then(function (data) {
            document.getElementById("statTotal").textContent = data.total || 0;
            document.getElementById("statAnswered").textContent = data.answered || 0;
            document.getElementById("statUnanswered").textContent = data.unanswered || 0;
        });

    authFetch(API_BASE + "/api/analytics/questions?tenant=" + currentTenant + "&unanswered_only=true")
        .then(function (r) { return r.json(); })
        .then(function (data) {
            var list = document.getElementById("unansweredList");
            var questions = data.questions || [];
            if (questions.length === 0) {
                list.innerHTML = '<li class="empty-state"><svg class="empty-state-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg><div class="empty-state-text">All questions answered</div><div class="empty-state-hint">No content gaps detected</div></li>';
                return;
            }
            list.innerHTML = "";
            questions.slice(0, 50).forEach(function (q) {
                var li = document.createElement("li");
                li.className = "question-item";
                li.innerHTML =
                    '<span class="question-badge"></span>' +
                    '<div><div class="question-text">' + q.question + '</div>' +
                    '<div class="question-time">' + q.timestamp + '</div></div>';
                list.appendChild(li);
            });
        });
}
```

- [ ] **Step 4: Commit**

```bash
git add admin/index.html
git commit -m "feat: add edit tenant modal with security fields to admin dashboard"
```

---

### Task 8: Create Widget Test File

**Files:**
- Create: `test/widget-test.html`

- [ ] **Step 1: Create the test directory and file**

```bash
mkdir -p /Applications/XAMPP/xamppfiles/htdocs/personal/sagedocs/test
```

Create `test/widget-test.html`:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SageDocs Widget - Local Test</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f5f5; padding: 40px; }
        .container { max-width: 800px; margin: 0 auto; }
        h1 { font-size: 24px; margin-bottom: 8px; }
        p { color: #666; margin-bottom: 24px; }
        .config-panel { background: #fff; border-radius: 8px; padding: 24px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); margin-bottom: 24px; }
        .config-panel h2 { font-size: 16px; margin-bottom: 16px; }
        .form-row { display: flex; gap: 16px; margin-bottom: 12px; }
        .form-row > div { flex: 1; }
        label { display: block; font-size: 13px; font-weight: 600; margin-bottom: 4px; }
        input, select { width: 100%; padding: 8px 12px; border: 1px solid #ddd; border-radius: 6px; font-size: 14px; }
        button { background: #0066cc; color: #fff; border: none; padding: 10px 20px; border-radius: 6px; font-size: 14px; cursor: pointer; margin-top: 12px; }
        button:hover { background: #0052a3; }
        .hint { font-size: 12px; color: #999; margin-top: 4px; }
        .status { margin-top: 12px; padding: 8px 12px; border-radius: 6px; font-size: 13px; display: none; }
        .status.ok { display: block; background: #ecfdf5; color: #065f46; }
        .status.err { display: block; background: #fef2f2; color: #991b1b; }
    </style>
</head>
<body>
    <div class="container">
        <h1>SageDocs Widget - Local Test</h1>
        <p>Use this page to test the widget locally. Configure the settings below and click "Load Widget".</p>

        <div class="config-panel">
            <h2>Widget Configuration</h2>
            <div class="form-row">
                <div>
                    <label>API URL</label>
                    <input type="text" id="cfgApiUrl" value="http://localhost:8500" />
                </div>
                <div>
                    <label>Tenant</label>
                    <input type="text" id="cfgTenant" placeholder="e.g. chirocloud" />
                </div>
            </div>
            <div class="form-row">
                <div>
                    <label>Widget API Key</label>
                    <input type="text" id="cfgWidgetKey" placeholder="wk_... (optional)" />
                    <div class="hint">Required if the tenant has a widget API key configured.</div>
                </div>
                <div>
                    <label>Theme</label>
                    <select id="cfgTheme">
                        <option value="light">Light</option>
                        <option value="dark">Dark</option>
                    </select>
                </div>
            </div>
            <div class="form-row">
                <div>
                    <label>Account Number (optional)</label>
                    <input type="text" id="cfgAccount" placeholder="For data mode" />
                </div>
                <div>
                    <label>Token (optional)</label>
                    <input type="text" id="cfgToken" placeholder="JWT for data mode" />
                </div>
            </div>
            <div class="form-row">
                <div>
                    <label>Position</label>
                    <select id="cfgPosition">
                        <option value="bottom-right">Bottom Right</option>
                        <option value="bottom-left">Bottom Left</option>
                    </select>
                </div>
                <div></div>
            </div>
            <button onclick="loadWidget()">Load Widget</button>
            <div class="status" id="loadStatus"></div>
        </div>
    </div>

    <script src="/widget/sagedocs-widget.js"></script>
    <script>
        function loadWidget() {
            var tenant = document.getElementById("cfgTenant").value.trim();
            var statusEl = document.getElementById("loadStatus");

            if (!tenant) {
                statusEl.className = "status err";
                statusEl.textContent = "Tenant is required.";
                return;
            }

            var opts = {
                tenant: tenant,
                apiUrl: document.getElementById("cfgApiUrl").value.trim(),
                widgetApiKey: document.getElementById("cfgWidgetKey").value.trim(),
                theme: document.getElementById("cfgTheme").value,
                position: document.getElementById("cfgPosition").value
            };

            var account = document.getElementById("cfgAccount").value.trim();
            var token = document.getElementById("cfgToken").value.trim();
            if (account) opts.accountNumber = account;
            if (token) opts.token = token;

            SageDocs.init(opts);

            statusEl.className = "status ok";
            statusEl.textContent = "Widget loaded for tenant '" + tenant + "'. Click the chat button in the corner.";
        }
    </script>
</body>
</html>
```

- [ ] **Step 2: Commit**

```bash
git add test/widget-test.html
git commit -m "feat: add widget test page with security config options"
```

---

### Task 9: Update Documentation

**Files:**
- Modify: `docs/DESIGN.md`
- Modify: `CLAUDE.md`

- [ ] **Step 1: Update DESIGN.md security section**

In `docs/DESIGN.md`, add a new subsection after the existing Security section (5.4). Insert before `---` at line 218:

```markdown
- **Widget embedding security** — Per-tenant domain whitelisting (`allowed_origins`), widget API keys (`wk_` prefix, SHA-256 hashed), and CSP `frame-ancestors` headers on widget-facing endpoints. Origin enforcement is toggleable per tenant via `enforce_origin_check` flag.
```

- [ ] **Step 2: Update DESIGN.md widget integration section**

In section 6.1, update the widget integration example to include the widget API key:

```html
<script src="https://sagedocs.yourdomain.com/widget/sagedocs-widget.js"></script>
<script>
  SageDocs.init({
    tenant: 'chirocloud',
    accountNumber: '12345',
    token: '{jwt}',
    theme: 'light',
    widgetApiKey: 'wk_...'   // optional, required if tenant has widget key configured
  });
</script>
```

- [ ] **Step 3: Update DESIGN.md tenant-configurable options**

In section 6.3, add to the list:

```markdown
- Allowed origins (domain whitelist for widget embedding)
- Enforce origin check toggle
- Widget API key
```

- [ ] **Step 4: Update the project CLAUDE.md**

In `CLAUDE.md`, under "Key Patterns", add:

```markdown
- **Widget Security:** Per-tenant `allowed_origins` + `enforce_origin_check` flag + widget API keys (`wk_` prefix). Validation runs on `GET /api/tenants/{id}` and `/api/chat/*` endpoints.
```

- [ ] **Step 5: Commit**

```bash
git add docs/DESIGN.md CLAUDE.md
git commit -m "docs: update DESIGN.md and CLAUDE.md with widget security details"
```

---

### Task 10: Manual Integration Test

- [ ] **Step 1: Start the backend**

Run: `cd /Applications/XAMPP/xamppfiles/htdocs/personal/sagedocs/backend && source venv/bin/activate && uvicorn app.main:app --reload --port 8500`

- [ ] **Step 2: Verify existing tenant still loads**

Run: `curl -s http://localhost:8500/api/tenants/chirocloud | python -m json.tool`

Expected: JSON response with the new fields `allowed_origins`, `enforce_origin_check` defaulting to `[]` and `false`. Should NOT contain `api_key_hash` or `widget_api_key_hash`.

- [ ] **Step 3: Test the admin edit flow**

Open `http://localhost:8500/admin/` in browser. Select a tenant. Click the edit (pencil) button. Verify the form pre-fills with current config. Add an allowed origin, toggle enforce origin check. Save. Verify changes persist.

- [ ] **Step 4: Test widget API key generation**

In edit mode, click "Generate New Widget API Key". Verify a `wk_` prefixed key is displayed. Save the key.

- [ ] **Step 5: Test origin enforcement**

Update a tenant with `enforce_origin_check: true` and `allowed_origins: ["http://localhost:8500"]`. Then:

```bash
# Should succeed (matching origin)
curl -s -H "Origin: http://localhost:8500" http://localhost:8500/api/tenants/chirocloud

# Should fail with 403
curl -s -H "Origin: http://evil.com" http://localhost:8500/api/tenants/chirocloud
```

- [ ] **Step 6: Test widget API key enforcement**

After generating a widget key for the tenant:

```bash
# Should fail with 401 (no key)
curl -s http://localhost:8500/api/tenants/chirocloud

# Should succeed (with key)
curl -s -H "X-Widget-Key: wk_..." http://localhost:8500/api/tenants/chirocloud
```

- [ ] **Step 7: Test the widget test page**

Open `http://localhost:8500/test/widget-test.html` (needs static mount). Or open `test/widget-test.html` directly via the filesystem and configure the API URL.

- [ ] **Step 8: Verify CSP header**

```bash
curl -sI -H "X-Widget-Key: wk_..." http://localhost:8500/api/tenants/chirocloud | grep -i content-security
```

Expected: `Content-Security-Policy: frame-ancestors http://localhost:8500` (or whatever origins are configured)

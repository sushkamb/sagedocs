# Output Formatting Improvements — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Replace the widget's custom regex markdown renderer with marked.js + DOMPurify, add CSS for rich markdown elements, redesign sources as a collapsible section, and tune the RAG system prompt to produce better-structured markdown.

**Architecture:** Frontend-only for rendering (marked.js parses markdown, DOMPurify sanitizes HTML, CSS styles all elements). Backend change is limited to the RAG system prompt string in rag_engine.py. No new endpoints, no schema changes.

**Tech Stack:** marked.js v15.x (CDN), DOMPurify v3.x (CDN), vanilla JS, CSS

---

### Task 1: Load marked.js and DOMPurify via CDN

**Files:**
- Modify: `widget/forteai-widget.js:73-78` (`_loadStyles` method)

**Step 1: Add CDN script loading to `_loadStyles`**

Replace the `_loadStyles` method to also load the two JS libraries:

```javascript
_loadStyles: function () {
    var link = document.createElement("link");
    link.rel = "stylesheet";
    link.href = this.config.apiUrl + "/widget/forteai-widget.css";
    document.head.appendChild(link);

    // Load marked.js for markdown rendering
    var markedScript = document.createElement("script");
    markedScript.src = "https://cdn.jsdelivr.net/npm/marked@15/marked.min.js";
    document.head.appendChild(markedScript);

    // Load DOMPurify for HTML sanitization
    var purifyScript = document.createElement("script");
    purifyScript.src = "https://cdn.jsdelivr.net/npm/dompurify@3/dist/purify.min.js";
    document.head.appendChild(purifyScript);
},
```

**Step 2: Verify scripts load**

Run the FastAPI server: `cd /Applications/XAMPP/xamppfiles/htdocs/forte/forteaibot/backend && source venv/bin/activate && uvicorn app.main:app --reload --port 8500`

Open browser dev tools on a page that loads the widget. Confirm:
- Network tab shows both CDN scripts loaded (200 OK)
- Console: `typeof marked` returns `"object"` and `typeof DOMPurify` returns `"object"`

**Step 3: Commit**

```bash
git add widget/forteai-widget.js
git commit -m "feat(widget): load marked.js and DOMPurify via CDN"
```

---

### Task 2: Replace `_formatMarkdown` with marked.js

**Files:**
- Modify: `widget/forteai-widget.js:201-226` (`_formatMarkdown` method)

**Step 1: Replace the `_formatMarkdown` method**

Replace lines 201-226 with:

```javascript
_formatMarkdown: function (text) {
    // Use marked.js if loaded, otherwise fall back to basic escaping
    if (typeof marked !== "undefined" && typeof DOMPurify !== "undefined") {
        var renderer = new marked.Renderer();
        // Open all links in new tab
        renderer.link = function (token) {
            return '<a href="' + token.href + '" target="_blank" rel="noopener noreferrer">' + (token.text || token.href) + '</a>';
        };

        marked.setOptions({
            breaks: true,
            gfm: true,
            renderer: renderer
        });

        var rawHtml = marked.parse(text);
        return DOMPurify.sanitize(rawHtml, { ADD_ATTR: ['target'] });
    }

    // Fallback: basic HTML escaping if libraries not loaded yet
    return text
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/\n/g, "<br>");
},
```

**Step 2: Verify rendering works**

Open the widget and send a test message. The LLM response should now render:
- **Bold text** and *italic text*
- Bullet lists and numbered lists
- Code blocks with proper formatting
- Links should be clickable and open in new tabs

**Step 3: Commit**

```bash
git add widget/forteai-widget.js
git commit -m "feat(widget): replace custom markdown with marked.js + DOMPurify"
```

---

### Task 3: Replace old custom CSS with markdown element styles

**Files:**
- Modify: `widget/forteai-widget.css:320-395` (the "Formatted Message Content" section through end of file)

**Step 1: Replace the old custom formatting CSS**

Replace everything from `/* Formatted Message Content */` (line 320) to the `/* Responsive */` comment (line 389) with new styles. Keep the responsive media query at the end.

Remove these old classes entirely: `.forteai-list`, `.forteai-ul-item`, `.forteai-ol-item`, `.forteai-code-block`, `.forteai-inline-code` (marked.js outputs standard `<ul>`, `<ol>`, `<li>`, `<pre>`, `<code>` elements).

Replace with:

```css
/* Formatted Message Content — Markdown Elements */
.forteai-msg-text p {
    margin: 0 0 8px 0;
}

.forteai-msg-text p:last-child {
    margin-bottom: 0;
}

.forteai-msg-text strong {
    font-weight: 600;
}

/* Headings */
.forteai-msg-text h1,
.forteai-msg-text h2,
.forteai-msg-text h3,
.forteai-msg-text h4 {
    font-weight: 600;
    margin: 12px 0 6px 0;
    line-height: 1.3;
}

.forteai-msg-text h1 { font-size: 1.2em; }
.forteai-msg-text h2 { font-size: 1.1em; }
.forteai-msg-text h3 { font-size: 1.05em; }
.forteai-msg-text h4 { font-size: 1em; }

.forteai-msg-text h1:first-child,
.forteai-msg-text h2:first-child,
.forteai-msg-text h3:first-child,
.forteai-msg-text h4:first-child {
    margin-top: 0;
}

/* Lists */
.forteai-msg-text ul,
.forteai-msg-text ol {
    margin: 6px 0;
    padding-left: 20px;
}

.forteai-msg-text li {
    margin-bottom: 4px;
}

.forteai-msg-text li > ul,
.forteai-msg-text li > ol {
    margin: 2px 0;
}

/* Code */
.forteai-msg-text pre {
    background: rgba(0, 0, 0, 0.06);
    border-radius: 6px;
    padding: 8px 10px;
    font-family: "SFMono-Regular", Consolas, monospace;
    font-size: 12px;
    overflow-x: auto;
    margin: 6px 0;
    white-space: pre-wrap;
}

.forteai-msg-text code {
    background: rgba(0, 0, 0, 0.06);
    border-radius: 3px;
    padding: 1px 5px;
    font-family: "SFMono-Regular", Consolas, monospace;
    font-size: 12px;
}

.forteai-msg-text pre code {
    background: none;
    padding: 0;
    border-radius: 0;
}

/* Tables */
.forteai-msg-text table {
    border-collapse: collapse;
    width: 100%;
    margin: 8px 0;
    font-size: 13px;
    display: block;
    overflow-x: auto;
}

.forteai-msg-text th,
.forteai-msg-text td {
    border: 1px solid rgba(0, 0, 0, 0.12);
    padding: 6px 10px;
    text-align: left;
}

.forteai-msg-text th {
    background: rgba(0, 0, 0, 0.04);
    font-weight: 600;
}

.forteai-msg-text tr:nth-child(even) {
    background: rgba(0, 0, 0, 0.02);
}

/* Blockquotes */
.forteai-msg-text blockquote {
    border-left: 3px solid #0066cc;
    background: rgba(0, 102, 204, 0.05);
    margin: 8px 0;
    padding: 6px 12px;
    color: #555;
}

.forteai-msg-text blockquote p {
    margin: 0;
}

/* Links */
.forteai-msg-text a {
    color: #0066cc;
    text-decoration: none;
}

.forteai-msg-text a:hover {
    text-decoration: underline;
}

/* Horizontal Rules */
.forteai-msg-text hr {
    border: none;
    border-top: 1px solid rgba(0, 0, 0, 0.1);
    margin: 10px 0;
}
```

**Step 2: Verify visual rendering**

Open the widget and test with responses that contain various markdown elements. All should render cleanly within the chat bubble.

**Step 3: Commit**

```bash
git add widget/forteai-widget.css
git commit -m "feat(widget): add CSS for full markdown element support"
```

---

### Task 4: Replace source display with collapsible section

**Files:**
- Modify: `widget/forteai-widget.js:262-267` (source rendering in `_addMessage`)
- Modify: `widget/forteai-widget.css:165-170` (`.forteai-msg-sources` styles)

**Step 1: Update the source rendering in `_addMessage`**

Replace the source rendering block (lines 262-267) with:

```javascript
if (sources && sources.length > 0) {
    var srcDiv = document.createElement("div");
    srcDiv.className = "forteai-msg-sources";
    var details = document.createElement("details");
    var summary = document.createElement("summary");
    summary.innerHTML = '<span class="forteai-sources-icon">&#128196;</span> Sources (' + sources.length + ')';
    details.appendChild(summary);

    var srcList = document.createElement("div");
    srcList.className = "forteai-sources-list";
    sources.forEach(function (s) {
        var pill = document.createElement("span");
        pill.className = "forteai-source-pill";
        pill.textContent = s.title;
        srcList.appendChild(pill);
    });
    details.appendChild(srcList);
    srcDiv.appendChild(details);
    msgDiv.appendChild(srcDiv);
}
```

**Step 2: Replace the source CSS**

Replace the `.forteai-msg-sources` block (lines 165-170 in CSS) with:

```css
/* Collapsible Sources */
.forteai-msg-sources {
    margin-top: 6px;
    padding-left: 4px;
}

.forteai-msg-sources details {
    font-size: 12px;
    color: #666;
}

.forteai-msg-sources summary {
    cursor: pointer;
    user-select: none;
    font-weight: 500;
    padding: 4px 0;
    list-style: none;
}

.forteai-msg-sources summary::-webkit-details-marker {
    display: none;
}

.forteai-msg-sources summary::after {
    content: " \25B8";
}

.forteai-msg-sources details[open] summary::after {
    content: " \25BE";
}

.forteai-sources-icon {
    font-size: 13px;
}

.forteai-sources-list {
    display: flex;
    flex-wrap: wrap;
    gap: 4px;
    padding: 6px 0 2px 0;
}

.forteai-source-pill {
    background: #e8f0fe;
    color: #0066cc;
    border-radius: 12px;
    padding: 3px 10px;
    font-size: 11px;
    white-space: nowrap;
}
```

**Step 3: Verify collapsible sources**

Send a question that retrieves from documentation. Sources should:
- Appear as "Sources (N) ▸" collapsed by default
- Click to expand showing pills with source names
- Click again to collapse

**Step 4: Commit**

```bash
git add widget/forteai-widget.js widget/forteai-widget.css
git commit -m "feat(widget): collapsible sources with pill badges"
```

---

### Task 5: Tune RAG system prompt for structured markdown output

**Files:**
- Modify: `backend/app/services/rag_engine.py:185-196`

**Step 1: Update the system prompt rules**

Replace lines 185-196 with:

```python
system_prompt += (
    "## Rules\n"
    "- Answer ONLY based on the documentation provided below. Do not use outside knowledge.\n"
    "- If the documentation does not contain enough information to fully answer, clearly state what "
    "you found and what is missing, then suggest contacting support.\n"
    "- Structure your response with clear visual hierarchy:\n"
    "  - Use **bold** for key terms, UI labels, button names, and important values.\n"
    "  - Use `##` or `###` headings when covering multiple distinct topics or long answers.\n"
    "  - Use numbered steps (1. 2. 3.) for procedures and bullet points for lists.\n"
    "  - Use markdown tables when comparing options, features, or settings.\n"
    "  - Use blockquotes (> ) for important notes, warnings, or tips.\n"
    "  - Format navigation paths as: **Settings > Billing > Plans**\n"
    "- Keep responses concise — prefer structured formatting over long paragraphs.\n"
    "- When documentation includes [Screenshot: ...] markers, reference those visual descriptions "
    "to give specific UI guidance (e.g., 'click the blue **Save** button in the top-right corner').\n"
    "- Quote specific UI labels, button names, and menu paths exactly as they appear.\n"
    "- If multiple sources cover the topic, synthesize into a coherent answer.\n"
    "- Chunks marked HIGH relevance are most likely to contain the answer.\n\n"
    f"## Documentation (ordered by relevance)\n{context}"
)
```

**Step 2: Verify prompt produces better-structured output**

Restart the backend server. Ask a multi-step question (e.g., "How do I set up billing?"). The response should now contain:
- Headings for distinct sections
- Bold UI labels
- Numbered steps for procedures
- Blockquotes for important notes

**Step 3: Commit**

```bash
git add backend/app/services/rag_engine.py
git commit -m "feat(rag): tune system prompt for structured markdown output"
```

---

### Task 6: Manual E2E verification

**Files:** None (manual testing only)

**Step 1: Start the server**

```bash
cd /Applications/XAMPP/xamppfiles/htdocs/forte/forteaibot/backend
source venv/bin/activate
uvicorn app.main:app --reload --port 8500
```

**Step 2: Open the widget on a test page and verify these scenarios**

1. **Bold/italic** — Ask a simple question, confirm bold and italic text renders
2. **Lists** — Ask "what are the steps to..." and confirm numbered lists render with proper indentation
3. **Tables** — Ask a comparison question, confirm table renders with borders and alternating rows
4. **Links** — Confirm any URLs in responses are clickable and open in new tabs
5. **Code blocks** — If response contains code, confirm it renders in a monospace box
6. **Blockquotes** — Confirm any notes/warnings appear with a blue left border
7. **Headings** — Confirm multi-section answers have visible headings
8. **Sources** — Confirm collapsible "Sources (N)" appears, expands/collapses on click
9. **Images** — Confirm inline images still render and click-to-enlarge still works
10. **Fallback** — Temporarily block CDN in dev tools, confirm widget still works with basic text

**Step 3: Final commit if any fixes needed**

```bash
git add -A
git commit -m "fix(widget): address formatting edge cases from testing"
```

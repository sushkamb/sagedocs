# Output Formatting Improvements — Help Mode

**Date:** 2026-02-13
**Approach:** B — Frontend markdown library + backend prompt tuning + collapsible sources

## Problem

Help Mode responses suffer from:
- Wall of text — hard to scan, no visual hierarchy
- Missing formatting — tables, headings, blockquotes, links not rendered
- Non-clickable links
- Poor source display — plain gray text, not interactive

## Solution

### 1. Widget: Replace custom markdown renderer with marked.js

- Load `marked.min.js` (v15.x) and `DOMPurify` via CDN in `_loadStyles()`
- Replace `_formatMarkdown()` with `marked.parse()` + DOMPurify sanitization
- Configure marked: `breaks: true`, custom link renderer (`target="_blank"`, `rel="noopener"`)
- Remove old custom regex-based `_formatMarkdown()` function

### 2. Widget: CSS for markdown elements

Add scoped CSS (`.forteai-msg-text` prefix) for:
- Headings (h1–h4): scaled sizes, weight 600, margin-top
- Tables: bordered cells, alternating row backgrounds, horizontal scroll
- Blockquotes: left border accent (#0066cc), light background
- Links: theme color, underline on hover
- Horizontal rules: subtle divider
- Nested lists: proper indentation

Remove old custom list/code classes (`.forteai-list`, `.forteai-ul-item`, `.forteai-ol-item`) since marked.js outputs standard HTML elements.

### 3. Widget: Collapsible sources

Replace plain-text source line with `<details>/<summary>` element:
- Collapsed by default: "Sources (3) ▸"
- Expanded shows source names as styled pills
- Zero additional JS needed (native browser element)

### 4. Backend: System prompt tuning (rag_engine.py)

Update RAG system prompt rules to encourage structured markdown:
- Use `##` headings for multi-topic answers
- Use tables for comparisons, numbered steps for procedures
- Bold key terms and UI labels
- Format navigation as **Settings > Billing > Plans**
- Use blockquotes for notes/warnings
- Include markdown links when URLs exist in docs

## Files Changed

| File | Change |
|------|--------|
| `widget/forteai-widget.js` | Replace `_formatMarkdown()`, add CDN loading, update `_addMessage()` for sources |
| `widget/forteai-widget.css` | Add markdown element styles, remove old custom list/code classes |
| `backend/app/services/rag_engine.py` | Update system prompt rules (lines 185-196) |

## Dependencies

- marked.js v15.x via CDN (jsDelivr or cdnjs)
- DOMPurify v3.x via CDN

## Not In Scope

- Streaming/SSE (future enhancement)
- Rich answer cards (future enhancement)
- Data Mode formatting (separate effort)

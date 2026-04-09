/**
 * SageDocs Chat Widget
 * Embeddable chat widget for any web application.
 *
 * Floating mode (default) — adds a FAB + chat panel to the page:
 *   <script src="https://sagedocs.yourdomain.com/widget/sagedocs-widget.js"></script>
 *   <script>
 *     SageDocs.init({
 *       tenant: 'chirocloud',
 *       accountNumber: '12345',   // optional, enables data mode
 *       token: 'jwt-token',       // optional, enables data mode
 *       theme: 'light',           // 'light' or 'dark'
 *       position: 'bottom-right', // 'bottom-right' or 'bottom-left'
 *       apiUrl: 'https://sagedocs.yourdomain.com'
 *     });
 *   </script>
 *
 * Inline mode — render the chat panel inside an existing element (no FAB):
 *   SageDocs.init({
 *     tenant: 'chirocloud',
 *     inline: true,
 *     target: '#myChatHost'  // CSS selector or HTMLElement
 *   });
 *
 * Re-init (e.g. switch tenant) — call init() again; the previous instance is destroyed.
 */
(function () {
    "use strict";

    var SageDocs = {
        config: null,
        container: null,
        isOpen: false,
        sessionId: null,
        messages: [],

        init: function (options) {
            // Destroy any prior instance so init() can be called again (e.g. tenant switch)
            this.destroy();

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
                target: null
            }, options);

            if (!this.config.apiUrl) {
                var scripts = document.getElementsByTagName("script");
                for (var i = 0; i < scripts.length; i++) {
                    if (scripts[i].src && scripts[i].src.indexOf("sagedocs-widget.js") > -1) {
                        this.config.apiUrl = scripts[i].src.replace("/widget/sagedocs-widget.js", "");
                        break;
                    }
                }
            }

            this.sessionId = null;
            this.messages = [];
            this._loadStyles();
            this._fetchTenantConfig();
            this._render();
        },

        destroy: function () {
            if (this.container && this.container.parentNode) {
                this.container.parentNode.removeChild(this.container);
            }
            this.container = null;
            this.isOpen = false;
            this.sessionId = null;
            this.messages = [];
        },

        _fetchTenantConfig: function () {
            var self = this;
            if (!this.config.tenant) return;

            fetch(this.config.apiUrl + "/api/tenants/" + this.config.tenant)
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

        _loadStyles: function () {
            var self = this;
            if (!document.getElementById("sagedocs-widget-css")) {
                var link = document.createElement("link");
                link.id = "sagedocs-widget-css";
                link.rel = "stylesheet";
                link.href = this.config.apiUrl + "/widget/sagedocs-widget.css";
                document.head.appendChild(link);
            }

            if (!document.getElementById("sagedocs-marked-js") && typeof marked === "undefined") {
                var markedScript = document.createElement("script");
                markedScript.id = "sagedocs-marked-js";
                markedScript.src = "https://cdn.jsdelivr.net/npm/marked@15/marked.min.js";
                markedScript.onload = function () { self._rerenderAssistantMessages(); };
                document.head.appendChild(markedScript);
            }

            if (!document.getElementById("sagedocs-dompurify-js") && typeof DOMPurify === "undefined") {
                var purifyScript = document.createElement("script");
                purifyScript.id = "sagedocs-dompurify-js";
                purifyScript.src = "https://cdn.jsdelivr.net/npm/dompurify@3/dist/purify.min.js";
                purifyScript.onload = function () { self._rerenderAssistantMessages(); };
                document.head.appendChild(purifyScript);
            }
        },

        _render: function () {
            var self = this;
            var inline = !!this.config.inline;
            var posClass = inline
                ? "sagedocs-inline"
                : (this.config.position === "bottom-left" ? "sagedocs-left" : "sagedocs-right");

            // Container
            this.container = document.createElement("div");
            this.container.className = "sagedocs-container " + posClass;

            var panelStyle = inline ? "" : 'style="display:none;"';
            var resizeHandle = inline ? "" : '<div class="sagedocs-resize-handle" id="sagedocs-resize-handle"></div>';
            var closeButton = inline ? "" : '<button class="sagedocs-close" id="sagedocs-close">&times;</button>';
            var fabButton = inline ? "" :
                '<button class="sagedocs-fab" id="sagedocs-fab" title="Chat with SageDocs">' +
                    '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">' +
                        '<path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>' +
                    '</svg>' +
                '</button>';

            this.container.innerHTML =
                '<div class="sagedocs-chat-panel" id="sagedocs-panel" ' + panelStyle + '>' +
                    resizeHandle +
                    '<div class="sagedocs-header">' +
                        '<span class="sagedocs-title">SageDocs Assistant</span>' +
                        closeButton +
                    '</div>' +
                    '<div class="sagedocs-messages" id="sagedocs-messages"></div>' +
                    '<div class="sagedocs-input-area">' +
                        '<input type="text" id="sagedocs-input" placeholder="' + this.config.placeholder + '" />' +
                        '<button id="sagedocs-send">&#9654;</button>' +
                    '</div>' +
                '</div>' +
                fabButton;

            // Mount: inline -> into target; floating -> body
            var mountTarget = document.body;
            if (inline) {
                var t = this.config.target;
                if (typeof t === "string") t = document.querySelector(t);
                if (!t) {
                    console.warn("[SageDocs] inline mode requires a valid 'target' element");
                    return;
                }
                t.innerHTML = "";
                mountTarget = t;
                this.isOpen = true;
            }
            mountTarget.appendChild(this.container);

            // Add welcome message
            this._addMessage("assistant", this.config.welcomeMessage);

            // Add starter questions
            if (this.config.starterQuestions.length > 0) {
                this._addStarterQuestions();
            }

            // Event listeners (inline mode skips FAB/close/resize)
            if (!inline) {
                document.getElementById("sagedocs-fab").addEventListener("click", function () {
                    self.toggle();
                });
                document.getElementById("sagedocs-close").addEventListener("click", function () {
                    self.toggle();
                });

                var resizeEl = document.getElementById("sagedocs-resize-handle");
                var panel = document.getElementById("sagedocs-panel");
                var isResizing = false;
                var startX, startY, startW, startH;

                resizeEl.addEventListener("mousedown", function (e) {
                    isResizing = true;
                    startX = e.clientX;
                    startY = e.clientY;
                    startW = panel.offsetWidth;
                    startH = panel.offsetHeight;
                    e.preventDefault();
                });

                document.addEventListener("mousemove", function (e) {
                    if (!isResizing) return;
                    var isLeft = self.config.position === "bottom-left";
                    var dw = isLeft ? (e.clientX - startX) : (startX - e.clientX);
                    var dh = startY - e.clientY;
                    var newW = Math.max(320, Math.min(700, startW + dw));
                    var newH = Math.max(400, Math.min(800, startH + dh));
                    panel.style.width = newW + "px";
                    panel.style.height = newH + "px";
                });

                document.addEventListener("mouseup", function () {
                    isResizing = false;
                });
            }

            document.getElementById("sagedocs-send").addEventListener("click", function () {
                self._sendMessage();
            });
            document.getElementById("sagedocs-input").addEventListener("keydown", function (e) {
                if (e.key === "Enter") self._sendMessage();
            });
        },

        _updateWelcome: function () {
            var messagesEl = document.getElementById("sagedocs-messages");
            if (messagesEl && messagesEl.children.length > 0) {
                messagesEl.children[0].querySelector(".sagedocs-msg-text").textContent = this.config.welcomeMessage;
            }
        },

        _addStarterQuestions: function () {
            var self = this;
            var messagesEl = document.getElementById("sagedocs-messages");
            var starterDiv = document.createElement("div");
            starterDiv.className = "sagedocs-starters";

            this.config.starterQuestions.forEach(function (q) {
                var btn = document.createElement("button");
                btn.className = "sagedocs-starter-btn";
                btn.textContent = q;
                btn.addEventListener("click", function () {
                    document.getElementById("sagedocs-input").value = q;
                    self._sendMessage();
                    starterDiv.remove();
                });
                starterDiv.appendChild(btn);
            });

            messagesEl.appendChild(starterDiv);
        },

        toggle: function () {
            this.isOpen = !this.isOpen;
            var panel = document.getElementById("sagedocs-panel");
            var fab = document.getElementById("sagedocs-fab");
            panel.style.display = this.isOpen ? "flex" : "none";
            fab.style.display = this.isOpen ? "none" : "flex";

            if (this.isOpen) {
                document.getElementById("sagedocs-input").focus();
            }
        },

        _formatMarkdown: function (text) {
            if (typeof marked !== "undefined" && typeof DOMPurify !== "undefined") {
                var renderer = new marked.Renderer();
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

            return text
                .replace(/&/g, "&amp;")
                .replace(/</g, "&lt;")
                .replace(/>/g, "&gt;")
                .replace(/\n/g, "<br>");
        },

        _rerenderAssistantMessages: function () {
            if (typeof marked === "undefined" || typeof DOMPurify === "undefined") return;
            var nodes = document.querySelectorAll(".sagedocs-msg-assistant .sagedocs-msg-text[data-markdown]");
            for (var i = 0; i < nodes.length; i++) {
                nodes[i].innerHTML = this._formatMarkdown(nodes[i].getAttribute("data-markdown"));
            }
        },

        _addMessage: function (role, text, sources, images) {
            var self = this;
            var messagesEl = document.getElementById("sagedocs-messages");
            var msgDiv = document.createElement("div");
            msgDiv.className = "sagedocs-msg sagedocs-msg-" + role;

            var textDiv = document.createElement("div");
            textDiv.className = "sagedocs-msg-text";

            if (role === "assistant") {
                textDiv.setAttribute("data-markdown", text);
                textDiv.innerHTML = this._formatMarkdown(text);
            } else {
                textDiv.textContent = text;
            }

            msgDiv.appendChild(textDiv);

            // Render images if present
            if (images && images.length > 0) {
                var imagesDiv = document.createElement("div");
                imagesDiv.className = "sagedocs-msg-images";
                images.forEach(function (imgUrl) {
                    var img = document.createElement("img");
                    img.src = self.config.apiUrl + imgUrl;
                    img.className = "sagedocs-msg-img";
                    img.alt = "Screenshot from documentation";
                    img.addEventListener("click", function () {
                        self._showImageModal(img.src);
                    });
                    imagesDiv.appendChild(img);
                });
                msgDiv.appendChild(imagesDiv);
            }

            if (sources && sources.length > 0) {
                var srcDiv = document.createElement("div");
                srcDiv.className = "sagedocs-msg-sources";
                var details = document.createElement("details");
                var summary = document.createElement("summary");
                summary.innerHTML = '<span class="sagedocs-sources-icon">&#128196;</span> Sources (' + sources.length + ')';
                details.appendChild(summary);

                var srcList = document.createElement("div");
                srcList.className = "sagedocs-sources-list";
                sources.forEach(function (s) {
                    var pill = document.createElement("span");
                    pill.className = "sagedocs-source-pill";
                    pill.textContent = s.title;
                    srcList.appendChild(pill);
                });
                details.appendChild(srcList);
                srcDiv.appendChild(details);
                msgDiv.appendChild(srcDiv);
            }

            messagesEl.appendChild(msgDiv);
            messagesEl.scrollTop = messagesEl.scrollHeight;
        },

        _showImageModal: function (src) {
            var overlay = document.createElement("div");
            overlay.className = "sagedocs-img-overlay";
            overlay.innerHTML = '<img src="' + src + '" class="sagedocs-img-full" />';
            overlay.addEventListener("click", function () {
                overlay.remove();
            });
            document.body.appendChild(overlay);
        },

        _showTyping: function () {
            var messagesEl = document.getElementById("sagedocs-messages");
            var typingDiv = document.createElement("div");
            typingDiv.className = "sagedocs-msg sagedocs-msg-assistant sagedocs-typing";
            typingDiv.id = "sagedocs-typing";
            typingDiv.innerHTML = '<div class="sagedocs-msg-text"><span class="sagedocs-dot"></span><span class="sagedocs-dot"></span><span class="sagedocs-dot"></span></div>';
            messagesEl.appendChild(typingDiv);
            messagesEl.scrollTop = messagesEl.scrollHeight;
        },

        _hideTyping: function () {
            var el = document.getElementById("sagedocs-typing");
            if (el) el.remove();
        },

        _sendMessage: function () {
            var self = this;
            var input = document.getElementById("sagedocs-input");
            var message = input.value.trim();

            if (!message) return;

            this._addMessage("user", message);
            input.value = "";
            this._showTyping();

            var body = {
                tenant: this.config.tenant,
                message: message,
                session_id: this.sessionId
            };

            if (this.config.accountNumber) body.account_number = this.config.accountNumber;
            if (this.config.token) body.token = this.config.token;

            fetch(this.config.apiUrl + "/api/chat/", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(body)
            })
            .then(function (r) { return r.json(); })
            .then(function (data) {
                self._hideTyping();
                self.sessionId = data.session_id;
                self._addMessage("assistant", data.reply, data.sources, data.images);
            })
            .catch(function () {
                self._hideTyping();
                self._addMessage("assistant", "Sorry, something went wrong. Please try again.");
            });
        }
    };

    // Expose globally
    window.SageDocs = SageDocs;
})();

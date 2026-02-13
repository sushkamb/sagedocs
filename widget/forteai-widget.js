/**
 * ForteAI Chat Widget
 * Embeddable chat widget for any web application.
 *
 * Usage:
 *   <script src="https://forteai.yourdomain.com/widget/forteai-widget.js"></script>
 *   <script>
 *     ForteAI.init({
 *       tenant: 'chirocloud',
 *       accountNumber: '12345',   // optional, enables data mode
 *       token: 'jwt-token',       // optional, enables data mode
 *       theme: 'light',           // 'light' or 'dark'
 *       position: 'bottom-right', // 'bottom-right' or 'bottom-left'
 *       apiUrl: 'https://forteai.yourdomain.com'
 *     });
 *   </script>
 */
(function () {
    "use strict";

    var ForteAI = {
        config: null,
        container: null,
        isOpen: false,
        sessionId: null,
        messages: [],

        init: function (options) {
            this.config = Object.assign({
                tenant: "",
                accountNumber: "",
                token: "",
                theme: "light",
                position: "bottom-right",
                apiUrl: "",
                welcomeMessage: "Hi! How can I help you?",
                placeholder: "Ask me anything...",
                starterQuestions: []
            }, options);

            if (!this.config.apiUrl) {
                var scripts = document.getElementsByTagName("script");
                for (var i = 0; i < scripts.length; i++) {
                    if (scripts[i].src && scripts[i].src.indexOf("forteai-widget.js") > -1) {
                        this.config.apiUrl = scripts[i].src.replace("/widget/forteai-widget.js", "");
                        break;
                    }
                }
            }

            this._loadStyles();
            this._fetchTenantConfig();
            this._render();
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
            var link = document.createElement("link");
            link.rel = "stylesheet";
            link.href = this.config.apiUrl + "/widget/forteai-widget.css";
            document.head.appendChild(link);

            var markedScript = document.createElement("script");
            markedScript.src = "https://cdn.jsdelivr.net/npm/marked@15/marked.min.js";
            document.head.appendChild(markedScript);

            var purifyScript = document.createElement("script");
            purifyScript.src = "https://cdn.jsdelivr.net/npm/dompurify@3/dist/purify.min.js";
            document.head.appendChild(purifyScript);
        },

        _render: function () {
            var self = this;
            var posClass = this.config.position === "bottom-left" ? "forteai-left" : "forteai-right";

            // Container
            this.container = document.createElement("div");
            this.container.className = "forteai-container " + posClass;
            this.container.innerHTML =
                '<div class="forteai-chat-panel" id="forteai-panel" style="display:none;">' +
                    '<div class="forteai-resize-handle" id="forteai-resize-handle"></div>' +
                    '<div class="forteai-header">' +
                        '<span class="forteai-title">ForteAI Assistant</span>' +
                        '<button class="forteai-close" id="forteai-close">&times;</button>' +
                    '</div>' +
                    '<div class="forteai-messages" id="forteai-messages"></div>' +
                    '<div class="forteai-input-area">' +
                        '<input type="text" id="forteai-input" placeholder="' + this.config.placeholder + '" />' +
                        '<button id="forteai-send">&#9654;</button>' +
                    '</div>' +
                '</div>' +
                '<button class="forteai-fab" id="forteai-fab" title="Chat with ForteAI">' +
                    '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">' +
                        '<path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>' +
                    '</svg>' +
                '</button>';

            document.body.appendChild(this.container);

            // Add welcome message
            this._addMessage("assistant", this.config.welcomeMessage);

            // Add starter questions
            if (this.config.starterQuestions.length > 0) {
                this._addStarterQuestions();
            }

            // Event listeners
            document.getElementById("forteai-fab").addEventListener("click", function () {
                self.toggle();
            });
            document.getElementById("forteai-close").addEventListener("click", function () {
                self.toggle();
            });
            document.getElementById("forteai-send").addEventListener("click", function () {
                self._sendMessage();
            });
            document.getElementById("forteai-input").addEventListener("keydown", function (e) {
                if (e.key === "Enter") self._sendMessage();
            });

            // Resize drag logic
            var resizeHandle = document.getElementById("forteai-resize-handle");
            var panel = document.getElementById("forteai-panel");
            var isResizing = false;
            var startX, startY, startW, startH;

            resizeHandle.addEventListener("mousedown", function (e) {
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
        },

        _updateWelcome: function () {
            var messagesEl = document.getElementById("forteai-messages");
            if (messagesEl && messagesEl.children.length > 0) {
                messagesEl.children[0].querySelector(".forteai-msg-text").textContent = this.config.welcomeMessage;
            }
        },

        _addStarterQuestions: function () {
            var self = this;
            var messagesEl = document.getElementById("forteai-messages");
            var starterDiv = document.createElement("div");
            starterDiv.className = "forteai-starters";

            this.config.starterQuestions.forEach(function (q) {
                var btn = document.createElement("button");
                btn.className = "forteai-starter-btn";
                btn.textContent = q;
                btn.addEventListener("click", function () {
                    document.getElementById("forteai-input").value = q;
                    self._sendMessage();
                    starterDiv.remove();
                });
                starterDiv.appendChild(btn);
            });

            messagesEl.appendChild(starterDiv);
        },

        toggle: function () {
            this.isOpen = !this.isOpen;
            var panel = document.getElementById("forteai-panel");
            var fab = document.getElementById("forteai-fab");
            panel.style.display = this.isOpen ? "flex" : "none";
            fab.style.display = this.isOpen ? "none" : "flex";

            if (this.isOpen) {
                document.getElementById("forteai-input").focus();
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

        _addMessage: function (role, text, sources, images) {
            var self = this;
            var messagesEl = document.getElementById("forteai-messages");
            var msgDiv = document.createElement("div");
            msgDiv.className = "forteai-msg forteai-msg-" + role;

            var textDiv = document.createElement("div");
            textDiv.className = "forteai-msg-text";

            if (role === "assistant") {
                textDiv.innerHTML = this._formatMarkdown(text);
            } else {
                textDiv.textContent = text;
            }

            msgDiv.appendChild(textDiv);

            // Render images if present
            if (images && images.length > 0) {
                var imagesDiv = document.createElement("div");
                imagesDiv.className = "forteai-msg-images";
                images.forEach(function (imgUrl) {
                    var img = document.createElement("img");
                    img.src = self.config.apiUrl + imgUrl;
                    img.className = "forteai-msg-img";
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
                srcDiv.className = "forteai-msg-sources";
                srcDiv.textContent = "Sources: " + sources.map(function (s) { return s.title; }).join(", ");
                msgDiv.appendChild(srcDiv);
            }

            messagesEl.appendChild(msgDiv);
            messagesEl.scrollTop = messagesEl.scrollHeight;
        },

        _showImageModal: function (src) {
            var overlay = document.createElement("div");
            overlay.className = "forteai-img-overlay";
            overlay.innerHTML = '<img src="' + src + '" class="forteai-img-full" />';
            overlay.addEventListener("click", function () {
                overlay.remove();
            });
            document.body.appendChild(overlay);
        },

        _showTyping: function () {
            var messagesEl = document.getElementById("forteai-messages");
            var typingDiv = document.createElement("div");
            typingDiv.className = "forteai-msg forteai-msg-assistant forteai-typing";
            typingDiv.id = "forteai-typing";
            typingDiv.innerHTML = '<div class="forteai-msg-text"><span class="forteai-dot"></span><span class="forteai-dot"></span><span class="forteai-dot"></span></div>';
            messagesEl.appendChild(typingDiv);
            messagesEl.scrollTop = messagesEl.scrollHeight;
        },

        _hideTyping: function () {
            var el = document.getElementById("forteai-typing");
            if (el) el.remove();
        },

        _sendMessage: function () {
            var self = this;
            var input = document.getElementById("forteai-input");
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
    window.ForteAI = ForteAI;
})();

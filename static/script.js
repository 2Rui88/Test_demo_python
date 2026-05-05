// 前端只负责通信与 DOM 渲染，所有业务逻辑（会话管理、AI 对话、校验）由后端实现

var API_BASE = "/api";

// ========== DOM 元素 ==========
var sessionListEl    = document.getElementById("sessionList");
var newSessionBtn    = document.getElementById("newSessionBtn");
var chatPlaceholder  = document.getElementById("chatPlaceholder");
var chatActive       = document.getElementById("chatActive");
var chatSessionName  = document.getElementById("chatSessionName");
var deleteSessionBtn = document.getElementById("deleteSessionBtn");
var messageListEl    = document.getElementById("messageList");
var messageInput     = document.getElementById("messageInput");
var sendBtn          = document.getElementById("sendBtn");

var currentSessionId = null;   // 当前选中会话 ID（仅 UI 用途）
var sessionsCache    = [];      // 会话列表缓存（仅 UI 用途）

// ========== 纯展示工具 ==========

function escapeHtml(str) {
    if (!str) return "";
    return str.replace(/[&<>]/g, function(m) {
        if (m === "&") return "&amp;";
        if (m === "<") return "&lt;";
        if (m === ">") return "&gt;";
        return m;
    });
}

// ========== 侧边栏渲染 ==========

function renderSessionList(sessions) {
    sessionsCache = sessions || [];
    if (!sessionsCache.length) {
        sessionListEl.innerHTML = '<div class="empty-sessions">暂无会话，点击上方按钮创建</div>';
        return;
    }
    var html = "";
    sessionsCache.forEach(function(s) {
        var activeClass = (s.id === currentSessionId) ? " active" : "";
        html +=
            '<div class="session-item' + activeClass + '" data-id="' + escapeHtml(s.id) + '">' +
                '<span class="session-item-name">' + escapeHtml(s.name) + '</span>' +
                '<span class="session-item-time">' + formatTime(s.createdAt) + '</span>' +
                '<button class="session-item-del" data-action="delete" data-id="' + escapeHtml(s.id) + '" title="删除">×</button>' +
            '</div>';
    });
    sessionListEl.innerHTML = html;
}

function formatTime(isoStr) {
    if (!isoStr) return "";
    try {
        var d = new Date(isoStr);
        var now = new Date();
        if (d.toDateString() === now.toDateString()) {
            return d.toLocaleTimeString([], {hour:"2-digit", minute:"2-digit"});
        }
        return (d.getMonth() + 1) + "/" + d.getDate();
    } catch(e) {
        return "";
    }
}

// ========== 消息渲染 ==========

function renderMessages(messages) {
    if (!messages || !messages.length) {
        messageListEl.innerHTML = '<div style="text-align:center;color:#b0b8c0;padding:40px;">开始和 AI 对话吧～</div>';
        return;
    }
    var html = "";
    messages.forEach(function(m) {
        var roleClass = (m.role === "user") ? "user" : "assistant";
        var avatar = (m.role === "user") ? "🙂" : "🤖";
        html +=
            '<div class="message-row ' + roleClass + '">' +
                '<div class="message-avatar">' + avatar + '</div>' +
                '<div>' +
                    '<div class="message-bubble">' + escapeHtml(m.content) + '</div>' +
                    '<div class="message-time">' + formatTime(m.timestamp) + '</div>' +
                '</div>' +
            '</div>';
    });
    messageListEl.innerHTML = html;
    messageListEl.scrollTop = messageListEl.scrollHeight;
}

// ========== 视图切换 ==========

function showPlaceholder() {
    chatPlaceholder.style.display = "";
    chatActive.style.display = "none";
    currentSessionId = null;
    renderSessionList(sessionsCache);
}

function showChat(sessionId, sessionName) {
    chatPlaceholder.style.display = "none";
    chatActive.style.display = "";
    chatSessionName.textContent = sessionName;
    currentSessionId = sessionId;
    renderSessionList(sessionsCache);
    messageInput.focus();
}

// ========== API 调用（仅发送请求、渲染响应） ==========

async function loadSessionList() {
    try {
        var res = await fetch(API_BASE + "/sessions");
        if (!res.ok) throw new Error("获取会话列表失败");
        var data = await res.json();
        renderSessionList(data.sessions);
    } catch (err) {
        console.error(err);
        sessionListEl.innerHTML = '<div class="empty-sessions">⚠️ 加载失败</div>';
    }
}

async function createSession() {
    try {
        var res = await fetch(API_BASE + "/sessions", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ name: "新会话" })
        });
        if (!res.ok) throw new Error("创建失败");
        var session = await res.json();
        await loadSessionList();
        await loadSession(session.id);
    } catch (err) {
        console.error(err);
    }
}

async function loadSession(sessionId) {
    try {
        var res = await fetch(API_BASE + "/sessions/" + encodeURIComponent(sessionId));
        if (!res.ok) throw new Error("加载会话失败");
        var session = await res.json();
        showChat(session.id, session.name);
        renderMessages(session.messages);
    } catch (err) {
        console.error(err);
    }
}

async function deleteSession(sessionId) {
    if (!confirm("确定删除此会话吗？")) return;
    try {
        var res = await fetch(API_BASE + "/sessions/" + encodeURIComponent(sessionId), {
            method: "DELETE"
        });
        if (!res.ok) throw new Error("删除失败");
        if (currentSessionId === sessionId) {
            showPlaceholder();
        }
        await loadSessionList();
    } catch (err) {
        console.error(err);
    }
}

async function sendMessage() {
    var content = messageInput.value.trim();
    if (!currentSessionId) return;

    sendBtn.disabled = true;
    messageInput.disabled = true;
    sendBtn.textContent = "发送中...";

    try {
        var res = await fetch(API_BASE + "/sessions/" + encodeURIComponent(currentSessionId) + "/messages", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ content: content })
        });
        if (!res.ok) throw new Error("发送失败");
        var data = await res.json();
        // 后端返回 { messages: [...] } 或 { feedback, messages }
        renderMessages(data.messages);
        messageInput.value = "";
    } catch (err) {
        console.error(err);
        messageListEl.insertAdjacentHTML("beforeend",
            '<div style="color:#d9534f;text-align:center;padding:8px;">⚠️ 发送失败，请重试</div>');
    } finally {
        sendBtn.disabled = false;
        messageInput.disabled = false;
        sendBtn.textContent = "发送";
        messageInput.focus();
    }
}

// ========== 事件绑定（纯 UI 连线） ==========

function bindEvents() {
    newSessionBtn.addEventListener("click", createSession);

    deleteSessionBtn.addEventListener("click", function() {
        if (currentSessionId) deleteSession(currentSessionId);
    });

    sendBtn.addEventListener("click", sendMessage);

    messageInput.addEventListener("keypress", function(e) {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    sessionListEl.addEventListener("click", function(e) {
        var item = e.target.closest(".session-item");
        if (!item) return;

        // 点击删除按钮
        if (e.target.getAttribute("data-action") === "delete") {
            e.stopPropagation();
            deleteSession(e.target.getAttribute("data-id"));
            return;
        }

        // 点击会话项 → 加载
        var id = item.getAttribute("data-id");
        if (id && id !== currentSessionId) {
            loadSession(id);
        }
    });
}

// ========== 初始化 ==========

function init() {
    bindEvents();
    loadSessionList();
}

init();

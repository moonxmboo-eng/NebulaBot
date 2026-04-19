const state = {
    sessionId: null,
    sessions: [],
};

const chatBox = document.getElementById("chat-box");
const chatForm = document.getElementById("chat-form");
const input = document.getElementById("message-input");
const sessionList = document.getElementById("session-list");
const sessionCount = document.getElementById("session-count");
const chatTitle = document.getElementById("chat-title");
const providerPill = document.getElementById("provider-pill");
const healthPill = document.getElementById("health-pill");
const messageTemplate = document.getElementById("message-template");
const newSessionButton = document.getElementById("new-session");

function escapeHtml(text) {
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
}

function renderMessage(role, content) {
    const node = messageTemplate.content.firstElementChild.cloneNode(true);
    node.classList.add(role === "user" ? "user" : "assistant");
    node.querySelector(".bubble-role").textContent = role;
    node.querySelector(".bubble-content").innerHTML = escapeHtml(content).replace(/\n/g, "<br>");
    chatBox.appendChild(node);
    chatBox.scrollTop = chatBox.scrollHeight;
}

function clearMessages() {
    chatBox.innerHTML = "";
}

async function fetchJson(url, options) {
    const response = await fetch(url, options);
    if (!response.ok) {
        throw new Error(`Request failed: ${response.status}`);
    }
    return response.json();
}

async function createSession() {
    const data = await fetchJson("/api/sessions", { method: "POST" });
    state.sessionId = data.session_id;
    chatTitle.textContent = "New Session";
    clearMessages();
    renderMessage(
        "assistant",
        "NebulaBot is ready. Try /help to inspect the built-in commands."
    );
    await refreshSessions();
}

async function refreshHealth() {
    const health = await fetchJson("/api/health");
    const providers = await fetchJson("/api/providers");
    providerPill.textContent = providers.default;
    healthPill.textContent = health.status;
}

function renderSessions() {
    sessionList.innerHTML = "";
    sessionCount.textContent = String(state.sessions.length);

    for (const session of state.sessions) {
        const button = document.createElement("button");
        button.type = "button";
        button.className = "session-item";
        if (session.session_id === state.sessionId) {
            button.classList.add("active");
        }
        button.innerHTML = `
            <span class="session-title">${escapeHtml(session.title)}</span>
            <span class="session-meta mono">${session.message_count} msgs</span>
        `;
        button.addEventListener("click", async () => {
            state.sessionId = session.session_id;
            chatTitle.textContent = session.title;
            await loadMessages(session.session_id);
            renderSessions();
        });
        sessionList.appendChild(button);
    }
}

async function refreshSessions() {
    state.sessions = await fetchJson("/api/sessions");
    if (!state.sessionId && state.sessions.length) {
        state.sessionId = state.sessions[0].session_id;
    }
    renderSessions();
}

async function loadMessages(sessionId) {
    clearMessages();
    const messages = await fetchJson(`/api/sessions/${sessionId}/messages`);
    if (!messages.length) {
        renderMessage(
            "assistant",
            "Empty session. Ask something or use a plugin command."
        );
        return;
    }
    for (const message of messages) {
        renderMessage(message.role, message.content);
    }
}

chatForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    const content = input.value.trim();
    if (!content || !state.sessionId) {
        return;
    }

    renderMessage("user", content);
    input.value = "";

    const reply = await fetchJson("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ session_id: state.sessionId, content }),
    });

    renderMessage("assistant", reply.reply);
    await refreshSessions();
});

newSessionButton.addEventListener("click", createSession);

input.addEventListener("input", () => {
    input.style.height = "auto";
    input.style.height = `${Math.min(input.scrollHeight, 180)}px`;
});

async function bootstrap() {
    await refreshHealth();
    await refreshSessions();
    if (!state.sessionId) {
        await createSession();
    } else {
        const current = state.sessions.find((item) => item.session_id === state.sessionId);
        chatTitle.textContent = current ? current.title : "Session";
        await loadMessages(state.sessionId);
    }
}

bootstrap().catch((error) => {
    clearMessages();
    renderMessage("assistant", `Failed to load NebulaBot UI: ${error.message}`);
});

document.addEventListener('DOMContentLoaded', () => {
    const chatBox = document.getElementById('chat-box');
    const chatForm = document.getElementById('chat-form');
    const messageInput = document.getElementById('message-input');
    const themeToggle = document.getElementById('theme-toggle');

    // Theme toggling
    themeToggle.addEventListener('click', () => {
        const currentTheme = document.body.getAttribute('data-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        document.body.setAttribute('data-theme', newTheme);
        themeToggle.textContent = newTheme === 'dark' ? '☀️' : '🌙';
    });

    // WebSocket Setup
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws`;
    
    let ws;
    let reconnectAttempts = 0;

    function connect() {
        ws = new WebSocket(wsUrl);

        ws.onopen = () => {
            console.log("Connected to NebulaBot");
            reconnectAttempts = 0;
            document.querySelector('.status').innerHTML = "Online";
            document.querySelector('.status').style.color = "var(--primary)";
        };

        ws.onmessage = (event) => {
            appendMessage(event.data, 'bot');
        };

        ws.onclose = () => {
            console.log("Disconnected. Reconnecting...");
            document.querySelector('.status').innerHTML = "Reconnecting...";
            document.querySelector('.status').style.color = "#ef4444";
            
            // Reconnect backoff
            const delay = Math.min(1000 * Math.pow(2, reconnectAttempts), 10000);
            reconnectAttempts++;
            setTimeout(connect, delay);
        };
        
        ws.onerror = (err) => {
            console.error("WebSocket Error:", err);
            ws.close();
        };
    }

    connect();

    function appendMessage(text, sender) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message', `${sender}-message`);
        
        const contentDiv = document.createElement('div');
        contentDiv.classList.add('message-content');
        contentDiv.textContent = text;
        
        messageDiv.appendChild(contentDiv);
        chatBox.appendChild(messageDiv);
        
        // Scroll to bottom
        chatBox.scrollTop = chatBox.scrollHeight;
    }

    chatForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const text = messageInput.value.trim();
        if (!text) return;

        // Display user message
        appendMessage(text, 'user');
        
        // Send to server
        if (ws && ws.readyState === WebSocket.OPEN) {
            ws.send(text);
        } else {
            appendMessage("Error: Connection lost.", 'bot');
        }

        // Clear input
        messageInput.value = '';
        messageInput.focus();
    });
});

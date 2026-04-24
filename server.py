import os
import socket
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from agent_core import run_agent, SYSTEM_MESSAGE
import uvicorn

app = FastAPI(title="JARVIS Mobile Interface")

# Simple memory storage for demo (replaces file-based history for now)
sessions = {}

class Query(BaseModel):
    text: str
    session_id: str = "default"

@app.get("/", response_class=HTMLResponse)
async def get_index():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>JARVIS Mobile</title>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600&family=JetBrains+Mono&display=swap" rel="stylesheet">
        <style>
            :root {
                --bg: #0b0e14;
                --card: #1a1d23;
                --text: #e1e1e1;
                --dim: #888;
                --accent: #3b82f6;
            }
            body {
                margin: 0;
                font-family: 'Inter', sans-serif;
                background: var(--bg);
                color: var(--text);
                display: flex;
                flex-direction: column;
                height: 100vh;
            }
            header {
                padding: 20px;
                text-align: center;
                border-bottom: 1px solid #333;
                background: var(--card);
            }
            header h1 {
                margin: 0;
                font-size: 1.5rem;
                letter-spacing: 2px;
                color: var(--accent);
            }
            #chat-container {
                flex: 1;
                overflow-y: auto;
                padding: 20px;
                display: flex;
                flex-direction: column;
                gap: 15px;
            }
            .message {
                max-width: 85%;
                padding: 12px 16px;
                border-radius: 15px;
                line-height: 1.5;
                font-size: 0.95rem;
            }
            .user {
                align-self: flex-end;
                background: var(--accent);
                color: white;
            }
            .jarvis {
                align-self: flex-start;
                background: var(--card);
                border: 1px solid #333;
            }
            .thinking {
                font-family: 'JetBrains Mono', monospace;
                color: var(--dim);
                font-size: 0.8rem;
                border-left: 2px solid var(--dim);
                padding-left: 10px;
                margin-bottom: 10px;
                display: block;
                white-space: pre-wrap;
            }
            footer {
                padding: 15px;
                background: var(--card);
                display: flex;
                gap: 10px;
            }
            input {
                flex: 1;
                background: #000;
                border: 1px solid #444;
                color: white;
                padding: 12px;
                border-radius: 8px;
                outline: none;
            }
            button {
                background: var(--accent);
                border: none;
                color: white;
                padding: 0 20px;
                border-radius: 8px;
                font-weight: 600;
            }
            /* Markdown-ish formatting */
            pre { background: #000; padding: 10px; border-radius: 5px; overflow-x: auto; }
        </style>
    </head>
    <body>
        <header><h1>JARVIS</h1></header>
        <div id="chat-container">
            <div class="message jarvis">Hello! How can I help you today?</div>
        </div>
        <footer>
            <input type="text" id="userInput" placeholder="Ask Jarvis..." onkeypress="if(event.key==='Enter') sendMessage()">
            <button onclick="sendMessage()">Send</button>
        </footer>

        <script>
            async function sendMessage() {
                const input = document.getElementById('userInput');
                const chat = document.getElementById('chat-container');
                const text = input.value.trim();
                if (!text) return;

                // Add User Message
                const userDiv = document.createElement('div');
                userDiv.className = 'message user';
                userDiv.innerText = text;
                chat.appendChild(userDiv);
                input.value = '';
                chat.scrollTop = chat.scrollHeight;

                // Add Jarvis Placeholder
                const jarvisDiv = document.createElement('div');
                jarvisDiv.className = 'message jarvis';
                jarvisDiv.innerHTML = '<i>Thinking...</i>';
                chat.appendChild(jarvisDiv);

                try {
                    const response = await fetch('/chat', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ text: text })
                    });
                    const data = await response.json();
                    
                    let content = data.response;
                    // Format thinking tags
                    content = content.replace(/<think>([\\s\\S]*?)<\\/think>/g, '<span class="thinking">$1</span>');
                    
                    jarvisDiv.innerHTML = content;
                } catch (e) {
                    jarvisDiv.innerText = "Error connecting to Jarvis.";
                }
                chat.scrollTop = chat.scrollHeight;
            }
        </script>
    </body>
    </html>
    """

@app.post("/chat")
async def chat(q: Query):
    # Retrieve or initialize session history
    if q.session_id not in sessions:
        sessions[q.session_id] = [SYSTEM_MESSAGE]
    
    response_text, updated_history = run_agent(q.text, sessions[q.session_id])
    sessions[q.session_id] = updated_history
    
    return {"response": response_text}

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

if __name__ == "__main__":
    local_ip = get_local_ip()
    print(f"\\n🚀 SERVER STARTING!")
    print(f"🔗 Access Jarvis on your phone at: http://{local_ip}:8000\\n")
    uvicorn.run(app, host="0.0.0.0", port=8000)

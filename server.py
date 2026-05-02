import os
import socket
import asyncio
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, StreamingResponse
from pydantic import BaseModel
from agent_core import run_agent, run_agent_stream, SYSTEM_MESSAGE
import uvicorn

app = FastAPI(title="JARVIS Mobile Interface")

sessions: dict = {}

class Query(BaseModel):
    text: str
    session_id: str = "default"

# ── Non-streaming fallback ─────────────────────────────────────────
@app.post("/chat")
async def chat(q: Query):
    if q.session_id not in sessions:
        sessions[q.session_id] = [SYSTEM_MESSAGE]
    response_text, updated_history = run_agent(q.text, sessions[q.session_id])
    sessions[q.session_id] = updated_history
    return {"response": response_text}

# ── Streaming endpoint (SSE) ───────────────────────────────────────
@app.post("/chat/stream")
async def chat_stream(q: Query):
    if q.session_id not in sessions:
        sessions[q.session_id] = [SYSTEM_MESSAGE]

    history = sessions[q.session_id]

    # run_agent_stream uses blocking urllib calls, so we push it into
    # a background thread and forward events via an asyncio.Queue.
    queue: asyncio.Queue = asyncio.Queue()
    loop = asyncio.get_event_loop()

    def _produce():
        """Runs in threadpool; pushes SSE strings into the queue."""
        try:
            for event in run_agent_stream(q.text, history):
                loop.call_soon_threadsafe(queue.put_nowait, event)
        finally:
            loop.call_soon_threadsafe(queue.put_nowait, None)  # sentinel

    async def _stream():
        loop.run_in_executor(None, _produce)
        while True:
            chunk = await queue.get()
            if chunk is None:
                break
            yield chunk
        sessions[q.session_id] = history  # updated in-place

    return StreamingResponse(
        _stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


# ── Web UI ─────────────────────────────────────────────────────────
@app.get("/", response_class=HTMLResponse)
async def get_index():
    return r"""
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>JARVIS</title>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600&family=JetBrains+Mono&display=swap" rel="stylesheet">
  <style>
    :root {
      --bg: #0b0e14;
      --card: #1a1d23;
      --text: #e1e1e1;
      --dim: #888;
      --accent: #3b82f6;
      --think-bg: #0f172a;
      --think-border: #1e3a5f;
      --think-text: #7dd3fc;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: 'Inter', sans-serif;
      background: var(--bg);
      color: var(--text);
      display: flex;
      flex-direction: column;
      height: 100vh;
    }
    header {
      padding: 16px 20px;
      text-align: center;
      border-bottom: 1px solid #2a2d33;
      background: var(--card);
    }
    header h1 { font-size: 1.4rem; letter-spacing: 3px; color: var(--accent); }

    #chat-container {
      flex: 1;
      overflow-y: auto;
      padding: 20px;
      display: flex;
      flex-direction: column;
      gap: 14px;
    }

    .bubble {
      max-width: 88%;
      padding: 12px 16px;
      border-radius: 14px;
      line-height: 1.6;
      font-size: 0.93rem;
    }
    .user {
      align-self: flex-end;
      background: var(--accent);
      color: #fff;
      border-bottom-right-radius: 4px;
    }
    .jarvis {
      align-self: flex-start;
      background: var(--card);
      border: 1px solid #2a2d33;
      border-bottom-left-radius: 4px;
    }

    /* ── Thinking block ─────────────────────────────── */
    .think-block {
      margin-bottom: 8px;
      border: 1px solid var(--think-border);
      border-radius: 8px;
      overflow: hidden;
    }
    .think-toggle {
      display: flex;
      align-items: center;
      gap: 8px;
      padding: 7px 12px;
      background: var(--think-bg);
      cursor: pointer;
      border: none;
      width: 100%;
      text-align: left;
      font-size: 0.75rem;
      color: var(--think-text);
      font-family: inherit;
    }
    .think-toggle:hover { filter: brightness(1.15); }
    .think-arrow {
      transition: transform 0.2s;
      font-size: 0.65rem;
    }
    .think-toggle.open .think-arrow { transform: rotate(90deg); }
    .think-body {
      display: none;
      padding: 10px 14px;
      background: var(--think-bg);
      font-family: 'JetBrains Mono', monospace;
      font-size: 0.75rem;
      color: var(--think-text);
      white-space: pre-wrap;
      border-top: 1px solid var(--think-border);
      max-height: 280px;
      overflow-y: auto;
    }
    .think-body.open { display: block; }

    /* ── Answer text ────────────────────────────────── */
    .answer-text { white-space: pre-wrap; }

    /* ── Tool pill ──────────────────────────────────── */
    .tool-pill {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      font-size: 0.72rem;
      color: #94a3b8;
      background: #1e293b;
      border: 1px solid #334155;
      border-radius: 999px;
      padding: 3px 10px;
      margin-bottom: 8px;
    }

    /* ── Cursor blink ───────────────────────────────── */
    .cursor {
      display: inline-block;
      width: 2px;
      height: 1em;
      background: var(--accent);
      margin-left: 2px;
      vertical-align: text-bottom;
      animation: blink 0.8s step-end infinite;
    }
    @keyframes blink { 50% { opacity: 0; } }

    footer {
      padding: 14px 16px;
      background: var(--card);
      display: flex;
      gap: 10px;
      border-top: 1px solid #2a2d33;
    }
    #userInput {
      flex: 1;
      background: #0b0e14;
      border: 1px solid #3a3d43;
      color: white;
      padding: 11px 14px;
      border-radius: 8px;
      outline: none;
      font-family: inherit;
      font-size: 0.93rem;
    }
    #userInput:focus { border-color: var(--accent); }
    #sendBtn {
      background: var(--accent);
      border: none;
      color: white;
      padding: 0 22px;
      border-radius: 8px;
      font-weight: 600;
      cursor: pointer;
      font-size: 0.93rem;
    }
    #sendBtn:disabled { opacity: 0.5; cursor: not-allowed; }
  </style>
</head>
<body>
  <header><h1>JARVIS</h1></header>
  <div id="chat-container">
    <div class="bubble jarvis">Hello! How can I help you today?</div>
  </div>
  <footer>
    <input type="text" id="userInput" placeholder="Ask Jarvis..."
           onkeypress="if(event.key==='Enter') sendMessage()">
    <button id="sendBtn" onclick="sendMessage()">Send</button>
  </footer>

  <script>
    let thinkId = 0;

    function escHtml(s) {
      return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
    }

    function toggleThink(id) {
      const body = document.getElementById('tb-' + id);
      const btn  = document.getElementById('tt-' + id);
      const open = body.classList.toggle('open');
      btn.classList.toggle('open', open);
    }

    async function sendMessage() {
      const input  = document.getElementById('userInput');
      const chat   = document.getElementById('chat-container');
      const btn    = document.getElementById('sendBtn');
      const text   = input.value.trim();
      if (!text) return;

      // User bubble
      const userDiv = document.createElement('div');
      userDiv.className = 'bubble user';
      userDiv.textContent = text;
      chat.appendChild(userDiv);
      input.value = '';
      btn.disabled = true;
      chat.scrollTop = chat.scrollHeight;

      // Jarvis bubble (will be filled by stream)
      const jarvisDiv = document.createElement('div');
      jarvisDiv.className = 'bubble jarvis';
      chat.appendChild(jarvisDiv);

      // ── State machine for streaming ─────────────────
      let inThink   = false;  // currently inside <think>
      let thinkBuf  = '';     // accumulated thinking text
      let answerBuf = '';     // accumulated answer text
      let thinkBlock = null;  // current .think-block DOM node
      let thinkBodyEl = null; // .think-body inside it
      let answerEl   = null;  // .answer-text DOM node
      let cursorEl   = null;  // blinking cursor

      function getOrCreateAnswer() {
        if (!answerEl) {
          answerEl = document.createElement('div');
          answerEl.className = 'answer-text';
          jarvisDiv.appendChild(answerEl);
        }
        return answerEl;
      }

      function setCursor(el) {
        if (cursorEl && cursorEl.parentNode) cursorEl.parentNode.removeChild(cursorEl);
        cursorEl = document.createElement('span');
        cursorEl.className = 'cursor';
        el.appendChild(cursorEl);
      }

      function removeCursor() {
        if (cursorEl && cursorEl.parentNode) cursorEl.parentNode.removeChild(cursorEl);
        cursorEl = null;
      }

      function flushThink() {
        if (!thinkBlock) return;
        thinkBodyEl.textContent = thinkBuf.trim();
        thinkBuf = '';
      }

      function handleToken(text) {
        // Accumulate and parse <think>...</think> in the stream
        answerBuf += text;

        let buf = answerBuf;
        answerBuf = '';

        while (buf.length > 0) {
          if (!inThink) {
            const tStart = buf.indexOf('<think>');
            if (tStart === -1) {
              // Plain answer text
              const el = getOrCreateAnswer();
              el.textContent = (el.textContent || '') + buf;
              setCursor(el);
              buf = '';
            } else {
              // Text before <think>
              if (tStart > 0) {
                const before = buf.slice(0, tStart);
                const el = getOrCreateAnswer();
                el.textContent = (el.textContent || '') + before;
              }
              // Start a think block
              inThink = true;
              thinkBuf = '';
              const id = thinkId++;
              thinkBlock = document.createElement('div');
              thinkBlock.className = 'think-block';
              const toggleBtn = document.createElement('button');
              toggleBtn.className = 'think-toggle open';
              toggleBtn.id = 'tt-' + id;
              toggleBtn.innerHTML = '<span class="think-arrow">&#9654;</span><span>Thinking...</span>';
              toggleBtn.onclick = () => toggleThink(id);
              thinkBodyEl = document.createElement('div');
              thinkBodyEl.className = 'think-body open';
              thinkBodyEl.id = 'tb-' + id;
              thinkBlock.appendChild(toggleBtn);
              thinkBlock.appendChild(thinkBodyEl);
              jarvisDiv.insertBefore(thinkBlock, answerEl);
              // Reset answerEl so next text goes below think block
              answerEl = null;
              setCursor(thinkBodyEl);
              buf = buf.slice(tStart + 7);
            }
          } else {
            const tEnd = buf.indexOf('</think>');
            if (tEnd === -1) {
              // Still inside think
              thinkBuf += buf;
              thinkBodyEl.textContent = thinkBuf;
              setCursor(thinkBodyEl);
              buf = '';
            } else {
              thinkBuf += buf.slice(0, tEnd);
              thinkBodyEl.textContent = thinkBuf.trim();
              // Close thinking block — collapse it
              const btn = thinkBodyEl.previousElementSibling;
              if (btn) {
                btn.classList.remove('open');
                btn.querySelector('span:last-child').textContent = 'Thought for a moment';
              }
              thinkBodyEl.classList.remove('open');
              inThink = false;
              thinkBlock = null;
              thinkBodyEl = null;
              removeCursor();
              buf = buf.slice(tEnd + 8);
            }
          }
        }
        chat.scrollTop = chat.scrollHeight;
      }

      // ── Connect SSE ────────────────────────────────
      try {
        const resp = await fetch('/chat/stream', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ text })
        });

        const reader = resp.body.getReader();
        const decoder = new TextDecoder();
        let leftover = '';

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;
          leftover += decoder.decode(value, { stream: true });

          const lines = leftover.split('\n\n');
          leftover = lines.pop(); // keep incomplete chunk

          for (const line of lines) {
            if (!line.startsWith('data: ')) continue;
            let evt;
            try { evt = JSON.parse(line.slice(6)); } catch { continue; }

            if (evt.type === 'tool') {
              // Show tool pill above answer
              const pill = document.createElement('div');
              pill.className = 'tool-pill';
              pill.innerHTML = '&#9881; ' + escHtml(evt.name);
              jarvisDiv.appendChild(pill);
              answerEl = null; // next text goes after pill
              chat.scrollTop = chat.scrollHeight;

            } else if (evt.type === 'token') {
              handleToken(evt.text);

            } else if (evt.type === 'done') {
              removeCursor();
            }
          }
        }
      } catch (e) {
        jarvisDiv.textContent = 'Error connecting to Jarvis.';
      }

      removeCursor();
      btn.disabled = false;
      input.focus();
      chat.scrollTop = chat.scrollHeight;
    }
  </script>
</body>
</html>
"""

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
    print(f"\n🚀 SERVER STARTING!")
    print(f"🔗 Access Jarvis on your phone at: http://{local_ip}:8000\n")
    uvicorn.run(app, host="0.0.0.0", port=8000)

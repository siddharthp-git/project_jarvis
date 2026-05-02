# 🤖 Project JARVIS

JARVIS is a 100% local, on-device AI assistant designed for macOS. It features complex text-to-text reasoning, visual "Thinking" streaming, and a high-performance web interface.

## 🚀 Key Features

- **Local-Only Intelligence**: Powered by Ollama (Gemma 4) and LiteRT-LM. No data leaves your machine.
- **✨ Modern Streamlit UI**: A premium, ChatGPT-like interface with:
  - **Collapsible Thinking**: See the model's internal reasoning process (auto-collapses after completion).
  - **Real-Time Streaming**: Tokens arrive word-by-word with zero buffering.
  - **Tool Notification Pills**: Visual indicators when JARVIS is using its tools.
- **📱 Mobile Web Interface**: Access JARVIS from any device on your WiFi (Phone, Tablet, etc.).
- **Modular Tools**:
  - 📧 **Automated Email**: Send emails via Gmail SMTP.
  - ✈️ **Flight Tracking**: Real-time flight status via AviationStack.
  - 🖥️ **macOS Automation**: Launch apps (Spotify, WhatsApp, etc.) and run system commands.
  - 🌐 **Web Intelligence**: Search (Tavily), news retrieval, and weather updates.
- **Voice Engine**: Support for wake-word detection and local audio processing.

## 🛠️ Setup

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   pip install streamlit
   ```

2. **Configure Environment**:
   Create a `.env` file with your keys:
   ```env
   TAVILY_API_KEY=your_key
   NEWS_API_KEY=your_key
   GMAIL_ADDRESS=your_email
   GMAIL_APP_PASS=your_app_password
   AVIATIONSTACK_API_KEY=your_key
   ```

3. **Run JARVIS (New Premium UI)**:
   ```bash
   python3 -m streamlit run app.py
   ```

4. **Run JARVIS (Terminal Mode)**:
   ```bash
   python3 main.py
   ```

5. **Run JARVIS (FastAPI Server Mode)**:
   ```bash
   python3 server.py
   ```

## 🏗️ Architecture

- **`app.py`**: Premium Streamlit interface with real-time SSE streaming.
- **`agent_core.py`**: The unified reasoning engine with a "Streaming-First" architecture.
- **`server.py`**: FastAPI-powered web gateway for mobile access.
- **`tools/`**: Extensible tool registry (Weather, News, Gmail, Flights, macOS commands).

## 🛡️ Security

This project uses a `.env` system to protect your credentials. Your `.env` file is ignored by Git to prevent secrets from being pushed to public repositories.

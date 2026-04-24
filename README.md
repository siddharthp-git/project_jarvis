# 🤖 Project JARVIS

JARVIS is a 100% local, on-device AI assistant designed for macOS. It features complex text-to-text reasoning, visual "Thinking" streaming, and a mobile-optimized web interface.

## 🚀 Key Features
- **Local-Only Intelligence**: Powered by Ollama (Gemma 4) and LiteRT-LM. No data leaves your machine.
- **📱 Mobile Web Interface**: Access Jarvis from any device on your WiFi (Phone, Tablet, etc.) using the built-in FastAPI server.
- **Visual "Thinking"**: See the assistant's internal reasoning process in real-time.
- **Modular Tools**:
  - 📧 **Automated Email**: Send emails via Gmail SMTP (bypasses sandbox restrictions).
  - 🖥️ **macOS Automation**: Launch apps (Spotify, WhatsApp, etc.) and run system commands.
  - 🌐 **Web Intelligence**: Search (Tavily), news retrieval, and weather updates.
- **Voice Engine**: Built-in support for wake-word detection and local audio processing.

## 🛠️ Setup

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
2. **Configure Environment**:
   Create a `.env` file based on the placeholders in `config.py`.
   ```env
   TAVILY_API_KEY=your_key
   NEWS_API_KEY=your_key
   GMAIL_ADDRESS=your_email
   GMAIL_APP_PASS=your_app_password
   ```
3. **Run JARVIS (Terminal Mode)**:
   ```bash
   python3 main.py
   ```
4. **Run JARVIS (Mobile/Server Mode)**:
   ```bash
   python3 server.py
   ```
   *Then access on your phone via the IP address shown in the terminal (e.g., `http://192.168.x.x:8000`).*

## 🏗️ Architecture
- **`agent_core.py`**: The unified reasoning engine shared across all interfaces.
- **`server.py`**: FastAPI-powered web gateway with a custom CSS/JS UI.
- **`main.py`**: High-performance terminal interface.
- **`tools/`**: Extensible tool registry for macOS automation and API integrations.

## 🛡️ Security
This project uses a `.env` system to protect your credentials. Your `.env` file is ignored by Git to prevent secrets from being pushed to public repositories.

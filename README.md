# 🤖 Project JARVIS

JARVIS is a 100% local, on-device AI assistant designed for macOS. It features complex text-to-text reasoning, visual streaming, and modular automation tools.

## 🚀 Key Features
- **Local-Only Intelligence**: Powered by Ollama (Gemma 4) and LiteRT-LM. No data leaves your machine.
- **Visual "Thinking"**: See the assistant's internal reasoning process in real-time.
- **Modular Tools**:
  - 📧 **Automated Email**: Send emails via Gmail SMTP.
  - 🖥️ **macOS Automation**: Launch apps and system commands.
  - 🌐 **Web Intelligence**: Search (Tavily) and news retrieval.
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
3. **Run JARVIS**:
   ```bash
   python3 main.py
   ```

## 🛡️ Security
This project uses a `.env` system to protect your credentials. Never commit your `.env` file to version control.

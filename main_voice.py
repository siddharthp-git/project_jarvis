#!/usr/bin/env python3
import time
from audio_service import AudioService
from tts_service import TTSService
from voice_engine import VoiceEngine
from config import WAKE_WORD
from tools import TOOL_REGISTRY

SYSTEM_PROMPT = (
    "You are Jarvis, a helpful and efficient on-device AI assistant. "
    "Maintain a helpful, concise, and professional tone. "
    "You have access to tools for real-time information. "
    "TOOL PREFERENCE: For weather, news, time, and currency conversion, you MUST use the specialized tools provided. "
    "ONLY use 'web_search' as a fallback if the specialized tools are not applicable. "
    "Use 'read_webpage' for detailed reading and 'open_in_chrome' for visual browser requests. "
    "Always provide accurate information based on the tool outputs. "
    "REPLY ONLY WITH THE TRANSCRIPTION OF YOUR SPEECH. "
    "CRITICAL: DO NOT use any Markdown (asterisks, hashtags, underscores, etc.) in your final response. "
    "Always speak in clear, plain text suitable for a voice assistant."
)

def main():
    # Initialize services
    print("\n  ========================================================")
    print("  🤖 JARVIS MULTIMODAL MODE — Powered by LiteRT-LM      ")
    print(f"  Status: Initializing Engines...                       ")
    print("  ========================================================\n")
    
    audio = AudioService()
    tts = TTSService()
    engine = VoiceEngine(system_prompt=SYSTEM_PROMPT, tools=TOOL_REGISTRY)
    
    print(f"\n  ✅ System Ready. Listening for commands...")
    tts.speak("I am ready and listening, sir.")

    while True:
        # Step 2: Capture command audio
        b64_audio = audio.capture_command_b64()
        
        if not b64_audio:
            # Instead of breaking, we just continue listening in always-active mode
            continue
        
        # Step 3: Process through multimodal brain
        print("  🤔 Processing...")
        result = engine.process_audio(b64_audio)
        
        transcription = result.get("transcription")
        response = result.get("response")

        if transcription:
            print(f"  📝 You: {transcription}")
            
            # Check for exit commands
            exit_phrases = ["goodbye", "go to sleep", "stop listening"]
            if any(phrase in transcription.lower() for phrase in exit_phrases):
                tts.speak("Goodbye sir. I will stay active if you need more help.")
                # We stay in the loop but skip this turn
                continue
        
        if response:
            print(f"  🔊 Jarvis: {response}")
            tts.speak(response)
        else:
            print("  ❌ No response generated.")
            # We don't break, we just keep listening
            continue

        print("  👂 Listening...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n  👋 System terminated.")

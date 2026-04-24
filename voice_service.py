import speech_recognition as sr
import subprocess
import time
import asyncio
import edge_tts
import os
import base64
import io
from config import WAKE_WORD, MODEL
from ollama_client import chat_request

class VoiceService:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.voice = "en-GB-RyanNeural"  # Premium Jarvis-like voice
        
        # Optimize recognizer
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.8
        
    async def _async_speak(self, text):
        """Internal async helper for Edge TTS."""
        output_file = "jarvis_temp.mp3"
        communicate = edge_tts.Communicate(text, self.voice)
        await communicate.save(output_file)
        
        try:
            # afplay is a built-in macOS audio player
            subprocess.run(["afplay", output_file], check=True)
        finally:
            if os.path.exists(output_file):
                os.remove(output_file)

    def speak(self, text):
        """Uses Edge TTS for high-quality voice output."""
        if not text:
            return
        print(f"\n  🔊 Jarvis: {text}")
        try:
            # Since our loop is sync, we run the async TTS task here
            asyncio.run(self._async_speak(text))
        except Exception as e:
            print(f"  ❌ Error in TTS: {e}")
            # Fallback to native 'say' if Edge TTS fails
            subprocess.run(["say", text])

    def listen(self, prompt_text="Listening..."):
        """Captures audio and transcribes it using the local Gemma 4 model."""
        with self.microphone as source:
            print(f"\n  🎤 {prompt_text}")
            # Adjust for ambient noise
            self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio = self.recognizer.listen(source, timeout=10, phrase_time_limit=10)
        
        try:
            print(f"  🤔 Recognizing (Model: {MODEL})...")
            
            # Convert audio to WAV format for the multimodal model
            wav_data = audio.get_wav_data()
            b64_audio = base64.b64encode(wav_data).decode("utf-8")
            
            # Send to Ollama for native transcription
            # We use a clean prompt to get just the text
            messages = [
                {
                    "role": "user",
                    "content": "Transcribe this audio. Return ONLY the transcribed text.",
                    "audio": [b64_audio]
                }
            ]
            
            response = chat_request(messages, use_tools=False)
            
            # DEBUG: Print the raw response to help troubleshoot
            # print(f"  DEBUG: Raw Response from {MODEL}: {json.dumps(response, indent=2)}")
            
            query = response.get("message", {}).get("content", "").strip()
            
            # If content is empty, check if it's because of the prompt
            if not query:
                print(f"  ⚠️  Model {MODEL} responded but content was empty.")
                # Try a fallback simple prompt if the first one failed
                # query = self._fallback_transcription(b64_audio)
            
            if query:
                print(f"  📝 You: {query}")
                return query.lower()
            else:
                print("  ❌ Model returned empty transcription")
                return ""
                
        except Exception as e:
            print(f"  ❌ Transcription error: {e}")
            return ""

    def wait_for_wake_word(self, keyword=WAKE_WORD):
        """Keeps listening and blocks until the wake word is detected."""
        print(f"\n  👂 JARVIS is in background... (Waiting for '{keyword}')")
        
        while True:
            with self.microphone as source:
                # Use a very short timeout for "always listening" to keep it responsive
                try:
                    audio = self.recognizer.listen(source, timeout=2, phrase_time_limit=3)
                    text = self.recognizer.recognize_google(audio).lower()
                    if keyword in text:
                        print(f"  ✨ {keyword.upper()} detected!")
                        return True
                except (sr.UnknownValueError, sr.WaitTimeoutError):
                    continue
                except Exception as e:
                    print(f"  ❌ Background listen error: {e}")
                    time.sleep(1)

if __name__ == "__main__":
    # Test
    vs = VoiceService()
    vs.speak("Voice system initialized. Testing listen function.")
    cmd = vs.listen("Say something to confirm.")
    vs.speak(f"You said: {cmd}")

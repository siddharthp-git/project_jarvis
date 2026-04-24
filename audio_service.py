"""Low-level Audio Service for Jarvis."""

import base64
import numpy as np
import speech_recognition as sr
from config import WAKE_WORD

class AudioService:
    """Handles raw microphone input and wake-word detection."""

    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        
        # TIMING THRESHOLDS (Increased for user patience)
        # Seconds of non-speaking audio before a phrase is considered complete
        self.recognizer.pause_threshold = 3.0
        # Seconds of non-speaking audio to keep on both sides of the phrase
        self.recognizer.non_speaking_duration = 1.5
        # Minimum seconds of speaking audio before it's considered a phrase
        self.recognizer.phrase_threshold = 0.2
        
        # ENERGY THRESHOLDS (Lowered for sensitivity)
        self.recognizer.dynamic_energy_threshold = False
        self.recognizer.energy_threshold = 300
        
        # Wake word variants
        self.wake_variants = [WAKE_WORD.lower(), "jarvis", "hey jarvis", "hi jarvis", "wake up"]
        
        # Calibration
        with self.microphone as source:
            print("Audio: Calibrating for ambient noise...")
            self.recognizer.adjust_for_ambient_noise(source, duration=0.5)

    def wait_for_wake_word(self):
        """Listen in the background for any wake word variant."""
        with self.microphone as source:
            # Temporarily enable dynamic sensitivity to catch soft whispers in quiet rooms
            self.recognizer.dynamic_energy_threshold = True
            
            try:
                # Use a specific pause_threshold for the wake-word to stay responsive
                orig_pause = self.recognizer.pause_threshold
                self.recognizer.pause_threshold = 0.6
                
                audio = self.recognizer.listen(source, timeout=None, phrase_time_limit=3)
                text = self.recognizer.recognize_google(audio).lower()
                
                self.recognizer.pause_threshold = orig_pause # Restore
                self.recognizer.dynamic_energy_threshold = False # Back to stable mode
                
                if any(variant in text for variant in self.wake_variants):
                    return True
            except:
                self.recognizer.dynamic_energy_threshold = False # Restore on error
                pass
        return False

    def capture_command_b64(self) -> str:
        """Capture audio for a command and return as base64."""
        with self.microphone as source:
            print("🎤 Listening...")
            try:
                # timeout: How long to wait for speech to START
                # phrase_time_limit: Max duration of the captured speech
                audio = self.recognizer.listen(source, timeout=10, phrase_time_limit=45)
                # Convert to WAV format bytes
                wav_data = audio.get_wav_data(convert_rate=16000, convert_width=2)
                return base64.b64encode(wav_data).decode("utf-8")
            except Exception as e:
                print(f"Audio Error/Timeout: {e}")
                return None

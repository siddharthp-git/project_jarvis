import os
import platform
import sys
import re
import numpy as np

def _is_apple_silicon() -> bool:
    return sys.platform == "darwin" and platform.machine() == "arm64"

class TTSService:
    """Unified TTS interface for Jarvis."""

    def __init__(self, use_mlx=True):
        self.backend = None
        self.sample_rate = 24000
        
        if _is_apple_silicon() and use_mlx:
            try:
                from mlx_audio.tts.generate import load_model
                print("TTS: Loading mlx-audio (Apple GPU accelerated)...")
                self.backend = load_model("mlx-community/Kokoro-82M-bf16")
                self.sample_rate = self.backend.sample_rate
                # Warmup
                list(self.backend.generate(text="Warmup", voice="bm_george", speed=1.0))
            except ImportError:
                print("TTS: mlx-audio not found, falling back to ONNX")
        
        if not self.backend:
            import kokoro_onnx
            from huggingface_hub import hf_hub_download
            print("TTS: Loading kokoro-onnx (CPU)...")
            model_path = hf_hub_download("fastrtc/kokoro-onnx", "kokoro-v1.0.onnx")
            voices_path = hf_hub_download("fastrtc/kokoro-onnx", "voices-v1.0.bin")
            self.backend = kokoro_onnx.Kokoro(model_path, voices_path)
            self.sample_rate = 24000

    def clean_text_for_speech(self, text: str) -> str:
        """Sanitize text by removing Markdown and symbols that sound weird in TTS."""
        if not text:
            return ""
            
        # 1. Remove Markdown URL patterns [text](url) -> text
        text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
        
        # 2. Replace bullet points at starts of lines with a pause (comma)
        text = re.sub(r'(^|\n)[\s]*[\*\-][\s]+', r'\1, ', text)
        
        # 3. Strip bold/italic markers (*, _, **)
        text = text.replace('**', '').replace('__', '')
        text = text.replace('*', '').replace('_', '')
        
        # 4. Strip hashtags (titles)
        text = re.sub(r'#+', '', text)
        
        # 5. Clean up multiple spaces and newlines
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text

    def generate(self, text: str, voice: str = "bm_george", speed: float = 1.0) -> np.ndarray:
        """Generate audio PCM data from text."""
        cleaned_text = self.clean_text_for_speech(text)
        if not cleaned_text:
            return np.array([], dtype=np.float32)

        if hasattr(self.backend, "generate"): # MLX
            results = list(self.backend.generate(text=cleaned_text, voice=voice, speed=speed))
            return np.concatenate([np.array(r.audio) for r in results])
        else: # ONNX
            pcm, _sr = self.backend.create(cleaned_text, voice=voice, speed=speed)
            return pcm

    def speak(self, text: str):
        """Generate and play audio directly."""
        import sounddevice as sd
        cleaned_text = self.clean_text_for_speech(text)
        if not cleaned_text:
            return
            
        pcm = self.generate(cleaned_text)
        sd.play(pcm, self.sample_rate)
        sd.wait()

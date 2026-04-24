"""LiteRT-LM Multimodal Engine for Jarvis (Gemma 4 E2B)."""

import os
import time
import litert_lm
from huggingface_hub import hf_hub_download

HF_REPO = "litert-community/gemma-4-E2B-it-litert-lm"
HF_FILENAME = "gemma-4-E2B-it.litertlm"

class VoiceEngine:
    """Agentic multimodal engine for Jarvis using LiteRT-LM (Local Only)."""

    def __init__(self, system_prompt: str, tools: dict = None):
        self.model_path = self._resolve_model_path()
        print(f"Engine: Loading local Gemma 4 E2B...")
        
        self.engine = litert_lm.Engine(
            self.model_path,
            backend=litert_lm.Backend.GPU,
            vision_backend=litert_lm.Backend.GPU,
            audio_backend=litert_lm.Backend.CPU,
            max_num_tokens=8192,
        )
        self.engine.__enter__()
        
        self.system_prompt = system_prompt
        self.external_tools = tools or {}
        self.tool_result = {}

    def _resolve_model_path(self) -> str:
        """Download model if not present."""
        path = os.environ.get("MODEL_PATH", "")
        if path:
            return path
        return hf_hub_download(repo_id=HF_REPO, filename=HF_FILENAME)

    def respond_to_user(self, transcription: str, response: str) -> str:
        """Respond to the user's voice message. Use this only when you have the final answer.

        Args:
            transcription: Exact transcription of what the user said in the audio.
            response: Your conversational response to the user. Provide complete and detailed information.
        """
        self.tool_result["transcription"] = transcription
        self.tool_result["response"] = response
        return "OK"

    def process_text(self, text_command: str) -> str:
        """Process text using the local engine."""
        self.tool_result = {}
        exposed_tools = [self.respond_to_user] + list(self.external_tools.values())
        
        conversation = self.engine.create_conversation(
            messages=[{"role": "system", "content": self.system_prompt}],
            tools=exposed_tools,
        )
        
        with conversation:
            payload = {"role": "user", "content": text_command}
            max_turns = 5
            turn = 0
            
            while turn < max_turns:
                turn += 1
                response = conversation.send_message(payload)
                
                if self.tool_result:
                    return self.tool_result.get("response", "").strip()

                if "tool_calls" in response and response["tool_calls"]:
                    tool_responses = []
                    for call in response["tool_calls"]:
                        name = call["function"]["name"]
                        args = call["function"]["arguments"]
                        print(f"  🛠️  Local Tool: {name}({args})")
                        
                        if name in self.external_tools:
                            try:
                                result = self.external_tools[name](**args)
                                tool_responses.append(result)
                            except Exception as e:
                                tool_responses.append(f"Error: {str(e)}")
                        else:
                            tool_responses.append(f"Tool {name} not found.")

                    payload = {"role": "tool", "content": "\n\n".join(tool_responses)}
                    continue
                break
                
            return response["content"][0]["text"].strip() if "content" in response else "No response generated."

    def process_audio(self, b64_audio: str) -> dict:
        """Process audio through the local agentic loop."""
        self.tool_result = {}
        exposed_tools = [self.respond_to_user] + list(self.external_tools.values())
        
        conversation = self.engine.create_conversation(
            messages=[{"role": "system", "content": self.system_prompt}],
            tools=exposed_tools,
        )
        
        with conversation:
            content = [
                {"type": "audio", "blob": b64_audio},
                {"type": "text", "text": "The user just spoke to you. Respond to what they said."}
            ]
            
            payload = {"role": "user", "content": content}
            max_turns = 5
            turn = 0
            t_start = time.time()

            while turn < max_turns:
                turn += 1
                response = conversation.send_message(payload)
                
                if self.tool_result:
                    elapsed = time.time() - t_start
                    return {
                        "transcription": self.tool_result.get("transcription", "").strip(),
                        "response": self.tool_result.get("response", "").strip(),
                        "time": elapsed,
                        "method": "local_agent"
                    }

                if "tool_calls" in response and response["tool_calls"]:
                    tool_responses = []
                    for call in response["tool_calls"]:
                        name = call["function"]["name"]
                        args = call["function"]["arguments"]
                        print(f"  🛠️  Local Tool: {name}({args})")
                        
                        if name in self.external_tools:
                            try:
                                result = self.external_tools[name](**args)
                                tool_responses.append(result)
                            except Exception as e:
                                tool_responses.append(f"Error: {str(e)}")
                        else:
                            tool_responses.append(f"Tool {name} not found.")

                    payload = {"role": "tool", "content": "\n\n".join(tool_responses)}
                    continue
                
                break

            elapsed = time.time() - t_start
            return {
                "transcription": None,
                "response": response["content"][0]["text"].strip() if "content" in response else "Error processing audio.",
                "time": elapsed,
                "method": "local_direct"
            }

    def __del__(self):
        if hasattr(self, "engine"):
            self.engine.__exit__(None, None, None)

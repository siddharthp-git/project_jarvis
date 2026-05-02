#!/usr/bin/env python3
import json
import sys
from config import MODEL, MAX_TOOL_ROUNDS, CONVERSATION_HISTORY_LIMIT
from ollama_client import chat_request
from tools import TOOL_REGISTRY

def process_tool_calls(tool_calls: list) -> list:
    """Execute tool calls and return tool response messages."""
    tool_messages = []

    for tc in tool_calls:
        func_name = tc["function"]["name"]
        func_args = tc["function"].get("arguments", {})

        print(f"\n  🔧 {func_name}({json.dumps(func_args, ensure_ascii=False)[:80]})")

        if func_name in TOOL_REGISTRY:
            try:
                result = TOOL_REGISTRY[func_name](**func_args)
            except Exception as e:
                result = json.dumps({"status": "error", "message": str(e)})
                print(f"  ❌ Error executing {func_name}: {e}")
        else:
            result = json.dumps({"error": f"Unknown tool: {func_name}"})
            print(f"  ❌ Unknown tool: {func_name}")

        tool_messages.append({
            "role": "tool",
            "content": result,
            "tool_call_id": tc.get("id", ""),
        })

    return tool_messages


def main():
    print("\n  ========================================================")
    print("  🤖 JARVIS TEXT MODE — Powered by Gemma 4 (Local)      ")
    print("  ========================================================\n")
    print("  Type your message. Type 'quit' to exit.\n")

    messages = [
        {
            "role": "system",
            "content": (
"You are Jarvis, a highly efficient local AI assistant.\n\n"
"CORE BEHAVIOR RULES:\n"
"1. ALWAYS wrap your internal reasoning or chain-of-thought inside <think>...</think> tags if a question requires multi-step thought.\n"
"2. ALWAYS use tools when searching for real-time information.\n"
"3. Keep your responses CONCISE and professional.\n"
"4. Do NOT provide any conversational text when calling a tool.\n"
"5. Never say 'I am searching' or 'Please wait'."
"6. Give answer in organised way - using bullet points if needed"
"7.Think step by step before answering. Show your reasoning in <think> tags, then provide the final answer."
            ),
        }
    ]

    while True:
        try:
            user_input = input("  You ➜  ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n\n  👋 Goodbye!")
            break

        if not user_input:
            continue
        if user_input.lower() in ("quit", "exit", "bye"):
            print("\n  👋 Goodbye!")
            break

        messages.append({"role": "user", "content": user_input})
        print("\n  ⏳ Thinking...", end="", flush=True)

        # Agentic loop
        for round_num in range(MAX_TOOL_ROUNDS):
            full_content = ""
            tool_calls = []
            is_thinking = False
            
            print(f"\r{'':50}\r  Jarvis ➜  ", end="", flush=True)

            from ollama_client import chat_request_stream
            for chunk in chat_request_stream(messages):
                msg_chunk = chunk.get("message", {})
                
                # Check for tool calls
                if msg_chunk.get("tool_calls"):
                    tool_calls.extend(msg_chunk["tool_calls"])
                
                # Stream content
                content = msg_chunk.get("content", "")
                if content:
                    full_content += content
                    
                    # Handle thinking tags (dim the thinking text)
                    if "<think>" in content:
                        is_thinking = True
                        content = content.replace("<think>", "\033[90m💭 Thinking: ") # Dim start
                    if "</think>" in content:
                        is_thinking = False
                        content = content.replace("</think>", "\033[0m\n\n  ") # Reset end
                    
                    print(content, end="", flush=True)

            # Store the full assistant message
            assistant_msg = {"role": "assistant", "content": full_content}
            if tool_calls:
                assistant_msg["tool_calls"] = tool_calls
            
            messages.append(assistant_msg)

            if tool_calls:
                print(f"\n\n  🛠️  Using tools (Round {round_num + 1})...")
                tool_responses = process_tool_calls(tool_calls)
                messages.extend(tool_responses)
                print("\n  ⏳ Jarvis is thinking...", end="", flush=True)
            else:
                if not is_thinking: # Ensure we didn't end on a dimmed state
                    print("\033[0m", end="")
                print("\n")
                break
        else:
            print("\n  ⚠️  Max tool rounds reached.")

        # History management
        if len(messages) > CONVERSATION_HISTORY_LIMIT:
            messages = [messages[0]] + messages[-(CONVERSATION_HISTORY_LIMIT-1):]

if __name__ == "__main__":
    main()

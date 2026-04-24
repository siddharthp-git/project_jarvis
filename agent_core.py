import json
from config import MODEL, MAX_TOOL_ROUNDS, CONVERSATION_HISTORY_LIMIT
from ollama_client import chat_request, chat_request_stream
from tools import TOOL_REGISTRY

SYSTEM_MESSAGE = {
    "role": "system",
    "content": (
        "You are Jarvis, a highly efficient local AI assistant.\n\n"
        "CORE BEHAVIOR RULES:\n"
        "1. ALWAYS wrap your internal reasoning or chain-of-thought inside <think>...</think> tags if a question requires multi-step thought.\n"
        "2. ALWAYS use tools when searching for real-time information.\n"
        "3. Keep your responses CONCISE and professional.\n"
        "4. Do NOT provide any conversational text when calling a tool.\n"
        "5. Never say 'I am searching' or 'Please wait'."
    ),
}

def process_tool_calls(tool_calls: list) -> list:
    """Execute tool calls and return tool response messages."""
    tool_messages = []
    for tc in tool_calls:
        func_name = tc["function"]["name"]
        func_args = tc["function"].get("arguments", {})

        print(f"\n  🔧 Executing Tool: {func_name}")

        if func_name in TOOL_REGISTRY:
            try:
                result = TOOL_REGISTRY[func_name](**func_args)
            except Exception as e:
                result = json.dumps({"status": "error", "message": str(e)})
        else:
            result = json.dumps({"error": f"Unknown tool: {func_name}"})

        tool_messages.append({
            "role": "tool",
            "content": result,
            "tool_call_id": tc.get("id", ""),
        })
    return tool_messages

def run_agent(user_input: str, history: list = None):
    """
    Core agent reasoning loop.
    Returns the final assistant response string.
    """
    if history is None:
        messages = [SYSTEM_MESSAGE]
    else:
        messages = history

    messages.append({"role": "user", "content": user_input})

    final_response = ""
    
    for _ in range(MAX_TOOL_ROUNDS):
        full_content = ""
        tool_calls = []
        
        # We use non-streaming here for simpler backend logic, 
        # but you can refactor for streaming if needed.
        response = chat_request(messages)
        message = response.get("message", {})
        
        full_content = message.get("content", "")
        tool_calls = message.get("tool_calls", [])
        
        # Store message
        assistant_msg = {"role": "assistant", "content": full_content}
        if tool_calls:
            assistant_msg["tool_calls"] = tool_calls
        
        messages.append(assistant_msg)
        final_response += full_content

        if tool_calls:
            tool_responses = process_tool_calls(tool_calls)
            messages.extend(tool_responses)
        else:
            break
            
    return final_response, messages

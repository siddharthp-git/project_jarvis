import streamlit as st
import json
import time
from agent_core import SYSTEM_MESSAGE, run_agent_stream

st.set_page_config(page_title="JARVIS AI Assistant", page_icon="🤖", layout="wide")

# Custom CSS for ChatGPT-like design
st.markdown("""
<style>
    .stChatMessage { border-radius: 15px; padding: 15px; margin-bottom: 10px; }
    .think-container {
        background-color: #f0f2f6;
        border-left: 5px solid #3b82f6;
        padding: 10px;
        border-radius: 5px;
        margin-bottom: 10px;
        font-family: 'Courier New', Courier, monospace;
        font-size: 0.85em;
        color: #555;
    }
    .tool-pill {
        display: inline-block;
        padding: 2px 10px;
        border-radius: 10px;
        background-color: #1e293b;
        color: #94a3b8;
        font-size: 0.7em;
        margin-bottom: 5px;
        border: 1px solid #334155;
    }
</style>
""", unsafe_allow_html=True)

st.title("🤖 JARVIS")
st.caption("Powered by Gemma 4 (Local)")

if "messages" not in st.session_state:
    st.session_state.messages = [SYSTEM_MESSAGE]

# Display history
for msg in st.session_state.messages:
    if msg["role"] == "system": continue
    with st.chat_message(msg["role"]):
        content = msg["content"]
        if "<think>" in content and "</think>" in content:
            parts = content.split("</think>")
            think_text = parts[0].replace("<think>", "").strip()
            answer_text = parts[1].strip()
            with st.expander("Thought for a moment", expanded=False):
                st.write(think_text)
            st.write(answer_text)
        else:
            st.write(content)

# Chat input
if prompt := st.chat_input("Ask Jarvis..."):
    st.chat_message("user").write(prompt)
    
    with st.chat_message("assistant"):
        think_placeholder = st.empty()
        answer_placeholder = st.empty()
        status_placeholder = st.empty()
        
        full_answer = ""
        full_thought = ""
        history_copy = list(st.session_state.messages)
        
        for sse_line in run_agent_stream(prompt, history_copy):
            if not sse_line.startswith("data: "): continue
            try:
                data = json.loads(sse_line[6:])
            except: continue
            
            if data["type"] == "tool":
                status_placeholder.markdown(f'<div class="tool-pill">⚙ Executing {data["name"]}...</div>', unsafe_allow_html=True)
            
            elif data["type"] == "think":
                full_thought += data["text"]
                with think_placeholder.expander("Thinking...", expanded=True):
                    st.write(full_thought + "▌")

            elif data["type"] == "token":
                # Once we get a normal token, collapse the thinking box if it was open
                full_answer += data["text"]
                answer_placeholder.write(full_answer + "▌")
            
            elif data["type"] == "done":
                status_placeholder.empty()
                if full_thought:
                    with think_placeholder.expander("Thought for a moment", expanded=False):
                        st.write(full_thought)
                answer_placeholder.write(full_answer)
                
        st.session_state.messages = history_copy



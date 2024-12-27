import os
import json
import html
from datetime import datetime
from typing import List, Dict, Optional

import streamlit as st
import anthropic

ANTHROPIC_API_KEY = open(os.path.expanduser('~/.anthropic'),'r').read()[:-1]


class SystemPromptManager:
    def __init__(self, file_path: str = "system_prompts.json"):
        self.file_path = file_path
        self.prompts = self._load_prompts()

    def _load_prompts(self) -> Dict[str, str]:
        if os.path.exists(self.file_path):
            with open(self.file_path, 'r') as f:
                return json.load(f)
        return {"Default": "You are Claude, a helpful AI assistant."}

    def save_prompt(self, name: str, content: str) -> None:
        self.prompts[name] = content
        with open(self.file_path, 'w') as f:
            json.dump(self.prompts, f, indent=2)

    def get_prompt(self, name: str) -> Optional[str]:
        return self.prompts.get(name)

    def get_prompt_names(self) -> list[str]:
        return list(self.prompts.keys())


class ChatManager:
    def __init__(self, file_path: str = "saved_chats.json"):
        self.file_path = file_path
        self.chats = self._load_chats()

    def _load_chats(self) -> Dict[str, List[Dict[str, str]]]:
        if os.path.exists(self.file_path):
            with open(self.file_path, 'r') as f:
                return json.load(f)
        return {}

    def save_chat(self, name: str, messages: List[Dict[str, str]]) -> None:
        self.chats[name] = messages
        with open(self.file_path, 'w') as f:
            json.dump(self.chats, f, indent=2)

    def delete_chat(self, name: str) -> None:
        if name in self.chats:
            del self.chats[name]
            with open(self.file_path, 'w') as f:
                json.dump(self.chats, f, indent=2)

    def get_chat(self, name: str) -> Optional[List[Dict[str, str]]]:
        return self.chats.get(name)

    def get_chat_names(self) -> list[str]:
        return list(self.chats.keys())


def init_session_state():
    """Initialize session state variables"""
    if 'client' not in st.session_state:
        st.session_state.client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    if 'messages' not in st.session_state:
        st.session_state.messages = []

def apply_custom_css():
    """Apply custom CSS styling"""
    st.markdown("""
    <style>
        .element-container, .stMarkdown, div[data-testid="stMarkdownContainer"] {
            background-color: transparent !important;
        }
        
        .element-container {
            padding: 0 !important;
            margin: 0 !important;
        }
        
        .stTextInput>div>div>input {
            background-color: #262626;
            color: white;
        }
        
        .chat-container {
            display: flex;
            flex-direction: column;
            gap: 0.5rem;
            padding: 0.5rem;
        }
        
        .user-message {
            background-color: #3B82F6;
            color: #ffffff;
            padding: 1rem;
            border-radius: 1rem;
            margin: 0.2rem 0;
            margin-left: 20%;
            max-width: 80%;
            float: right;
            clear: both;
        }
        
        .assistant-message {
            background-color: #262626;
            color: #ffffff;
            padding: 1rem;
            border-radius: 1rem;
            margin: 0.2rem 0;
            margin-right: 20%;
            max-width: 80%;
            float: left;
            clear: both;
        }
        
        pre {
            background-color: #363636 !important;
            padding: 1rem !important;
            border-radius: 0.5rem !important;
            margin: 0.5rem 0 !important;
            white-space: pre-wrap !important;
            overflow-x: auto;
        }
        
        code {
            color: #E0E0E0 !important;
        }
        
        .message-timestamp {
            font-size: 0.8rem;
            color: rgba(255, 255, 255, 0.7);
            margin-top: 0.2rem;
            text-align: right;
        }
    </style>
    """, unsafe_allow_html=True)

def create_anthropic_client() -> anthropic.Anthropic:
    """Create and return an Anthropic client"""
    return anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)


def get_llm_response(client: anthropic.Anthropic, messages: List[Dict[str, str]], system_prompt: str) -> str:
    """Get response from LLM given a message history and system prompt"""
    response = client.messages.create(
        model="claude-3-opus-20240229",
        max_tokens=1024,
        system=system_prompt,  # Pass system prompt directly
        messages=[m for m in messages if m["role"] != "system"]  # Filter out any system messages
    )
    return response.content[0].text

def format_message(content: str, role: str, timestamp: str) -> str:
    """Format a single message with appropriate HTML styling"""
    css_class = "user-message" if role == "user" else "assistant-message"
    # Don't escape the content - let Streamlit handle markdown
    return f"""
        <div class="{css_class}">
            {content}
            <div class="message-timestamp">{timestamp}</div>
        </div>
    """

def render_messages(messages: List[Dict[str, str]]) -> None:
    """Render all messages in the chat interface"""
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    timestamp = datetime.now().strftime("%H:%M")
    
    for message in messages:
        formatted_message = format_message(
            content=message["content"],
            role=message["role"],
            timestamp=timestamp
        )
        st.markdown(formatted_message, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

def initialize_chat_state() -> tuple[anthropic.Anthropic, List[Dict[str, str]]]:
    """Initialize or retrieve chat state"""
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'client' not in st.session_state:
        st.session_state.client = create_anthropic_client()
    
    return st.session_state.client, st.session_state.messages

def clear_chat_history(messages: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """Clear the chat history and return empty list"""
    return []

def create_load_chat_modal(chat_manager: ChatManager) -> Optional[str]:
    """Create a modal for loading saved chats"""
    with st.form("load_chat_form"):
        st.subheader("Load Saved Chat")
        saved_chats = chat_manager.get_chat_names()
        
        if not saved_chats:
            st.write("No saved chats found.")
            if st.form_submit_button("Close"):
                return "cancel"
            return None
        
        selected_chat = st.selectbox(
            "Select a chat to load",
            saved_chats
        )
        
        submitted = st.form_submit_button("Load Chat", use_container_width=True)
        cancelled = st.form_submit_button("Cancel", use_container_width=True)
        
        if submitted and selected_chat:
            return selected_chat
        if cancelled:
            return "cancel"
    return None

def create_new_prompt_modal():
    """Create a modal for new system prompt input"""
    with st.form("new_prompt_form"):
        st.subheader("Create New System Prompt")
        prompt_name = st.text_input("Prompt Name")
        prompt_content = st.text_area("Prompt Content", height=200)
        
        submitted = st.form_submit_button("Save Prompt", use_container_width=True)
        cancelled = st.form_submit_button("Cancel", use_container_width=True)
        
        if submitted and prompt_name and prompt_content:
            return prompt_name, prompt_content
        if cancelled:
            return "cancel", "cancel"
    return None, None

def main():
    """Main application function"""
    st.set_page_config(page_title="Chat with Claude", layout="wide")
    apply_custom_css()
    
    # Initialize managers
    if 'prompt_manager' not in st.session_state:
        st.session_state.prompt_manager = SystemPromptManager()
    if 'chat_manager' not in st.session_state:
        st.session_state.chat_manager = ChatManager()
    if 'current_chat_name' not in st.session_state:
        st.session_state.current_chat_name = None
    
    client, messages = initialize_chat_state()
    
    # Main title
    st.title("🔥 Sonnet 3.5 Burner")
    
    # Sidebar controls
    with st.sidebar:
        st.title("Chat Controls")
        
        # Chat management section
        st.subheader("Chat Management")
        
        # Chat name input
        current_name = st.session_state.current_chat_name or ""
        new_chat_name = st.text_input("Name current chat", value=current_name)
        
        if new_chat_name != current_name:
            if new_chat_name:  # Save chat if named
                st.session_state.chat_manager.save_chat(new_chat_name, messages)
                st.session_state.current_chat_name = new_chat_name
            else:  # Unnamed chat
                st.session_state.current_chat_name = None
        
        # Load and Clear chat buttons
        if st.button("📂 Load Chat History", use_container_width=True):
            st.session_state.show_load_chat_modal = True
            
        if st.button("🗑️ Clear Chat History", type="secondary", use_container_width=True):
            if st.session_state.current_chat_name:
                st.session_state.chat_manager.delete_chat(st.session_state.current_chat_name)
            st.session_state.messages = clear_chat_history(messages)
            st.session_state.current_chat_name = None
            st.rerun()
        
        st.markdown("---")        
        
        # System prompt section
        st.subheader("System Prompts")
        
        # System prompt selector
        selected_prompt = st.selectbox(
            "Select Prompt",
            st.session_state.prompt_manager.get_prompt_names(),
            index=0
        )
        
        # Show current system prompt
        with st.expander("View Current Prompt"):
            st.write(st.session_state.prompt_manager.get_prompt(selected_prompt))
        
        # New prompt button
        if st.button("➕ New System Prompt", use_container_width=True):
            st.session_state.show_prompt_modal = True
    
    # Handle load chat modal
    if st.session_state.get('show_load_chat_modal', False):
        selected_chat = create_load_chat_modal(st.session_state.chat_manager)
        if selected_chat == "cancel":
            st.session_state.show_load_chat_modal = False
            st.rerun()
        elif selected_chat:
            loaded_chat = st.session_state.chat_manager.get_chat(selected_chat)
            if loaded_chat:
                st.session_state.messages = loaded_chat
                st.session_state.current_chat_name = selected_chat
                st.session_state.show_load_chat_modal = False
                st.rerun()

    # Handle new prompt modal
    if st.session_state.get('show_prompt_modal', False):
        name, content = create_new_prompt_modal()
        if name == "cancel":
            st.session_state.show_prompt_modal = False
            st.rerun()
        elif name and content:
            st.session_state.prompt_manager.save_prompt(name, content)
            st.session_state.show_prompt_modal = False
            st.rerun()    

    if prompt := st.chat_input("What would you like to know?"):
        # First update messages with user input and render
        messages = messages + [{"role": "user", "content": prompt}]
        st.session_state.messages = messages
        render_messages(messages)
        
        # Then show spinner while getting response
        with st.spinner("Thinking..."):
            # Get system prompt
            system_prompt = st.session_state.prompt_manager.get_prompt(selected_prompt)
            
            # Get response passing system prompt separately
            response = get_llm_response(client, messages, system_prompt)
            messages = messages + [{"role": "assistant", "content": response}]
            st.session_state.messages = messages
            
            # Save chat if it's named
            if st.session_state.current_chat_name:
                st.session_state.chat_manager.save_chat(
                    st.session_state.current_chat_name, 
                    messages
                )
            
            st.rerun()
    else:
        render_messages(messages)

if __name__ == "__main__":
    main()

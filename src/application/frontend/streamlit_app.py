import streamlit as st
import httpx
from typing import Dict, Any
import asyncio
from src.configs.configs import money_tracker_config

class ChatUI:
    def __init__(self):
        self.API_URL = "http://localhost:8000/api/v1/chat/"

    def get_headers(self) -> Dict[str, str]:
        return {
            "API_KEY": money_tracker_config.llm_api_key,
            "API_URL": money_tracker_config.llm_api_url,
            "Content-Type": "application/json"
        }

    async def send_message(self, message: str) -> Dict[str, Any]:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.API_URL,
                headers=self.get_headers(),
                json={"message": message}
            )
            return response.json()

    def display_chat(self):
        st.title("Money Tracker AI Chat")

        if "messages" not in st.session_state:
            st.session_state.messages = []

        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        if prompt := st.chat_input("What's on your mind?"):
            with st.chat_message("user"):
                st.markdown(prompt)
            st.session_state.messages.append({"role": "user", "content": prompt})

            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                try:
                    response = asyncio.run(self.send_message(prompt))
                    assistant_response = response["response"]["content"]
                    message_placeholder.markdown(assistant_response)
                    st.session_state.messages.append(
                        {"role": "assistant", "content": assistant_response}
                    )
                except Exception as e:
                    message_placeholder.error(f"Error: {str(e)}")

def main():
    st.set_page_config(page_title="Money Tracker AI", page_icon="💰", layout="centered")
    chat_ui = ChatUI()
    chat_ui.display_chat()

if __name__ == "__main__":
    main()
import streamlit as st
import httpx
from typing import Dict
import asyncio
from src.configs.configs import money_tracker_config, MoneyTrackerConfig

class ChatUI:
    def __init__(self):
        self.API_URL = f"{MoneyTrackerConfig.get_server_host()}/api/v1/chat/"

    def get_headers(self) -> Dict[str, str]:
        return {
            "API_KEY": money_tracker_config.llm_api_key,
            "API_URL": money_tracker_config.llm_api_url,
            "Content-Type": "application/json"
        }

    async def send_message(self, message: str) -> httpx.Response:
        async with httpx.AsyncClient() as client:
            if not message.strip():
                return None
            
            response = await client.post(
                self.API_URL,
                headers=self.get_headers(),
                json={
                    "message": message,
                    "stream": True
                },
                timeout=30.0
            )
            return response

    async def display_chat(self):
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
                full_response = ""
                
                try:
                    response = await self.send_message(prompt)
                    if response is None:
                        return
                        
                    async for line in response.aiter_lines():
                        if line:
                            try:
                                if line.startswith("data: "):
                                    content = line[6:]
                                    full_response += content
                                    message_placeholder.markdown(full_response + "▌")
                                    await asyncio.sleep(0.05)
                            except Exception as e:
                                st.error(f"Error processing response: {e}")
                                break

                    st.session_state.messages.append(
                        {"role": "assistant", "content": full_response}
                    )

                except Exception as e:
                    st.error(f"Error: {str(e)}")

def main():
    st.set_page_config(page_title="Money Tracker AI", page_icon="💰")
    chat_ui = ChatUI()
    asyncio.run(chat_ui.display_chat())

if __name__ == "__main__":
    main()
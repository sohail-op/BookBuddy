import streamlit as st
import requests

st.set_page_config(page_title="BookBuddy Chat", page_icon="📅")
st.title("🤖 BookBuddy — AI Appointment Assistant")

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hi! I can help you book meetings on your calendar. Try saying something like:\n\n👉 Book a slot tomorrow at 3 PM\n\n👉 What's my availability on Friday?"}
    ]

user_input = st.chat_input("Type your message here...")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    try:
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                res = requests.post(
                    "http://localhost:8000/chat",
                    json={"message": user_input},
                    timeout=30,
                )
                reply = res.json()["reply"]
                st.markdown(reply)
                st.session_state.messages.append({"role": "assistant", "content": reply})
    except Exception as e:
        st.error(f"❌ Error: {e}")

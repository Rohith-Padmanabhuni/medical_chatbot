import streamlit as st
import os
from groq import Groq
from dotenv import load_dotenv
from utils import inject_css, handle_enter_pressed

load_dotenv()
groq_api_key = os.getenv("groq_api_key")

st.sidebar.title("Personalization")
prompt = st.sidebar.title("System Prompt:")
model = st.sidebar.selectbox(
    'Choose a model', ['Llama3-8b-8192', 'Llama3-70b-8192', 'Mixtral-8x7b-32768', 'Gemma-7b-It']
)

# Inject CSS from external file
inject_css('styles.css')

# Initialize Groq client
client = Groq(api_key=groq_api_key)

# Interface
st.title("Medical ChatBot")

# Session state for history
if "history" not in st.session_state:
    st.session_state.history = []

user_input = st.text_input("Enter your query:", "")
# truncated_input = user_input[:20]
# Call handle_enter_pressed function to handle Enter key press
handle_enter_pressed(client, user_input, model)

col1, col2 = st.columns([3, 1])
with col1:
    if st.button("Submit", key='submit_button'):
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": user_input,
                }
            ],
            model=model,
        )
        # Store the query and response
        response = chat_completion.choices[0].message.content
        st.session_state.history.append({"query": user_input[:20]+"...", "response": response})
        st.markdown(f'<div class="response-box">{response}</div>', unsafe_allow_html=True)

with col2:
    if st.button("Clear History"):
        st.session_state.history = []

# History Display
st.sidebar.title("History")
for i, entry in enumerate(st.session_state.history):
    if st.sidebar.button(f'{i + 1}.{entry["query"]}'):
        st.markdown(f'<div class="response-box">{entry["response"]}</div>', unsafe_allow_html=True)

import streamlit as st
import os
from groq import Groq
from dotenv import load_dotenv
from utils import inject_css

st.set_page_config(page_title="MedPhi-v1", page_icon="☣")

load_dotenv()
groq_api_key = os.getenv("groq_api_key")

st.sidebar.title("Personalization")
st.sidebar.title("System Prompt:")

model = st.sidebar.selectbox(
    'Choose a model', ['Llama3-8b-8192', 'Llama3-70b-8192', 'Mixtral-8x7b-32768', 'Gemma-7b-It', 'BioMistral-7B']
)

# Inject CSS from external file
inject_css('styles.css')

# Initialize Groq client
client = Groq(api_key=groq_api_key)

# Interface
st.markdown('<div class="fixed-title"><h1>Medical ChatBot</h1></div>', unsafe_allow_html=True)

# Session state for history
if "history" not in st.session_state:
    st.session_state.history = []

if "user_input" not in st.session_state:
    st.session_state.user_input = ""

def handle_submit():
    user_input = st.session_state.user_input
    if user_input:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": user_input,
                }
            ],
            model=model,
        )
        response = chat_completion.choices[0].message.content
        st.session_state.history.append({"query": user_input[:20], "response": response})
        st.markdown(f'<div class="query-box"><p>{user_input}</p></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="response-box">Response:<br>{response}</div>', unsafe_allow_html=True)
        st.session_state.user_input = ""

# JavaScript to handle Enter key press and add custom id/class
enter_script = """
<script>
document.addEventListener('DOMContentLoaded', function() {
    const input = document.querySelectorAll('input[type="text"]');
    input.forEach(function(element) {
        element.setAttribute('id', 'user-input-field');
        element.classList.add('custom-input-class');
    });

    const textArea = document.querySelectorAll('textarea');
    textArea.forEach(function(element) {
        element.addEventListener('keydown', function(event) {
            if (event.key === 'Enter') {
                event.preventDefault(); // Prevents the default action (e.g., form submission)
                const submitButton = document.querySelector('.stButton button');
                submitButton.click(); // Simulate click on the submit button
            }
        });
    });
});
</script>
"""
st.markdown(enter_script, unsafe_allow_html=True)

# Function to clear chat history
def clear_history():
    st.session_state.history = []



# Layout for input and button
col1, col2 = st.columns([3, 1])
with col1:
    user_input = st.text_input("Enter your query:", placeholder="Message", key="user_input", on_change=handle_submit)
    

with col2:
    st.button("➤", key="send-btn", on_click=handle_submit)

# History Display
st.sidebar.title("History")
if st.sidebar.button("Clear History"):
    st.session_state.history = []
for i, entry in enumerate(st.session_state.history):
    if st.sidebar.button(f'{i+1}.{entry["query"][:50]}...', key=f'history_{i}'):
        st.markdown(f'<div class="response-box">{entry["response"]}</div>', unsafe_allow_html=True)

import streamlit as st
import os
from groq import Groq
from dotenv import load_dotenv

st.set_page_config(page_title="MedPhi-v1", page_icon="☣")

load_dotenv()
groq_api_key = os.getenv("groq_api_key")

st.sidebar.title("Personalization")
st.sidebar.title("System Prompt:")

model = st.sidebar.selectbox(
    'Choose a model', ['Llama3-8b-8192', 'Llama3-70b-8192', 'Mixtral-8x7b-32768', 'Gemma-7b-It', 'BioMistral-7B']
)

# Function to inject CSS
def inject_css(css_file):
    with open(css_file) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Inject CSS from external file
inject_css('styles.css')

# Initialize Groq client
client = Groq(api_key=groq_api_key)

# Interface
st.markdown('<div class="fixed-title"><h1>Medical ChatBot</h1></div>', unsafe_allow_html=True)

# Session state for history
if "history" not in st.session_state:
    st.session_state.history = []

if "selected_history" not in st.session_state:
    st.session_state.selected_history = None

def handle_submit(user_input):
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
        st.session_state.history.append({"query": user_input, "response": response})

# Function to clear chat history
def clear_history():
    st.session_state.history = []
    st.session_state.selected_history = None

# Use st.chat_input for user input
user_input = st.chat_input("Say something:")
if user_input:
    handle_submit(user_input)

# History Display
st.sidebar.title("History")
if st.sidebar.button("Clear History", key="clear"):
    clear_history()

for i, entry in enumerate(st.session_state.history):
    if st.sidebar.button(f'{i+1}. {entry["query"]}', key=f'history_{i}'):
        st.session_state.selected_history = entry

# Display the selected history entry
if st.session_state.selected_history:
    entry = st.session_state.selected_history
    st.markdown(f'<div class="query-box1"><p>{entry["query"]}</p></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="response-box">Response:<br>{entry["response"]}</div>', unsafe_allow_html=True)

# Display the full chat history
for entry in st.session_state.history:
    st.markdown(f'<div class="query-box"><p>{entry["query"]}</p></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="response-box">Response:<br>{entry["response"]}</div>', unsafe_allow_html=True)

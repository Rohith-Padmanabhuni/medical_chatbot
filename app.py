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
    'Choose a model', ['Llama3-8b-8192', 'Llama3-70b-8192', 'Mixtral-8x7b-32768', 'Gemma-7b-It']
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

# Session state for sessions and editing
if "sessions" not in st.session_state:
    st.session_state.sessions = [[]]  # Start with one empty session

if "current_session_index" not in st.session_state:
    st.session_state.current_session_index = 0  # Start with the first session

if "editing_query_index" not in st.session_state:
    st.session_state.editing_query_index = None  # Initialize editing mode

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
        if st.session_state.editing_query_index is not None:
            # Update existing query
            st.session_state.sessions[st.session_state.current_session_index][st.session_state.editing_query_index]["query"] = user_input
            st.session_state.sessions[st.session_state.current_session_index][st.session_state.editing_query_index]["response"] = response
            st.session_state.editing_query_index = None  # Reset edit mode
        else:
            # Add new query
            st.session_state.sessions[st.session_state.current_session_index].append({"query": user_input, "response": response})


# Function to create a new session
def create_new_session():
    st.session_state.sessions.append([])
    st.session_state.current_session_index = len(st.session_state.sessions) - 1

# Function to switch to a session
def switch_session(index):
    st.session_state.current_session_index = index

# Sidebar buttons for creating new sessions and displaying existing sessions
st.sidebar.title("Sessions")
if st.sidebar.button("Create New Session"):
    create_new_session()

for i, session in enumerate(st.session_state.sessions):
    if st.sidebar.button(f'Session {i+1}', key=f'session_{i}'):
        switch_session(i)

# Use st.chat_input for user input
user_input = st.chat_input("Say something:")
if user_input:
    handle_submit(user_input)


# Display the chat history in a div with an id
st.markdown('<div id="chat-history" style="max-height: 70vh; overflow-y: auto;">', unsafe_allow_html=True)
current_session = st.session_state.sessions[st.session_state.current_session_index]        
for i, entry in enumerate(current_session):
    st.markdown(f'<div class="query-box" id="query_{i}"><p> {entry["query"]}</p></div>', unsafe_allow_html=True)
    # Add edit button for each query
    if st.button(f'🖋', key=f'edit_button_{i}'):  
        st.session_state.editing_query_index = i  # Set edit mode
    st.markdown(f'<div class="response-box">Response:<br>{entry["response"]}</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

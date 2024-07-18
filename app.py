import streamlit as st
import os
import logging
from dotenv import load_dotenv
from transformers import pipeline

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

st.set_page_config(page_title="MedPhi-v1", page_icon="☣")

st.title("Medical ChatBot")

load_dotenv()

# Groq API key
groq_api_key = os.getenv("groq_api_key")

# Hugging Face API keys
huggingface_api_keys = {
    "Key 1": os.getenv("huggingface_api_key_1"),
    "Key 2": os.getenv("huggingface_api_key_2"),
    "Key 3": os.getenv("huggingface_api_key_3"),
}

# Function to inject CSS
def inject_css(css_file):
    with open(css_file) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Inject CSS from external file
inject_css('styles.css')

# Sidebar options for API and model selection
st.sidebar.title("Medical ChatBot")

api_provider = st.sidebar.selectbox('Choose API Provider', ['Groq', 'Hugging Face'])

if api_provider == 'Groq':
    from groq import Groq
    groq_api_key = os.getenv("groq_api_key")
    model = st.sidebar.selectbox(
        'Choose a model', ['Llama3-8b-8192', 'Llama3-70b-8192', 'Mixtral-8x7b-32768', 'Gemma-7b-It']
    )
    client = Groq(api_key=groq_api_key)
else:
    huggingface_api_key = st.sidebar.selectbox(
        'Choose an API Key', list(huggingface_api_keys.keys())
    )
    model = st.sidebar.selectbox(
        'Choose a model', ['facebook/bart-large', 'microsoft/DialoGPT-medium', 'gpt2']
    )
    
    @st.cache_resource
    def load_model(model_name):
        logger.info(f"Loading Hugging Face model: {model_name}")
        return pipeline('text-generation', model=model_name)
    
    generator = load_model(model)

# Session state for sessions and editing
if "sessions" not in st.session_state:
    st.session_state.sessions = [{"first_query": None, "history": []}]  # Start with one empty session

if "current_session_index" not in st.session_state:
    st.session_state.current_session_index = 0  # Start with the first session

if "editing_query_index" not in st.session_state:
    st.session_state.editing_query_index = None  # Initialize editing mode

def handle_submit(user_input, is_edit=False):
    if user_input:
        current_session = st.session_state.sessions[st.session_state.current_session_index]

        if api_provider == 'Groq':
            # Generate the response using Groq
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
        else:
            # Generate the response using Hugging Face
            response = generator(user_input, max_length=100, num_return_sequences=1)[0]['generated_text']

        if is_edit:
            # Update existing query and response
            current_session["history"][st.session_state.editing_query_index]["query"] = user_input
            current_session["history"][st.session_state.editing_query_index]["response"] = response
            st.session_state.editing_query_index = None  # Reset edit mode
        else:
            # Add new query and response
            current_session["history"].append({"query": user_input, "response": response})
            
            # Set the first query and rerun to update the session title
            if current_session["first_query"] is None:
                current_session["first_query"] = user_input
                st.rerun()

# Function to create a new session
def create_new_session():
    st.session_state.sessions.append({"first_query": None, "history": []})
    st.session_state.current_session_index = len(st.session_state.sessions) - 1

# Function to switch to a session
def switch_session(index):
    st.session_state.current_session_index = index

# Sidebar buttons for creating new sessions and displaying existing sessions
st.sidebar.title("Sessions")
if st.sidebar.button("Create New Session"):
    create_new_session()

for i, session in enumerate(st.session_state.sessions):
    session_title = session["first_query"] if session["first_query"] else f"Session {i + 1}"
    if st.sidebar.button(session_title, key=f'session_{i}'):
        switch_session(i)

# Handle query input and edit mode
if st.session_state.editing_query_index is not None:
    editing_index = st.session_state.editing_query_index
    edited_query = st.text_input("Edit your query:", value=st.session_state.sessions[st.session_state.current_session_index]["history"][editing_index]["query"], key=f'edit_query_{editing_index}')
    if st.button("Submit Edit", key=f'submit_edit_{editing_index}'):
        handle_submit(edited_query, is_edit=True)
        st.rerun()  # Rerun to update the view and exit edit mode
else:
    user_input = st.chat_input("Say something:")
    if user_input:
        handle_submit(user_input)

# Display the chat history
current_session = st.session_state.sessions[st.session_state.current_session_index]["history"]

# Display chat history with edit options
st.markdown('<div id="chat-history" style="max-height: 70vh; overflow-y: auto;">', unsafe_allow_html=True)
for i, entry in enumerate(current_session):
    if i == st.session_state.editing_query_index:
        continue  # Skip displaying the entry currently being edited
    
    # Display query and response
    col1, col2 = st.columns([9, 1])
    with col2:
        st.markdown(f'<div class="query-box">{entry["query"]}</div>', unsafe_allow_html=True)
    with col1:
        if st.button("🖋", key=f'edit_{i}'):
            st.session_state.editing_query_index = i
            st.experimental_rerun()  # Trigger rerun to show the edit input

    st.markdown(f'<div class="response-box">Response:<br>{entry["response"]}</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

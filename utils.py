import streamlit as st

def inject_css(filename):
    """
    Inject CSS from an external file into Streamlit app.
    """
    with open(filename, 'r') as file:
        css = file.read()
    st.markdown(f'<style>{css}</style>', unsafe_allow_html=True)

def handle_enter_pressed(client, user_input, model):
    """
    Handle Enter key press to submit user query.
    """
    if user_input:
        # JavaScript to handle Enter key press and submit form
        st.markdown(
            f"""
            <script>
            document.addEventListener('keydown', function(event) {{
                if (event.code === 'Enter') {{
                    document.getElementById('submit_button').click();
                }}
            }});
            </script>
            """,
            unsafe_allow_html=True
        )
def inject_css(css_file):
    with open(css_file) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
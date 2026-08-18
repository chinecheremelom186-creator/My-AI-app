import streamlit as st
from google import genai
from google.genai.errors import APIError

st.title("My AI Assistant")

# Checks Streamlit Secrets first; falls back to input box if not set
api_key = st.secrets.get("GEMINI_API_KEY") or st.text_input("Enter Gemini API Key", type="password")
user_prompt = st.text_area("Ask your AI anything:")

if st.button("Generate Response"):
    if not api_key:
        st.warning("Please provide an API key in Streamlit Secrets or the text field.")
    elif not user_prompt:
        st.warning("Please enter a prompt.")
    else:
        try:
            client = genai.Client(api_key=api_key)
            
            # Stream the response live line-by-line for fast rendering
            response = client.models.generate_content_stream(
                model="gemini-3.6-flash",
                contents=user_prompt,
            )
            
            st.subheader("Response:")
            st.write_stream(chunk.text for chunk in response if chunk.text)
            
        except APIError:
            st.error("The Gemini service is experiencing high traffic right now. Please wait a moment and try again!")
        except Exception as e:
            st.error(f"An error occurred: {e}")

import streamlit as st
from google import genai
from google.genai.errors import APIError

st.title("My AI Assistant")

api_key = st.text_input("Enter Gemini API Key", type="password")
user_prompt = st.text_area("Ask your AI anything:")

if st.button("Generate Response"):
    if not api_key or not user_prompt:
        st.warning("Please enter your API key and a prompt.")
    else:
        try:
            client = genai.Client(api_key=api_key)
            response = client.models.generate_content(
                model="gemini-3.6-flash",
                contents=user_prompt,
            )
            st.subheader("Response:")
            st.write(response.text)
        except APIError:
            st.error("The Gemini service is experiencing high traffic right now. Please wait a moment and try again!")
        except Exception as e:
            st.error(f"An error occurred: {e}")

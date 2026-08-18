import streamlit as st
from google import genai

st.title("My AI Assistant")

api_key = st.text_input("Enter Gemini API Key", type="password")
user_prompt = st.text_area("Ask your AI anything:")

if st.button("Generate Response"):
    if not api_key or not user_prompt:
        st.warning("Please enter your API key and a prompt.")
    else:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=user_prompt,
        )
        st.subheader("Response:")
        st.write(response.text)

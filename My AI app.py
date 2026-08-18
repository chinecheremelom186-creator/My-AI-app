import streamlit as st
from google import genai
from google.genai.errors import APIError

# ==========================================
# 1. PAGE CONFIGURATION & BRANDING
# ==========================================
st.set_page_config(
    page_title="My Custom AI Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🤖 My Custom AI Assistant")
st.caption("Designed, Developed, and Deployed by **Developer**")
st.write("---")

# ==========================================
# 2. SECRET KEY CHECK & INITIALIZATION
# ==========================================
api_key = st.secrets.get("GEMINI_API_KEY") or st.sidebar.text_input("Gemini API Key", type="password")

if not api_key:
    st.error("⚠️ Error: GEMINI_API_KEY not found. Please enter it in the sidebar or add it to Streamlit Secrets.")
    st.stop()

try:
    client = genai.Client(api_key=api_key)
except Exception as e:
    st.error(f"Failed to initialize Gemini Client: {e}")
    st.stop()

if "messages" not in st.session_state:
    st.session_state.messages = []
if "generated_images" not in st.session_state:
    st.session_state.generated_images = []

# ==========================================
# 3. SIDEBAR / CONTROLS
# ==========================================
with st.sidebar:
    st.header("App Controls")
    
    app_mode = st.radio(
        "Choose Generation Mode:",
        ("Text Chat", "Advanced Image (Imagen 3)", "View Chat History"),
        index=0
    )
    
    st.write("---")
    if st.button("🗑️ Clear Current History"):
        st.session_state.messages = []
        st.session_state.generated_images = []
        st.success("History cleared!")
        st.rerun()

# ==========================================
# 4. MAIN APPLICATION LOGIC
# ==========================================

# --- MODE 1: TEXT CHAT (With Memory) ---
if app_mode == "Text Chat":
    st.subheader("1. Text Conversation")

    # Display Chat History from Session State
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Text Input Only
    user_prompt = st.chat_input("Type your message here...")

    if user_prompt:
        st.session_state.messages.append({"role": "user", "content": user_prompt})
        with st.chat_message("user"):
            st.markdown(user_prompt)

        with st.chat_message("assistant"):
            try:
                response_container = st.empty()
                full_response = ""

                # Build full history payload so the model remembers past turns
                formatted_contents = []
                for m in st.session_state.messages:
                    role = "user" if m["role"] == "user" else "model"
                    formatted_contents.append({
                        "role": role,
                        "parts": [{"text": m["content"]}]
                    })

                response_stream = client.models.generate_content_stream(
                    model="gemini-3.6-flash",
                    contents=formatted_contents,
                )

                for chunk in response_stream:
                    if chunk.text:
                        full_response += chunk.text
                        response_container.markdown(full_response)
                
                st.session_state.messages.append({"role": "assistant", "content": full_response})
                
            except APIError as e:
                st.error(f"Gemini API Error: {e.message if hasattr(e, 'message') else e}")
            except Exception as e:
                st.error(f"Error: {e}")

# --- MODE 2: ADVANCED IMAGE GENERATION (IMAGEN 3) ---
elif app_mode == "Advanced Image (Imagen 3)":
    st.subheader("2. High-Graphic Image Generation")
    st.info("Powered by Google Imagen 3. Fill in the form and tap Generate.")

    with st.form("image_form"):
        img_prompt = st.text_area("Describe the image you want to create:", height=100)
        aspect_ratio_choice = st.selectbox("Aspect Ratio:", ["1:1", "16:9", "9:16"], index=0)
        submit_btn = st.form_submit_button("🎨 Generate Image")

    if submit_btn:
        if not img_prompt.strip():
            st.warning("Please type a description before generating.")
        else:
            with st.spinner("Generating high-quality image..."):
                try:
                    # Using the correct plural 'generate_images' method
                    result = client.models.generate_images(
                        model="imagen-3.0-generate-001",
                        prompt=img_prompt,
                        config=dict(
                            aspect_ratio=aspect_ratio_choice,
                            number_of_images=1,
                        )
                    )
                    
                    generated_img = result.generated_images[0]
                    img_bytes = generated_img.image.image_bytes
                    
                    st.image(img_bytes, caption=f"Generated: {img_prompt}", use_container_width=True)
                    
                    st.session_state.generated_images.append({
                        "prompt": img_prompt,
                        "data": img_bytes,
                    })
                    st.success("Image generated successfully!")
                    
                except APIError as e:
                    st.error(f"Imagen Error: {e}")
                except Exception as e:
                    st.error(f"Error: {e}")

# --- MODE 3: VIEW CHAT HISTORY ---
elif app_mode == "View Chat History":
    st.subheader("3. Session History & Archives")
    
    st.write("---")
    st.write("#### Conversation History")
    if st.session_state.messages:
        for message in st.session_state.messages:
            role_label = "**You:**" if message["role"] == "user" else "**Assistant:**"
            st.markdown(f"{role_label} {message['content']}")
    else:
        st.write("No conversation history yet.")

    st.write("---")
    st.write("#### Generated Image Gallery")
    if st.session_state.generated_images:
        cols = st.columns(3)
        for i, img in enumerate(st.session_state.generated_images):
            with cols[i % 3]:
                st.image(img["data"], caption=f"'{img['prompt'][:40]}...'", use_container_width=True)
                st.download_button(
                    label=f"Download Image #{i+1}",
                    data=img["data"],
                    file_name=f"generated_ai_image_{i+1}.png",
                    mime="image/png",
                    key=f"dl_{i}"
                )
    else:
        st.write("No images generated yet.")

# ==========================================
# 5. FOOTER & BRANDING
# ==========================================
st.write("---")
st.markdown(
    """
    <div style='text-align: center;'>
        Created with Streamlit & Gemini API
    </div>
    """,
    unsafe_allow_html=True
)

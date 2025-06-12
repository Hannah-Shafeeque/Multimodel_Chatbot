import streamlit as st
from PIL import Image
import google.generativeai as genai
import hashlib
import base64

def set_bg(image_file):
    with open(image_file, "rb") as img:
        encoded = base64.b64encode(img.read()).decode()
    css = f"""
    <style>
    .stApp {{
        background-image: url("data:image/png;base64,{encoded}");
        background-size: cover;
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)



# --- Sign In Page ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False


def login():
    set_bg("qq - Copy.PNG")
    st.title("🔐 Sign In")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        # Simple hardcoded login (you can expand this later)
        if username == "admin" and password == "1234":
            st.session_state.authenticated = True
            st.success("Logged in successfully!")
            st.rerun()
        else:
            st.error("Invalid username or password")

if not st.session_state.authenticated:
    col1, col2 = st.columns([1, 1])
    with col2:

        login()
        st.stop()  # Stop rendering the rest of the app unless logged in

genai.configure(api_key="AIzaSyC_XrUioseHZQofU0H8bVtPmo7Ttv0aWA4")


if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "stop_chat" not in st.session_state:
    st.session_state.stop_chat = False

if "latest_image" not in st.session_state:
    st.session_state.latest_image = None

if "uploaded_hashes" not in st.session_state:
    st.session_state.uploaded_hashes = set()


text_model = genai.GenerativeModel("gemini-1.5-flash")
vision_model = genai.GenerativeModel("gemini-1.5-flash")

st.title("🤖 ChatBot")
st.info("I am here to help! Type exit to end the conversation.")


for entry in st.session_state.chat_history:
    if entry["type"] == "text":
        emoji = "👤" if entry["sender"] == "YOU" else "🤖"
        st.markdown(f"{emoji} **{entry['sender']}**: {entry['content']}")
    elif entry["type"] == "image":
        st.image(entry["image"], caption="🖼️ Uploaded Image", use_container_width=True)


col1, col2 = st.columns([1, 1])
with col1:
    st.subheader("📷 Upload an image")
    uploaded_file = st.file_uploader("Choose an image", type=["jpg", "jpeg", "png"])

def get_file_hash(file):
    return hashlib.md5(file.getvalue()).hexdigest()

if uploaded_file:
    image_hash = get_file_hash(uploaded_file)

    if image_hash not in st.session_state.uploaded_hashes:
        image = Image.open(uploaded_file)
        st.session_state.chat_history.append({
            "type": "image",
            "image": image
        })
        st.session_state.latest_image = image
        st.session_state.uploaded_hashes.add(image_hash)
        st.rerun()
    else:
        st.session_state.latest_image = Image.open(uploaded_file)


if not st.session_state.stop_chat:
    with col2:
        st.subheader("💬 Ask something")
        user_input = st.text_input("Your message", key=len(st.session_state.chat_history))

    if user_input:
        if user_input.lower().strip() == "exit":
            st.session_state.stop_chat = True
            st.success("Chat ended. Refresh to restart.")
        else:
            st.session_state.chat_history.append({
                "type": "text",
                "sender": "YOU",
                "content": user_input
            })

            if st.session_state.latest_image:
                response = vision_model.generate_content([
                    st.session_state.latest_image,
                    user_input
                ])
            else:
                response = text_model.generate_content(user_input)

            st.session_state.chat_history.append({
                "type": "text",
                "sender": "BOT",
                "content": response.text
            })

            st.rerun()

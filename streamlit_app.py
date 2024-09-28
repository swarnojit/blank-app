from dotenv import load_dotenv
load_dotenv()  # Load all the environment variables from .env

import streamlit as st
import os
from PIL import Image
import google.generativeai as genai
import time

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Load Gemini pro vision model
model = genai.GenerativeModel('gemini-1.5-flash')

def get_gemini_response(input, image, user_prompt):
    response = model.generate_content([input, image[0], user_prompt])
    return response.text

def input_image_details(uploaded_file):
    if uploaded_file is not None:
        # Read the file into bytes
        bytes_data = uploaded_file.getvalue()
        image_parts = [
            {
                "mime_type": uploaded_file.type,  # Get the mime type of the uploaded file
                "data": bytes_data
            }
        ]
        return image_parts
    else:
        raise FileNotFoundError("No file uploaded")

# Initialize our Streamlit app
st.set_page_config(page_title="GENTECH Chatbot")

st.header("Conversational AI Image Chatbot")

# Move the file uploader to the sidebar
uploaded_file = st.sidebar.file_uploader("Choose an image ...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.sidebar.image(image, caption="Uploaded Image.", use_column_width=True)

# Initialize session state for chat history if not already present
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'last_response' not in st.session_state:
    st.session_state.last_response = None
if 'last_question' not in st.session_state:
    st.session_state.last_question = None
if 'last_interaction_time' not in st.session_state:
    st.session_state.last_interaction_time = time.time()

# Check for session timeout (2 minutes)
if time.time() - st.session_state.last_interaction_time > 120:
    st.session_state.chat_history = []
    st.session_state.last_response = None
    st.session_state.last_question = None

# Define the input prompt for the AI
input_prompt = """
You are a conversational AI image chatbot. Your task is to analyze images provided by the user and answer any questions related to those images. You can remember the context of the conversation and use it to provide accurate and relevant responses. Here are your instructions:

Image Analysis: When an image is provided, analyze it to understand its content, objects, and any relevant details.
Answering Questions: Respond to questions related to the image with accurate and detailed information.
Contextual Memory: Remember the context of the conversation, including previous images and questions, to provide coherent and contextually relevant answers.
User Interaction: Engage with the user in a friendly and helpful manner, ensuring that your responses are clear and informative.
"""

# Define input text at the bottom
input_text = st.text_input("Input Prompt: ", key="input")
submit = st.button("Ask Question")

# If submit button is clicked
if submit and uploaded_file is not None:
    st.session_state.last_interaction_time = time.time()  # Update last interaction time
    image_data = input_image_details(uploaded_file)
    response = get_gemini_response(input_prompt, image_data, input_text)

    # Store the interaction temporarily
    st.session_state.last_response = response
    st.session_state.last_question = input_text

# Display the last question and response
if st.session_state.last_question and st.session_state.last_response:
    st.subheader("Last Question and Response:")
    st.write(f"**USER:** {st.session_state.last_question}")
    st.write(f"**JARVIS:** {st.session_state.last_response}")

# Only add to chat history if a new question is asked
if submit and uploaded_file is not None:
    st.session_state.chat_history.append({"user": st.session_state.last_question, "ai": st.session_state.last_response})

# Display chat history
st.subheader("Chat History")
for interaction in st.session_state.chat_history:
    st.write(f"**USER:** {interaction['user']}")
    st.write(f"**JARVIS:** {interaction['ai']}")

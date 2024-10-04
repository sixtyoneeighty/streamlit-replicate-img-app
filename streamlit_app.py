import os
from together import Together
import streamlit as st
import google.generativeai as genai
from streamlit_image_select import image_select

# Configure Gemini API with Streamlit secrets
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

# Configure Together API
client = Together(api_key=os.environ.get('TOGETHER_API_KEY'))

# Configure page layout
st.set_page_config(page_title="sixtyoneeighty Image AI", layout="wide")

# Custom CSS for additional styling, including background image
st.markdown(
    """
    <style>
    /* Set background image */
    body {
        background-image: url('gallery/background.png');
        background-size: cover;
        background-repeat: no-repeat;
        background-attachment: fixed;
        background-position: center;
    }

    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background-color: rgba(26, 26, 26, 0.85) !important;
    }

    /* Add box shadows for sidebar */
    section[data-testid="stSidebar"] {
        box-shadow: 5px 5px 15px rgba(0, 0, 0, 0.2);
    }

    /* Import the Epilogue font from Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Epilogue:wght@100;200;300;400;500;600;700;800;900&display=swap');

    /* Apply Epilogue font globally */
    body, h1, h2, h3, h4, h5, h6, p, div {
        font-family: 'Epilogue', sans-serif !important;
        color: #E8E8E8 !important;
    }

    /* Customize buttons */
    .button-container {
        display: flex;
        justify-content: space-between;
        gap: 10px;
        margin-top: 10px;
    }

    .stButton button {
        background-color: #7F38F2 !important;
        color: white !important;
        border-radius: 8px !important;
        padding: 0.5em 1.5em !important;
        flex: 1;
    }

    .stButton button:hover {
        background-color: #A64CF6 !important; /* Lighter purple on hover */
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown("# sixtyoneeighty")

# Hardcoded TOGETHER model
TOGETHER_MODEL_ENDPOINT = "black-forest-labs/flux-pro"
# Access TOGETHER API token from
TOGETHER_API_TOKEN = st.secrets["TOGETHER_API_TOKEN"]

# Placeholders for images and gallery
generated_images_placeholder = st.empty()
gallery_placeholder = st.empty()

# Global state to manage prompt text
if "prompt" not in st.session_state:
    st.session_state["prompt"] = ""

def magic_prompt(topic: str) -> list:
    """Generate the system and user message based on the topic."""
    
    system_message = {
        "role": "system",
        "content": "You are an expert AI assistant, specializing in photography and prompt enhancement..."
    }

    user_message = {
        "role": "user",
        "content": f"""Please create a creative and detailed image generation prompt based on the following information:

Topic: {topic}

Your prompt should include the following elements if applicable:
1. Main subject or character description
2. Background and setting details
3. Lighting, color scheme, and atmosphere
4. Specific actions or poses for characters
5. Important objects or elements to include
6. Overall mood or emotion to convey
7. Type of camera and lens used, if relevant"""
    }

    return [system_message, user_message]

def get_enhanced_prompt(topic: str) -> str:
    """Use Gemini API to enhance the user's prompt."""
    prompt_text = f"""Please create a creative and detailed image generation prompt based on the following information:

Topic: {topic}

Your prompt should include the following elements if applicable:
1. Subject: The main focus of the image.
2. Style: The artistic approach or visual aesthetic.
3. Composition: How elements are arranged within the frame.
4. Lighting: The type and quality of light in the scene.
5. Mood/Atmosphere: The emotional tone or ambiance of the image.
6. Technical Details: Camera settings, perspective, or specific visual techniques.
7. Additional Elements: Background, poses, actions, other objects in the photo."""
    
    model = genai.GenerativeModel(
        model_name="gemini-1.5-pro-latest",
        generation_config={
            "temperature": 1.3,
            "top_p": 0.95,
            "top_k": 64,
            "max_output_tokens": 8192,
        }
    )
    chat_session = model.start_chat(history=[])
    response = chat_session.send_message(prompt_text)
    return response.text

def configure_sidebar():
    with st.sidebar:
        with st.form("my_form"):
            # Logo
            st.image("gallery/logo.png", use_column_width=True)

            # Input prompt
            prompt = st.text_area("Prompt:", value=st.session_state.get("prompt", ""),
                                  placeholder="Enter your idea here. Our AI will enhance, optimize, and generate your image.")

            # Checkbox to skip prompt enhancement
            skip_enhancement = st.checkbox("Skip Prompt Enhancement", value=False)

            # Advanced settings
            with st.expander("**Advanced Settings**"):
                image_size = st.selectbox("Image Size", ["square_hd", "square", "portrait_4_3", "portrait_16_9", "landscape_4_3", "landscape_16_9"], index=4)
                seed = st.number_input("Seed (optional)", value=0, min_value=0, step=1)
                sync_mode = st.checkbox("Sync Mode", value=True)
                num_images = st.slider("Number of images to generate", value=1, min_value=1, max_value=10)
                enable_safety_checker = st.checkbox("Enable Safety Checker", value=False)
                safety_tolerance = st.selectbox("Safety Tolerance", ["1", "2", "3", "4", "5", "6"], index=1)

            submitted = st.form_submit_button("Generate Image")

    return (submitted, prompt, image_size, seed, sync_mode, num_images, enable_safety_checker, safety_tolerance, skip_enhancement)

def generate_image(prompt: str, image_size: str, num_images: int, enable_safety_checker: bool, safety_tolerance: str, seed: int = None, sync_mode: bool = True):
    response = client.images.generate(
        prompt=prompt,
        model=TOGETHER_MODEL_ENDPOINT,
        image_size=image_size,
        num_images=num_images,
        enable_safety_checker=enable_safety_checker,
        safety_tolerance=safety_tolerance,
        seed=seed if seed != 0 else None,
        sync_mode=sync_mode
    )
    return response.data[0].b64_json

def main():
    submitted, prompt, image_size, seed, sync_mode, num_images, enable_safety_checker, safety_tolerance, skip_enhancement = configure_sidebar()

    if submitted:
        if not skip_enhancement:
            prompt = get_enhanced_prompt(prompt)
        
        image_data = generate_image(
            prompt=prompt,
            image_size=image_size,
            num_images=num_images,
            enable_safety_checker=enable_safety_checker,
            safety_tolerance=safety_tolerance,
            seed=seed,
            sync_mode=sync_mode
        )

        # Access the image_data to display or process it
        st.image(image_data, caption="Generated Image")
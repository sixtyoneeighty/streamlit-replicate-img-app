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
                enable_safety_checker = st.checkbox("Enable Safety Checker", value=True)
                safety_tolerance = st.selectbox("Safety Tolerance", ["1", "2", "3", "4", "5", "6"], index=1)

            submitted = st.form_submit_button("Generate Image")

    return (submitted, prompt, image_size, seed, sync_mode, num_images, enable_safety_checker, safety_tolerance, skip_enhancement)

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
            seed=seed if seed != 0 else None,
            sync_mode=sync_mode
        )
        
        st.image(image_data, caption="Generated Image", use_column_width=True)

if __name__ == "__main__":
    main()
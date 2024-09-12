import replicate
import streamlit as st
import requests
import zipfile
import io
import os
from streamlit_image_select import image_select

# Set up page layout
st.set_page_config(page_title="sixtyoneeighty Image AI", layout="wide")

# Custom CSS for sidebar and gallery styling (minimal for now)
st.markdown(
    """
    <style>
    /* Set background color */
    body {
        background-color: #0D0D0D !important;
    }

    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background-color: #1A1A1A !important;
        padding: 10px;
    }

    /* Import the Epilogue font from Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Epilogue:wght@100;200;300;400;500;600;700;800;900&display=swap');

    /* Apply Epilogue font globally */
    body, h1, h2, h3, h4, h5, h6, p, div {
        font-family: 'Epilogue', sans-serif !important;
        color: #E8E8E8 !important;
    }

    /* Minimal styling for now */
    img {
        width: 100%;
        height: auto;
        border-radius: 10px;
    }
    </style>
    """, unsafe_allow_html=True
)

# Sidebar with form
def configure_sidebar() -> None:
    with st.sidebar:
        with st.form("my_form"):
            st.image("static/logo.png", use_column_width=True)

            # Prompt input field
            prompt = st.text_area("Prompt:", value="Your idea goes here. Our AI will then enhance, optimize, and generate your image.")

            # Advanced Settings in the sidebar
            with st.expander("Advanced Settings"):
                width = st.number_input("Width of output image", value=1024)
                height = st.number_input("Height of output image", value=1024)
                num_outputs = st.slider("Number of images to output", value=1, min_value=1, max_value=2)
                guidance_scale = st.slider("Guidance scale (0 to 10)", value=3.5, min_value=0.0, max_value=10.0, step=0.1)
                num_inference_steps = st.slider("Number of denoising steps", value=28, min_value=1, max_value=50)
                aspect_ratio = st.selectbox('Aspect Ratio', ('1:1', '5:4', '16:9'))
                output_format = st.selectbox('Output format', ('webp', 'jpg', 'png'))
                output_quality = st.slider('Output quality (0-100, for jpg/webp)', value=80, min_value=0, max_value=100)
                disable_safety_checker = st.checkbox("Disable safety checker", value=True)

            submitted = st.form_submit_button("Generate", type="primary", use_container_width=True)

        st.divider()
        st.markdown(":orange[**Resources:**]  \nReplicate AI")

        return submitted, width, height, num_outputs, guidance_scale, num_inference_steps, aspect_ratio, output_format, output_quality, disable_safety_checker, prompt


# Display images using st.image() directly to ensure they load
st.image("static/futurecity.webp", caption="A futuristic city skyline at sunset, with flying cars and glowing holograms, ultra-realistic")
st.image("static/robot.webp", caption="A robot bartender serving drinks to human and alien patrons in a sleek space station lounge, realistic.")
st.image("static/fest.webp", caption="A group of friends laughing and dancing at a music festival, joyful atmosphere, 35mm film photography")
st.image("static/wizard.png", caption="A wizard casting a spell, intense magical energy glowing from his hands")
st.image("static/skateboard.webp", caption="A woman street skateboarding in Paris Olympics 2024")
st.image("static/anime.jpg", caption="Anime style portrait of a female samurai at a beautiful lake with cherry trees, mountain fuji background, spring, sunset")
st.image("static/viking.png", caption="A photorealistic close-up portrait of a bearded viking warrior in a horned helmet. He stares intensely into the distance while holding a battle axe. Dramatic mood lighting.")

def main():
    submitted, width, height, num_outputs, guidance_scale, num_inference_steps, aspect_ratio, output_format, output_quality, disable_safety_checker, prompt = configure_sidebar()
    # Call the main image generation logic here (omitted for brevity)


if __name__ == "__main__":
    main()
import replicate
import streamlit as st
import requests
import zipfile
import io
from utils import icon
from streamlit_image_select import image_select

# Apply page layout settings from config.toml (no need to set page_icon here)
st.set_page_config(page_title="sixtyoneeighty Image AI", layout="wide")

# Custom CSS for additional styling
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
    }

    /* Add box shadows for sidebar */
    section[data-testid="stSidebar"] {
        box-shadow: 5px 5px 15px rgba(0, 0, 0, 0.2);
    }

    /* Custom font */
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;700&display=swap');
    
    body, h1, h2, h3, h4, h5, h6, p, div {
        font-family: 'Poppins', sans-serif !important;
        color: #E8E8E8 !important;
    }

    /* Customize buttons */
    .stButton button {
        background-color: #7F38F2 !important;
        color: white !important;
        border-radius: 8px !important;
        padding: 0.5em 1.5em !important;
    }
    
    .stButton button:hover {
        background-color: #A64CF6 !important; /* Lighter purple on hover */
    }

    /* Add gradient text */
    h1 {
        background: linear-gradient(90deg, #ff7e5f, #feb47b);  /* Gradient from peach to orange */
        -webkit-background-clip: text;
        color: transparent;
    }
    </style>
    """, unsafe_allow_html=True
)

icon.show_icon(":foggy:")
st.markdown("# sixtyoneeighty Image AI")

# API Tokens and endpoints from `.streamlit/secrets.toml` file
REPLICATE_API_TOKEN = st.secrets["REPLICATE_API_TOKEN"]
REPLICATE_MODEL_ENDPOINT = "black-forest-labs/flux-dev"  # Updated to Flux-Dev model

# Placeholders for images and gallery
generated_images_placeholder = st.empty()
gallery_placeholder = st.empty()

def configure_sidebar() -> None:
    with st.sidebar:
        with st.form("my_form"):
            # Display logo.png instead of text
            st.image("gallery/logo.png", use_column_width=True)

            # First, the prompt field
            prompt = st.text_area(":orange[Prompt:]", value="Your idea goes here. Our AI will then enhance, optimize and then generate your image")

            # Then the Advanced Settings
            with st.expander("**Advanced Settings**"):
                # Advanced Settings for Flux-Dev
                width = st.number_input("Width of output image", value=1024)
                height = st.number_input("Height of output image", value=1024)
                num_outputs = st.slider("Number of images to output", value=1, min_value=1, max_value=2)
                guidance_scale = st.slider("Guidance scale (0 to 10)", value=3.5, min_value=0.0, max_value=10.0, step=0.1)
                num_inference_steps = st.slider("Number of denoising steps", value=28, min_value=1, max_value=50)
                aspect_ratio = st.selectbox('Aspect Ratio', ('1:1', '5:4', '16:9'))
                output_format = st.selectbox('Output format', ('webp', 'jpg', 'png'))
                output_quality = st.slider('Output quality (0-100, for jpg/webp)', value=80, min_value=0, max_value=100)
                disable_safety_checker = st.checkbox("Disable safety checker", value=True)

            # Submit button at the bottom
            submitted = st.form_submit_button("Generate", type="primary", use_container_width=True)

        st.divider()
        st.markdown(":orange[**Resources:**]  \nReplicate AI")

        return submitted, width, height, num_outputs, guidance_scale, num_inference_steps, aspect_ratio, output_format, output_quality, disable_safety_checker, prompt

def main_page(submitted: bool, width: int, height: int, num_outputs: int,
              guidance_scale: float, num_inference_steps: int,
              aspect_ratio: str, output_format: str, output_quality: int,
              disable_safety_checker: bool, prompt: str) -> None:
    if submitted:
        with st.status('Generating..', expanded=True):
            st.write("AI initiated")
            try:
                if submitted:
                    with generated_images_placeholder.container():
                        all_images = []
                        output = replicate.run(
                            REPLICATE_MODEL_ENDPOINT,
                            input={
                                "prompt": prompt,
                                "guidance": guidance_scale,
                                "num_outputs": num_outputs,
                                "num_inference_steps": num_inference_steps,
                                "aspect_ratio": aspect_ratio,
                                "output_format": output_format,
                                "output_quality": output_quality,
                                "disable_safety_checker": disable_safety_checker
                            }
                        )
                        if output:
                            st.toast('Your image has been generated!', icon='😍')
                            st.session_state.generated_image = output

                            for image in st.session_state.generated_image:
                                with st.container():
                                    st.image(image, caption="Generated Image", use_column_width=True)
                                    all_images.append(image)

                                    response = requests.get(image)

                        st.session_state.all_images = all_images

                        zip_io = io.BytesIO()
                        with zipfile.ZipFile(zip_io, 'w') as zipf:
                            for i, image in enumerate(st.session_state.all_images):
                                response = requests.get(image)
                                if response.status_code == 200:
                                    image_data = response.content
                                    zipf.writestr(f"output_file_{i+1}.png", image_data)

                        st.download_button(":red[**Download All Images**]", data=zip_io.getvalue(), file_name="output_files.zip", mime="application/zip", use_container_width=True)
            except Exception as e:
                print(e)
                st.error(f'Encountered an error: {e}', icon="🚨")

    else:
        pass

    with gallery_placeholder.container():
        img = image_select(
            label="Want to save an image? Right-click and save!",
            images=[
                "gallery/futurecity.webp", "gallery/robot.webp",
                "gallery/fest.webp", "gallery/wizard.png",
                "gallery/skateboard.webp",
                "gallery/anime.jpg", "gallery/viking.png",
            ],
            captions=[
                "A futuristic city skyline at sunset, with flying cars and glowing holograms, ultra-realistic",
                "A robot bartender serving drinks to human and alien patrons in a sleek space station lounge, realistic.",
                "A group of friends laughing and dancing at a music festival, joyful atmosphere, 35mm film photography",
                "A wizard casting a spell, intense magical energy glowing from his hands",
                "A woman street skateboarding in Paris Olympics 2024",
                "Anime style portrait of a female samurai at a beautiful lake with cherry trees, mountain fuji background, spring, sunset",
                "A photorealistic close-up portrait of a bearded viking warrior in a horned helmet. He stares intensely into the distance while holding a battle axe. Dramatic mood lighting."
            ],
            use_container_width=True

        )
def main():
    submitted, width, height, num_outputs, guidance_scale, num_inference_steps, aspect_ratio, output_format, output_quality, disable_safety_checker, prompt = configure_sidebar()
    main_page(submitted, width, height, num_outputs, guidance_scale, num_inference_steps, aspect_ratio, output_format, output_quality, disable_safety_checker, prompt)

if __name__ == "__main__":
    main()
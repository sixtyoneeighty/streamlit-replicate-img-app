import streamlit as st
import google.generativeai as genai
from streamlit_image_select import image_select
from together import Together
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Configure Gemini API with Streamlit secrets
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

# Configure Together AI client
client = Together(api_key=st.secrets["TOGETHER_API_KEY"])

# Configure page layout
st.set_page_config(page_title="sixtyoneeighty Image AI", layout="wide")

# Custom CSS for additional styling (unchanged)
st.markdown(
    """
    <style>
    /* ... (rest of the CSS remains the same) ... */
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown("# sixtyoneeighty")

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
        "content": "You are an expert AI assistant, specializing in photography and prompt enhancement...",
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
7. Type of camera and lens used, if relevant""",
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
        generation_config={
            "temperature": 1.0,  # Updated temperature value
            "top_p": 0.95,
            "top_k": 64,
            "max_output_tokens": 8192,
        },
    )
def configure_sidebar() -> tuple:
    with st.sidebar:
        with st.form("my_form"):
            try:
                # Logo
                st.image("gallery/logo.png", use_column_width=True)
            except Exception as e:
                logging.error(f"Error loading image: {e}")

            # Input prompt
            try:
                prompt = st.text_area(
                    "Prompt:",
                    value=st.session_state.get("prompt", ""),
                    placeholder="Enter your idea here. Our AI will enhance, optimize, and generate your image.",
                )
            except Exception as e:
                logging.error(f"Error with text area: {e}")
                prompt = ""

            # Checkbox to skip prompt enhancement
            try:
                skip_enhancement = st.checkbox("Skip Prompt Enhancement", value=False)
            except Exception as e:
                logging.error(f"Error with checkbox: {e}")
                skip_enhancement = False

            # Advanced settings
            with st.expander("**Advanced Settings**"):
                try:
                    image_size = st.selectbox("Image Size", ["square_hd", "square", "portrait_4_3", "portrait_16_9", "landscape_4_3", "landscape_16_9"], index=4)
                    seed = st.number_input("Seed (optional)", value=0, min_value=0, step=1)
                    sync_mode = st.checkbox("Sync Mode", value=True)
                    num_images = st.slider("Number of images to generate", value=1, min_value=1, max_value=10)
                    enable_safety_checker = st.checkbox("Enable Safety Checker", value=True)
                    safety_tolerance = st.selectbox("Safety Tolerance", ["1", "2", "3", "4", "5", "6"], index=1)
                except Exception as e:
                    logging.error(f"Error with advanced settings: {e}")

            try:
                submitted = st.form_submit_button("Generate Image")
            except Exception as e:
                logging.error(f"Error with form submit button: {e}")
                submitted = False

    return (submitted, prompt, image_size, seed, sync_mode, num_images, enable_safety_checker, safety_tolerance, skip_enhancement)
def generate_image(prompt: str) -> str:
    try:
        response = client.images.generate(
            prompt=prompt,
            model="black-forest-labs/FLUX.1.1-pro",
            width=1024,
            height=768,
            steps=1,
            n=1,
            response_format="b64_json",
        )
        return response.data[0].b64_json
    except Exception as e:
        logging.error(f"Error generating image: {e}")
        return "Error generating image"

def generate_image(prompt: str) -> str:
    response = client.images.generate(
        prompt=prompt,
        model="black-forest-labs/FLUX.1.1-pro",
        width=1024,
        height=768,
        steps=1,
        n=1,
        response_format="b64_json",
    )
    return response.data[0].b64_json

def main_page(submitted: bool, topic: str, skip_enhancement: bool) -> None:
    if submitted:
        gallery_placeholder.empty()
        with st.status("Generating image...", expanded=True):
            try:
                if not skip_enhancement:
                    enhanced_prompt = get_enhanced_prompt(topic)
                    cleaned_prompt = (
                        enhanced_prompt.get("prompt", "")
                        if isinstance(enhanced_prompt, dict)
                        else enhanced_prompt
                    )
                else:
                    cleaned_prompt = topic

                output = generate_image(cleaned_prompt)

                if output:
                    st.image(output, use_column_width=False, width=400)
                    st.markdown(
                        f"<p style='font-size:14px; color:purple;'><strong>Your new enhanced prompt:</strong> {cleaned_prompt}</p>",
                        unsafe_allow_html=True,
                    )
                else:
                    st.error("Failed to generate image.")
            except Exception as e:
                st.error(f"Error: {e}")
    else:
        with gallery_placeholder.container():
            img = image_select(
            # img = image_select(save an image? Right-click and save!",
                images=[
                    "gallery/futurecity.webp",
                    "gallery/robot.webp",
                    "gallery/fest.webp",
                    "gallery/wizard.png",
                    "gallery/skateboard.webp",
                    "gallery/anime.jpg",
                    "gallery/viking.png",
                ],
                captions=[
                    "A futuristic city skyline at sunset, with flying cars and glowing holograms, ultra-realistic",
                    "A robot bartender serving drinks to human and alien patrons in a sleek space station lounge, realistic.",
                    "A group of friends laughing and dancing at a music festival, joyful atmosphere, 35mm film photography",
                    "A wizard casting a spell, intense magical energy glowing from his hands",
                    "A woman street skateboarding in Paris Olympics 2024",
                    "Anime style portrait of a female samurai at a beautiful lake with cherry trees, mountain fuji background, spring, sunset",
                    "A photorealistic close-up portrait of a bearded viking warrior in a horned helmet. He stares intensely into the distance while holding a battle axe. Dramatic mood lighting.",
                ],
                use_container_width=True,
            )
def main():
    (
        submitted,
        prompt,
        image_size,
        # image_size,
        # seed,mode,
        # sync_mode,,
        # num_images,ty_checker,
        # enable_safety_checker,
        # safety_tolerance,
    ) = configure_sidebar()

    if submitted:
        if not skip_enhancement:
            prompt = get_enhanced_prompt(prompt)
        image_data = generate_image(prompt)
        st.image(image_data, use_column_width=True)
    main_page(submitted, prompt, skip_enhancement)

if __name__ == "__main__":
    main()
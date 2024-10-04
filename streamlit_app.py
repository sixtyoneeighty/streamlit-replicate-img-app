import os
import streamlit as st
import google.generativeai as genai
from streamlit_image_select import image_select
from together import Together

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
        model_name="gemini-1.5-pro-latest",  # Updated model name
        generation_config={
            "temperature": 1.0,  # Updated temperature value
            "top_p": 0.95,
            "top_k": 64,
            "max_output_tokens": 8192,
        },
    )
    chat_session = model.start_chat(history=[])
    response = chat_session.send_message(prompt_text)
    return response.text

def configure_sidebar() -> tuple:
    with st.sidebar:
        with st.form("my_form"):
            # Logo
            st.image("gallery/logo.png", use_column_width=True)

            # Input prompt
            prompt = st.text_area(
                "Prompt:",
                value=st.session_state["prompt"],
                placeholder="Enter your idea here. Our AI will enhance, optimize, and generate your image.",
            )

            # Checkbox to skip prompt enhancement
            skip_enhancement = st.checkbox("Skip Prompt Enhancement", value=False)

            # Buttons
            st.markdown('<div class="button-container">', unsafe_allow_html=True)
            submitted = st.form_submit_button("Generate Image", type="primary")
            if st.form_submit_button("Clear"):
                st.session_state["prompt"] = ""
                st.experimental_rerun()
            st.markdown("</div>", unsafe_allow_html=True)

        # Resource section with the new link and no 'Replicate AI' text
        st.markdown(
            ':orange[**Resources:**]  \n[Your guide to sixtyoneeighty Image AI](https://sites.google.com/sixtyoneeightyai.com/imageai/home)'
        )

        return submitted, prompt, skip_enhancement

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
                label="Want to save an image? Right-click and save!",
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
        skip_enhancement,
    ) = configure_sidebar()
    main_page(submitted, prompt, skip_enhancement)

if __name__ == "__main__":
    main()
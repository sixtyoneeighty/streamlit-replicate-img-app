import os
import streamlit as st
import google.generativeai as genai
from streamlit_image_select import image_select
from together import Together
import base64
from io import BytesIO
from PIL import Image

# Configure Gemini API with Streamlit secrets
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

# Configure Together AI client
together_client = Together(api_key=st.secrets["TOGETHER_API_KEY"])

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
    """, unsafe_allow_html=True
)

st.markdown("# sixtyoneeighty")

# Placeholders for images and gallery
generated_images_placeholder = st.empty()
gallery_placeholder = st.empty()

# Global state to manage prompt text
if "prompt" not in st.session_state:
    st.session_state["prompt"] = ""

def get_enhanced_prompt(topic: str) -> str:
    """Use Gemini API to enhance the user's prompt."""
    prompt_text = f"""You are an AI assistant specializing in refining user prompts for the Flux image generation model. Flux requires two complementary prompts that work together to create one cohesive image. When refining user prompts, follow these guidelines:

Topic: {topic}

1. Enhanced Prompt (Natural Language):
- Provide an extremely detailed description of the image in natural language, using up to 512 tokens.
- Break down the scene into key components: subjects, setting, lighting, colors, composition, and atmosphere.
- Describe subjects in great detail, including their appearance, pose, expression, clothing, and any interactions between them.
- Elaborate on the setting, specifying the time of day, location specifics, architectural details, and any relevant objects or props.
- Explain the lighting conditions, including the source, intensity, shadows, and how it affects the overall scene.
- Using your knowledge set, select an appropriate high end camera and lens combination that should be used to capture the image.
- Specify color palettes and any significant color contrasts or harmonies that contribute to the image's visual impact.
- Detail the composition, describing the foreground, middle ground, background, and focal points to create a sense of depth and guide the viewer's eye.
- Convey the overall mood and atmosphere of the scene, using emotive language to evoke the desired feeling.
- Use vivid, descriptive language to paint a clear picture, as Flux follows instructions precisely but lacks inherent creativity.
- Avoid using grammatically negative statements or describing what the image should not include, as Flux may struggle to interpret these correctly. Instead, focus on positively stating what should be present in the image.

2. Keyword Prompt (Concise Keywords):
- Create a concise list of essential keywords and phrases, limited to 50-60 tokens (maximum 70).
- Prioritize the keywords in this order: main subject(s), art style, setting, important features, emotions/mood, lighting, and color scheme.
- Include relevant artistic techniques, visual effects, or stylistic elements if applicable to the requested image.
- Use commas to separate keywords and phrases, ensuring clarity and readability.
- Ensure that the keywords align perfectly with the details provided in the Enhanced prompt, as both prompts work together to generate the final image.
- Focus on keywords that positively describe what should be present in the image, rather than using keywords that negate or exclude certain elements.

When generating these prompts:
- Understand that the Enhanced and Keyword prompts are deeply connected and must align perfectly to create a single, cohesive image.
- Adapt your language and terminology to the requested art style (e.g., photorealistic, anime, oil painting) to maintain consistency across both prompts. Default style should be photorealistic unless it is stated otherwise in users original prompt.
- Consider potential visual symbolism, metaphors, or allegories that could enhance the image's meaning and impact, and include them in both prompts when relevant.
- For character-focused images, emphasize personality traits and emotions through visual cues such as facial expressions, body language, and clothing choices, ensuring consistency between the T5 and CLIP prompts.
- Maintain grammatically positive statements throughout both prompts, focusing on what the image should include rather than what it should not, as Flux may struggle with interpreting negative statements accurately.
- The enhancements should not take away or change the overall context of the original prompt, the objective is to bring the image to life not change the core vision of it.

Present your response in this format with no additional information or elaboration included:
Enhanced Prompt: [Detailed natural language description]
Keywords: [Concise keyword list]"""
    
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash-latest",
        generation_config={
            "temperature": 1.0,
            "top_p": 0.95,
            "top_k": 64,
            "max_output_tokens": 8192,
        }
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
            prompt = st.text_area("Prompt:", value=st.session_state["prompt"],
                                  placeholder="Enter your idea here. Our AI will enhance, optimize, and generate your image.")

            # Checkbox to skip prompt enhancement
            skip_enhancement = st.checkbox("Skip Prompt Enhancement", value=False)

            # Buttons
            st.markdown('<div class="button-container">', unsafe_allow_html=True)
            submitted = st.form_submit_button("Generate Image", type="primary")
            if st.form_submit_button("Clear"):
                st.session_state["prompt"] = ""
                st.experimental_rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        # Resource section with the new link and no 'Replicate AI' text
        st.markdown(":orange[**Resources:**]  \n[Your guide to sixtyoneeighty Image AI](https://sites.google.com/sixtyoneeightyai.com/imageai/home)")

        return submitted, prompt, skip_enhancement

def generate_image(prompt: str) -> Image.Image:
    response = together_client.images.generate(
        prompt=prompt,
        model="black-forest-labs/FLUX.1.1-pro",
        width=1024,
        height=768,
        steps=1,
        n=1,
        response_format="b64_json"
    )
    image_data = base64.b64decode(response.data[0].b64_json)
    image = Image.open(BytesIO(image_data))
    return image

def main_page(submitted: bool, topic: str, skip_enhancement: bool) -> None:
    if submitted:
        gallery_placeholder.empty()
        with st.status('Generating image...', expanded=True):
            try:
                if not skip_enhancement:
                    enhanced_prompt = get_enhanced_prompt(topic)
                    cleaned_prompt = enhanced_prompt if isinstance(enhanced_prompt, str) else enhanced_prompt.get("prompt", "")
                else:
                    cleaned_prompt = topic

                output_image = generate_image(cleaned_prompt)
                
                if output_image:
                    st.image(output_image, use_column_width=False, width=400)
                    st.markdown(f"<p style='font-size:14px; color:purple;'><strong>Your new enhanced prompt:</strong> {cleaned_prompt}</p>", unsafe_allow_html=True)
                else:
                    st.error("Failed to generate image.")
            except Exception as e:
                st.error(f"Error: {e}")
    else:
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
    submitted, prompt, skip_enhancement = configure_sidebar()
    main_page(submitted, prompt, skip_enhancement)

if __name__ == "__main__":
    main()
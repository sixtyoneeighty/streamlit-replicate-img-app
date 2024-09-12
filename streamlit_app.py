import os
import replicate
import streamlit as st
import google.generativeai as genai
from streamlit_image_select import image_select

# Configure Gemini API with Streamlit secrets
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

# Configure page layout
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
        background-color: #A64CF6 !important;
    }
    </style>
    """, unsafe_allow_html=True
)

st.markdown("# sixtyoneeighty")

# Hardcoded Replicate model
REPLICATE_MODEL_ENDPOINT = "black-forest-labs/flux-dev"

# Access Replicate API token from secrets
REPLICATE_API_TOKEN = st.secrets["REPLICATE_API_TOKEN"]

# Global state to manage prompt text
if "prompt" not in st.session_state:
    st.session_state["prompt"] = ""

def magic_prompt(topic: str) -> list:
    """Generate the system and user message based on the topic."""
    
    system_message = {
        "role": "system",
        "content": "You are an expert AI assistant, specializing in photography and prompt enhancement. You will dive deep into the user's ideas, extracting the essence of their vision. Then, weave those concepts into a tapestry of descriptive language, painting a vivid scene or concept for the AI to render. Be bold, creative, and detail-oriented, ensuring every prompt is a masterpiece waiting to be realized."
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
7. Type of camera and lens used, if relevant

Follow this format: Main character or Main subject:..., Background:..., Lighting:..., Color scheme:..., Atmosphere:..., Actions:..., Objects:..., Camera:..., Lens:...
"""
    }

    return [system_message, user_message]

def get_enhanced_prompt(topic: str) -> str:
    """Use Gemini API to enhance the user's prompt."""
    # Generate the system and user messages using magic_prompt
    messages = magic_prompt(topic)

    # Start a chat session with the Gemini model
    model = genai.GenerativeModel(
        model_name="gemini-1.5-pro-exp-0827",
        generation_config={
            "temperature": 1.5,
            "top_p": 0.95,
            "top_k": 64,
            "max_output_tokens": 8192,
            "response_mime_type": "application/json",
        },
        system_instruction="You are an AI assistant specializing in creating detailed prompts for image generation based on given topics and styles."
    )

    chat_session = model.start_chat(history=messages)

    # Send the message and get the enhanced prompt
    response = chat_session.send_message("Generate an enhanced image prompt based on the provided messages.")
    
    # Return the enhanced prompt
    return response.text

def configure_sidebar() -> tuple:
    """Configure the sidebar with user inputs"""
    with st.sidebar:
        with st.form("my_form"):
            # Logo
            st.image("gallery/logo.png", use_column_width=True)

            # Input prompt
            prompt = st.text_area("Prompt:", value=st.session_state["prompt"],
                                  placeholder="Enter your idea here. Our AI will enhance, optimize, and generate your image.")

            # Checkbox to skip prompt enhancement
            skip_enhancement = st.checkbox("Skip Prompt Enhancement", value=False)

            # Advanced settings
            with st.expander("**Advanced Settings**"):
                width = st.number_input("Width of output image", value=512)
                height = st.number_input("Height of output image", value=512)
                num_outputs = st.slider("Number of images to output", value=1, min_value=1, max_value=2)
                guidance_scale = st.slider("Guidance scale (0 to 10)", value=3.5, min_value=0.0, max_value=10.0, step=0.1)
                num_inference_steps = st.slider("Number of denoising steps", value=28, min_value=1, max_value=50)
                aspect_ratio = st.selectbox('Aspect Ratio', ('1:1', '5:4', '16:9'))
                output_format = st.selectbox('Output format', ('webp', 'jpg', 'png'))
                output_quality = st.slider('Output quality (0-100)', value=80, min_value=0, max_value=100)
                disable_safety_checker = st.checkbox("Disable safety checker", value=True)

            # Buttons
            st.markdown('<div class="button-container">', unsafe_allow_html=True)
            submitted = st.form_submit_button("Generate Image", type="primary")
            if st.form_submit_button("Clear"):
                st.session_state["prompt"] = ""
                st.experimental_rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown(":orange[**Resources:**]  \nReplicate AI")

        return submitted, width, height, num_outputs, guidance_scale, num_inference_steps, aspect_ratio, output_format, output_quality, disable_safety_checker, prompt, skip_enhancement

def generate_image(prompt: str, width: int, height: int, num_outputs: int, guidance_scale: float, num_inference_steps: int, aspect_ratio: str, output_format: str, output_quality: int, disable_safety_checker: bool) -> str:
    """Generate an image using Replicate API"""
    output = replicate.run(
        REPLICATE_MODEL_ENDPOINT,
        input={
            "prompt": prompt,
            "width": width,
            "height": height,
            "num_outputs": num_outputs,
            "guidance": guidance_scale,
            "num_inference_steps": num_inference_steps,
            "aspect_ratio": aspect_ratio,
            "output_format": output_format,
            "output_quality": output_quality,
            "disable_safety_checker": disable_safety_checker
        },
        auth=REPLICATE_API_TOKEN  # Using the token from secrets
    )
    return output

def main_page(submitted: bool, width: int, height: int, num_outputs: int,
              guidance_scale: float, num_inference_steps: int,
              aspect_ratio: str, output_format: str, output_quality: int,
              disable_safety_checker: bool, topic: str, skip_enhancement: bool) -> None:
    """Main page logic for generating and displaying the image"""
    if submitted:
        with st.status('Generating image...', expanded=True):
            try:
                if not skip_enhancement:
                    # Enhance the prompt using Gemini and magic_prompt logic
                    enhanced_prompt = get_enhanced_prompt(topic)
                    
                    # Log the enhanced prompt to the console for debugging
                    print(f"Enhanced Prompt for Debugging: {enhanced_prompt}")
                    
                    st.write(f"Enhanced Prompt: {enhanced_prompt}")  # Optional, remove if you don't want to display
                else:
                    enhanced_prompt = topic

                # Generate the image
                output = generate_image(enhanced_prompt, width, height, num_outputs, guidance_scale, num_inference_steps, aspect_ratio, output_format, output_quality, disable_safety_checker)
                
                if output:
                    st.image(output[0], use_column_width=False, width=400)
                else:
                    st.error("Failed to generate image.")

            except Exception as e:
                st.error(f"Error: {e}")

def main():
    submitted, width, height, num_outputs, guidance_scale, num_inference_steps, aspect_ratio, output_format, output_quality, disable_safety_checker, prompt, skip_enhancement = configure_sidebar()
    main_page(submitted, width, height, num_outputs, guidance_scale, num_inference_steps, aspect_ratio, output_format, output_quality, disable_safety_checker, prompt, skip_enhancement)

if __name__ == "__main__":
    main()
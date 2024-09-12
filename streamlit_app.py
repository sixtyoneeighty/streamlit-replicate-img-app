import os
import streamlit as st

# Serve the 'gallery' folder as static files
if not os.path.exists("gallery"):
    os.makedirs("gallery")

st.markdown(
    """
    <style>
    /* Flexbox for gallery to make images evenly spaced */
    .gallery-container {
        display: flex;
        flex-wrap: wrap;
        justify-content: space-between;
        gap: 20px; /* Add some space between items */
    }

    /* Style for individual gallery items */
    .gallery-item {
        flex: 1 1 calc(33% - 20px);  /* Make each image take up 1/3 of the row */
        box-sizing: border-box;
        margin-bottom: 20px;  /* Add spacing below the images */
    }

    img {
        width: 100%;
        height: auto;
        border-radius: 10px;  /* Optional: Add rounded corners */
    }
    </style>
    """, unsafe_allow_html=True
)

st.markdown('<div class="gallery-container">', unsafe_allow_html=True)

# Image paths should be inside the 'gallery/' folder
st.markdown('''
<div class="gallery-item">
    <img src="gallery/futurecity.webp" alt="Futuristic city" />
    <p>A futuristic city skyline at sunset, with flying cars and glowing holograms, ultra-realistic</p>
</div>
<div class="gallery-item">
    <img src="gallery/robot.webp" alt="Robot bartender" />
    <p>A robot bartender serving drinks to human and alien patrons in a sleek space station lounge, realistic.</p>
</div>
<div class="gallery-item">
    <img src="gallery/fest.webp" alt="Music festival" />
    <p>A group of friends laughing and dancing at a music festival, joyful atmosphere, 35mm film photography</p>
</div>
<div class="gallery-item">
    <img src="gallery/wizard.png" alt="Wizard casting spell" />
    <p>A wizard casting a spell, intense magical energy glowing from his hands</p>
</div>
<div class="gallery-item">
    <img src="gallery/skateboard.webp" alt="Street skateboarding" />
    <p>A woman street skateboarding in Paris Olympics 2024</p>
</div>
<div class="gallery-item">
    <img src="gallery/anime.jpg" alt="Anime samurai" />
    <p>Anime style portrait of a female samurai at a beautiful lake with cherry trees, mountain fuji background, spring, sunset</p>
</div>
<div class="gallery-item">
    <img src="gallery/viking.png" alt="Viking portrait" />
    <p>A photorealistic close-up portrait of a bearded viking warrior in a horned helmet. He stares intensely into the distance while holding a battle axe. Dramatic mood lighting.</p>
</div>
''', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
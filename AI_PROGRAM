import streamlit as st
import base64
import openai
from PIL import Image
from io import BytesIO
import os

st.set_page_config(layout="wide")

# --- CONFIG ---
openai.api_key = st.secrets.get("OPENAI_API_KEY")
CANVAS_SIZE = (800, 600)

# --- UTILITIES ---
def load_image_as_base64(path):
    with open(path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode("utf-8")

def display_reference_images():
    st.markdown("### 🧠 Reference Diagrams")
    cols = st.columns(3)
    for i, col in enumerate(cols):
        col.image(f"diagram_{i+1}.png", caption=f"Diagram {i+1}", use_column_width=True)

def generate_prompt_with_images():
    images_base64 = [load_image_as_base64(f"diagram_{i+1}.png") for i in range(3)]
    image_messages = [
        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img}"}}
        for img in images_base64
    ]
    system_msg = {
        "role": "system",
        "content": "You are a physics tutor and visual diagram generator. Analyze the diagrams below to understand typical layout patterns. Then, generate a new physics question and a corresponding SVG diagram (800x600 canvas, white background, all objects outlined only, no fill)."
    }
    user_msg = {
        "role": "user",
        "content": image_messages + [
            {"type": "text", "text": "Based on your analysis, create a new physics question and an SVG diagram that follows similar visual structure. Return both the question and the SVG code, clearly separated."}
        ]
    }
    return [system_msg, user_msg]

def generate_variants(n=3):
    messages = generate_prompt_with_images()
    results = []
    for _ in range(n):
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=messages,
            temperature=0.8
        )
        content = response.choices[0].message.content
        parts = content.split("<svg")
        if len(parts) < 2:
            continue
        question = parts[0].strip()
        svg_code = "<svg" + parts[1].split("</svg>")[0] + "</svg>"
        results.append({"question": question, "svg": svg_code})
    return results

# --- APP ---
st.title("🧠 Physics Diagram Generator with Visual Reference")

with st.expander("See Reference Diagrams"):
    display_reference_images()

st.markdown("---")

if st.button("Generate New Physics Questions and Diagrams"):
    with st.spinner("Generating multiple variations..."):
        variants = generate_variants(3)
    st.markdown("### 🎯 Pick Your Favorite Variant")
    for i, variant in enumerate(variants):
        st.subheader(f"Variant {i+1}")
        st.markdown(f"**Question:** {variant['question']}")
        st.markdown(variant['svg'], unsafe_allow_html=True)
        st.markdown("---")

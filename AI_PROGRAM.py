import streamlit as st
import openai
import os
import random
import base64
from datetime import datetime

# --- Config ---
TRAINING_DIR = "training_data"
MODEL = "gpt-4o"
EXAMPLES_TO_USE = 3

# --- Utils ---
def encode_image_to_base64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

def get_random_examples(n):
    subdirs = [os.path.join(TRAINING_DIR, d) for d in os.listdir(TRAINING_DIR) if os.path.isdir(os.path.join(TRAINING_DIR, d))]
    return random.sample(subdirs, min(n, len(subdirs)))

def generate_svg_from_examples(example_dirs):
    messages = [
        {
            "role": "system",
            "content": "You're a physics tutor. Study the diagram image examples and their corresponding questions. Then generate a new physics diagram (as SVG code) and a matching question based on the patterns you find."
        }
    ]

    for i, folder in enumerate(example_dirs):
        png_path = os.path.join(folder, "diagram.png")
        txt_path = os.path.join(folder, "question.txt")

        encoded_image = encode_image_to_base64(png_path)
        question_text = open(txt_path, "r").read().strip()

        messages.append({
            "role": "user",
            "content": [
                {"type": "text", "text": f"Example {i+1}:\n{question_text}"},
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{encoded_image}"}}
            ]
        })

    messages.append({
        "role": "user",
        "content": "Now please generate a new physics question and an accompanying SVG diagram. Only return the question followed by the SVG code. Keep the SVG under 100 lines."
    })

    response = openai.ChatCompletion.create(
        model=MODEL,
        messages=messages,
        temperature=0.7
    )

    return response.choices[0].message.content.strip()

def save_output(question, svg_code):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    folder_name = os.path.join(TRAINING_DIR, f"generated_{timestamp}")
    os.makedirs(folder_name, exist_ok=True)

    with open(os.path.join(folder_name, "diagram.svg"), "w") as f:
        f.write(svg_code)

    with open(os.path.join(folder_name, "question.txt"), "w") as f:
        f.write(question)

    return folder_name

# --- Streamlit App ---
st.set_page_config(page_title="Physics SVG Generator", layout="wide")
st.title("📐 Physics Diagram + Question Generator (Vision-Guided)")

if "examples" not in st.session_state:
    st.session_state.examples = get_random_examples(EXAMPLES_TO_USE)

# Step 1: Show examples
st.subheader("🧠 Training Examples Used")

cols = st.columns(EXAMPLES_TO_USE)
for idx, folder in enumerate(st.session_state.examples):
    with cols[idx]:
        st.image(os.path.join(folder, "diagram.png"), use_column_width=True)
        question_text = open(os.path.join(folder, "question.txt")).read()
        st.caption(question_text)

# Step 2: Generate
if st.button("🎲 Generate New Question + SVG"):
    with st.spinner("Generating..."):
        output = generate_svg_from_examples(st.session_state.examples)

        # Try to split the question and the SVG
        svg_start = output.find("<svg")
        if svg_start != -1:
            question = output[:svg_start].strip()
            svg_code = output[svg_start:]
        else:
            question, svg_code = output, ""

        st.session_state.generated = {
            "question": question,
            "svg": svg_code
        }

# Step 3: Display
if "generated" in st.session_state:
    st.subheader("🆕 Generated Question")
    st.markdown(st.session_state.generated["question"])

    st.subheader("📊 Generated Diagram")
    st.markdown(f"```xml\n{st.session_state.generated['svg']}\n```", unsafe_allow_html=True)
    st.components.v1.html(st.session_state.generated["svg"], height=400)

    if st.button("💾 Save to training_data"):
        folder = save_output(
            st.session_state.generated["question"],
            st.session_state.generated["svg"]
        )
        st.success(f"Saved to `{folder}` ✅")

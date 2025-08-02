import streamlit as st
import os
import uuid

TRAINING_DIR = "training_data"
os.makedirs(TRAINING_DIR, exist_ok=True)

st.header("📁 Training Data Uploader")

# --- Upload Form ---
with st.form("upload_form"):
    uploaded_image = st.file_uploader("Upload Diagram Image (PNG)", type=["png"])
    question_text = st.text_area("Enter Associated Physics Question")
    submitted = st.form_submit_button("Save Example")

    if submitted:
        if uploaded_image and question_text.strip():
            example_id = f"example_{uuid.uuid4().hex[:8]}"
            folder_path = os.path.join(TRAINING_DIR, example_id)
            os.makedirs(folder_path, exist_ok=True)

            with open(os.path.join(folder_path, "diagram.png"), "wb") as f:
                f.write(uploaded_image.getbuffer())

            with open(os.path.join(folder_path, "question.txt"), "w", encoding="utf-8") as f:
                f.write(question_text.strip())

            st.success(f"✅ Saved new example in `{folder_path}`")
        else:
            st.warning("⚠️ Please upload an image and enter a question before submitting.")

# --- Display Current Examples ---
st.markdown("---")
st.subheader("📚 Current Examples in Training Data")

example_dirs = [d for d in os.listdir(TRAINING_DIR) if os.path.isdir(os.path.join(TRAINING_DIR, d))]

if not example_dirs:
    st.info("No examples currently found in the training data folder.")
else:
    for example in sorted(example_dirs):
        path = os.path.join(TRAINING_DIR, example)
        img_path = os.path.join(path, "diagram.png")
        txt_path = os.path.join(path, "question.txt")

        col1, col2 = st.columns([1, 2])
        with col1:
            if os.path.exists(img_path):
                st.image(img_path, width=160)
        with col2:
            if os.path.exists(txt_path):
                with open(txt_path, "r") as f:
                    question = f.read()
                st.markdown(f"**{example}**\n\n{question}")

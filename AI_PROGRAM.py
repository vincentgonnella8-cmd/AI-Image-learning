import streamlit as st
import os
import uuid
import shutil

TRAINING_DIR = "training_data"
os.makedirs(TRAINING_DIR, exist_ok=True)

st.header("📁 Training Data Uploader")

# --- Upload Form ---
with st.form("upload_form"):
    uploaded_image = st.file_uploader("Upload Diagram Image (PNG)", type=["png"])
    question_text = st.text_area("Enter Associated Physics Question", height=150)
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

example_dirs = sorted([d for d in os.listdir(TRAINING_DIR) if os.path.isdir(os.path.join(TRAINING_DIR, d))])

# Track if we deleted something to rerun after loop
if "deleted_example" not in st.session_state:
    st.session_state.deleted_example = False

if not example_dirs:
    st.info("No examples currently found in the training data folder.")
else:
    for example in example_dirs:
        path = os.path.join(TRAINING_DIR, example)
        img_path = os.path.join(path, "diagram.png")
        txt_path = os.path.join(path, "question.txt")

        col1, col2, col3 = st.columns([1, 5, 1])
        with col1:
            if os.path.exists(img_path):
                st.image(img_path, width=160)
        with col2:
            if os.path.exists(txt_path):
                with open(txt_path, "r", encoding="utf-8") as f:
                    question = f.read()

                preview = question[:150].replace("\n", " ") + ("..." if len(question) > 150 else "")
                with st.expander(f"Question Preview ({example}): {preview}"):
                    st.write(question)
        with col3:
            if st.button("🗑️ Delete", key=f"del_{example}"):
                try:
                    shutil.rmtree(path)
                    st.success(f"Deleted example `{example}`")
                    st.session_state.deleted_example = True
                except Exception as e:
                    st.error(f"Error deleting `{example}`: {e}")

# Rerun only once after deletion(s)
if st.session_state.deleted_example:
    st.session_state.deleted_example = False
    st.experimental_rerun()

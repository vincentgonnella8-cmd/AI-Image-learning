import streamlit as st
import os
from PIL import Image
import shutil

# Load delete password from secrets
DELETE_PASSWORD = st.secrets.get("admin", {}).get("delete_password", "letmein")

# Paths
DATA_DIR = "training_data"

st.set_page_config(page_title="Physics Diagram Trainer", layout="wide")
st.title("📚 AI Physics Diagram Trainer")

# Ensure training data directory exists
os.makedirs(DATA_DIR, exist_ok=True)

# --- Section: Upload New Training Example ---
st.header("➕ Add New Training Example")
with st.container():
    upload_cols = st.columns([2, 3])
    with upload_cols[0]:
        uploaded_image = st.file_uploader("Upload Diagram (PNG)", type=["png"])
    with upload_cols[1]:
        question_text = st.text_area("Enter Physics Question", height=150)

    if uploaded_image and question_text:
        if st.button("✅ Finalize Upload"):
            example_name = question_text[:40].strip().replace(" ", "_").replace("/", "-")
            example_path = os.path.join(DATA_DIR, example_name)
            os.makedirs(example_path, exist_ok=True)

            # Save image
            image_save_path = os.path.join(example_path, "diagram.png")
            with open(image_save_path, "wb") as f:
                f.write(uploaded_image.read())

            # Save question
            question_save_path = os.path.join(example_path, "question.txt")
            with open(question_save_path, "w") as f:
                f.write(question_text)

            st.success(f"Saved new example to {example_name}")
            st.rerun()

# --- Section: Admin Access for Deletion ---
st.header("🛠 Manage Existing Training Data")

if "can_delete" not in st.session_state:
    st.session_state.can_delete = False

with st.expander("🔒 Admin Access to Delete Examples"):
    entered = st.text_input("Enter password to enable delete", type="password")
    if entered == DELETE_PASSWORD:
        st.success("✅ Delete access granted.")
        st.session_state.can_delete = True
    elif entered:
        st.error("❌ Incorrect password.")

# --- Section: Show Existing Examples ---
examples = sorted(os.listdir(DATA_DIR))
if not examples:
    st.info("No training data examples found yet.")
else:
    for example in examples:
        example_path = os.path.join(DATA_DIR, example)
        image_path = os.path.join(example_path, "diagram.png")
        question_path = os.path.join(example_path, "question.txt")

        if not (os.path.isfile(image_path) and os.path.isfile(question_path)):
            continue  # skip malformed examples

        with st.container():
            st.markdown("---")
            row_cols = st.columns([1, 2, 1])

            with row_cols[0]:
                st.markdown(f"**Diagram: `{example}`**")
                st.image(image_path, width=150)
                with st.expander("🔍 Expand Diagram Preview"):
                    st.image(image_path, use_column_width=True)

            with row_cols[1]:
                with open(question_path, "r") as f:
                    preview = f.read()
                st.markdown(f"**Question Preview:**")
                st.text_area("Full Question", preview, height=200, key=f"q_{example}")

            with row_cols[2]:
                if st.session_state.can_delete:
                    if st.button(f"🗑 Delete", key=f"del_{example}"):
                        try:
                            shutil.rmtree(example_path)
                            st.success(f"Deleted {example}")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error deleting {example}: {e}")

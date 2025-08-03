import streamlit as st
import os
from PIL import Image
import shutil
from datetime import datetime

# Load delete password from secrets
DELETE_PASSWORD = st.secrets.get("admin", {}).get("delete_password", "letmein")

# Paths
DATA_DIR = "training_data"
TRASH_DIR = "trash_data"

st.set_page_config(page_title="Physics Diagram Trainer", layout="wide")
st.title("📚 AI Physics Diagram Trainer")

# Ensure necessary directories exist
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(TRASH_DIR, exist_ok=True)

# --- Tabs ---
tabs = st.tabs(["Add & Review Examples", "🔐 Admin Panel"])

# --- Tab 1: Upload and View Examples ---
with tabs[0]:
    # --- Section: Upload New Training Example ---
    st.header("➕ Add New Training Example")
    col1, col2 = st.columns(2)

    with col1:
        uploaded_image = st.file_uploader("Upload Diagram (PNG)", type=["png"])
    with col2:
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

    # --- Section: Show Existing Examples ---
    st.header("📂 Existing Training Data Examples")
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

            col1, col2 = st.columns([3, 2])
            with col1:
                with open(question_path, "r") as f:
                    preview = f.read()

                st.markdown(f"**Example:** `{example}`")
                with st.expander("📄 Preview Question"):
                    st.text_area("Full Question:", preview, height=200)

            with col2:
                st.markdown(f"**Diagram:**")
                st.image(image_path, width=150)
                with st.expander("🔍 Expand Diagram Preview"):
                    st.image(image_path, use_column_width=True)

# --- Tab 2: Admin Panel ---
with tabs[1]:
    st.header("🔐 Admin Panel")

    if "can_delete" not in st.session_state:
        st.session_state.can_delete = False

    with st.expander("🔒 Enter Admin Password"):
        entered = st.text_input("Enter password to enable delete", type="password")
        if entered == DELETE_PASSWORD:
            st.success("✅ Delete access granted.")
            st.session_state.can_delete = True
        elif entered:
            st.error("❌ Incorrect password.")

    if st.session_state.can_delete:
        st.subheader("🗑 Delete Examples")
        examples = sorted(os.listdir(DATA_DIR))
        for example in examples:
            example_path = os.path.join(DATA_DIR, example)
            col_del, _ = st.columns([1, 5])
            with col_del:
                delete_button = st.button(f"🗑 Delete {example}", key=f"del_{example}")
                if delete_button:
                    try:
                        trash_path = os.path.join(TRASH_DIR, f"{example}_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
                        shutil.move(example_path, trash_path)
                        st.success(f"Moved {example} to trash")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error deleting {example}: {e}")

        st.subheader("♻️ Recover Deleted Examples")
        trashed = sorted(os.listdir(TRASH_DIR))
        for trashed_example in trashed:
            trashed_path = os.path.join(TRASH_DIR, trashed_example)
            col_rec, _ = st.columns([1, 5])
            with col_rec:
                recover_button = st.button(f"♻️ Recover {trashed_example}", key=f"rec_{trashed_example}")
                if recover_button:
                    try:
                        original_name = "_".join(trashed_example.split("_")[:-2])  # approximate original
                        restored_path = os.path.join(DATA_DIR, original_name)
                        shutil.move(trashed_path, restored_path)
                        st.success(f"Recovered {trashed_example}")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error recovering {trashed_example}: {e}")

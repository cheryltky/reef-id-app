"""
Coral Reef ID App — upload a dive photo for health/bleaching classification and location logging.
Uses NOAA ViT classifier (CORAL vs CORAL_BL). Persists predictions to reef_surveys.csv.
"""
import os
import streamlit as st
import pandas as pd
from PIL import Image
from transformers import pipeline

st.set_page_config(page_title="Coral Reef ID", page_icon="🪸", layout="centered")
st.title("🪸 Coral Reef ID App")
st.write("Upload a dive photo for coral health/bleaching classification and optional location logging.")


@st.cache_resource
def load_model():
    return pipeline(
        "image-classification",
        model="NMFS-OSI/noaa-esd-coral-bleaching-vit-classifier-v1",
    )


model = load_model()

# Use DATA_DIR if set (e.g. HF Spaces persistent storage); else repo root
data_dir = os.environ.get("DATA_DIR", ".")
csv_path = os.path.join(data_dir, "reef_surveys.csv")

uploaded_file = st.file_uploader("Choose reef image...", type=["jpg", "jpeg", "png"])
lat, lon = st.columns(2)
latitude = lat.number_input("Latitude (e.g., -27.5 Sydney)", value=-33.8688, format="%.4f")
longitude = lon.number_input("Longitude", value=151.2093, format="%.4f")

if uploaded_file and st.button("Identify Coral"):
    image = Image.open(uploaded_file).convert("RGB")
    st.image(image, caption="Uploaded reef photo", use_container_width=True)

    predictions = model(image)
    top_pred = predictions[0]
    st.success(
        f"**Prediction**: {top_pred['label']} (confidence: {top_pred['score']:.2%})"
    )

    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
    else:
        df = pd.DataFrame(
            columns=["label", "confidence", "latitude", "longitude", "timestamp"]
        )

    new_entry = {
        "label": top_pred["label"],
        "confidence": top_pred["score"],
        "latitude": latitude,
        "longitude": longitude,
        "timestamp": pd.Timestamp.now().isoformat(),
    }
    df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
    df.to_csv(csv_path, index=False)
    st.caption("Last 5 entries")
    st.dataframe(df.tail(5), use_container_width=True)

if os.path.exists(csv_path):
    st.subheader("Survey log")
    df_full = pd.read_csv(csv_path)
    st.dataframe(df_full, use_container_width=True)

import streamlit as st
from analyzer import (
    calculate_sharpness,
    calculate_noise,
    calculate_brightness,
    calculate_contrast,
    calculate_saturation,
    calculate_composition,
    composite_score
)
from PIL import Image, ImageOps
from PIL.ExifTags import TAGS
import os
import pandas as pd
import logging
import zipfile
import shutil
import io

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page config
st.set_page_config(
    page_title="📸 Best Shot Finder",
    page_icon="📸",
    layout="wide",
    initial_sidebar_state="expanded"
)
# Ensure temp folders exist
os.makedirs("temp", exist_ok=True)
os.makedirs("temp_uploaded", exist_ok=True)

# Sidebar navigation
st.sidebar.title("Navigation")
mode = st.sidebar.radio("Menu", ["Analyze", "About"])

def get_exif_data(img):
    try:
        exif = img.getexif()
        if not exif:
            return {}
        exif_data = {}
        for tag_id, value in exif.items():
            tag = TAGS.get(tag_id, tag_id)
            if tag in ["ExposureTime", "ISOSpeedRatings", "FNumber", "FocalLength"]:
                exif_data[tag] = value
        return exif_data
    except Exception as e:
        logger.warning(f"Error reading EXIF data: {str(e)}")
        return {}

def process_image(file, weights, filename=None):
    try:
        logger.info(f"Processing image: {filename or (file.name if not isinstance(file, str) else file)}")
        if isinstance(file, str):
            img = Image.open(file)
            name = os.path.basename(file)
        else:
            img = Image.open(file)
            name = filename or file.name
        
        img = ImageOps.exif_transpose(img)
        path = os.path.join("temp", name)
        # Save with high quality (95 for JPEG, or PNG for lossless)
        if name.lower().endswith('.png'):
            img.save(path, format='PNG')
        else:
            img.save(path, quality=95)

        metrics = {
            "sharpness": calculate_sharpness(path),
            "noise": calculate_noise(path),
            "brightness": calculate_brightness(path),
            "contrast": calculate_contrast(path),
            "saturation": calculate_saturation(path),
            "composition": calculate_composition(path)
        }
        exif_data = get_exif_data(img)
        if weights:
            metrics["composite"] = composite_score(metrics, weights)
        logger.info(f"Metrics for {name}: {metrics}, EXIF: {exif_data}")
        return {"name": name, "image": img, "metrics": metrics, "path": path, "exif": exif_data}
    except Exception as e:
        st.error(f"Error processing {filename or (file.name if not isinstance(file, str) else file)}: {str(e)}")
        logger.error(f"Error processing {filename or (file.name if not isinstance(file, str) else file)}: {str(e)}")
        return None

def create_zip(images):
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as z:
        for img in images:
            with open(img['path'], 'rb') as f:
                z.writestr(img['name'], f.read())
    buffer.seek(0)
    return buffer

if mode == "Analyze":
    st.header("📸 Best Shot Finder")
    st.markdown(
        "Upload up to 10 images or a ZIP file. Metrics are normalized 0–100 for clarity."
    )

    # Initialize session state for weights and calculation trigger
    if "weights" not in st.session_state:
        st.session_state.weights = {
            "sharpness": 0.25,
            "noise": -0.2,
            "brightness": 0.2,
            "contrast": 0.2,
            "saturation": 0.15,
            "composition": 0.2
        }
    if "calculate_triggered" not in st.session_state:
        st.session_state.calculate_triggered = False

    # File upload options
    upload_option = st.radio("Upload Option", ["Individual Images", "ZIP File"])
    
    uploaded_files = []
    if upload_option == "Individual Images":
        uploaded = st.file_uploader(
            "Drag & drop images or click to upload", 
            type=["jpg", "jpeg", "png"],
            accept_multiple_files=True
        )
        if uploaded:
            logger.info(f"Uploaded {len(uploaded)} individual images")
            uploaded_files = uploaded
    elif upload_option == "ZIP File":
        zip_file = st.file_uploader("Upload a ZIP file", type=["zip"])
        if zip_file:
            with zipfile.ZipFile(zip_file, 'r') as z:
                z.extractall("temp_uploaded")
                for file_name in z.namelist():
                    if file_name.lower().endswith(('.jpg', '.jpeg', '.png')):
                        uploaded_files.append(os.path.join("temp_uploaded", file_name))
            logger.info(f"Extracted {len(uploaded_files)} images from ZIP")

    # Limit to 10 images
    uploaded_files = uploaded_files[:10]

    if uploaded_files:
        # Choose criterion
        criterion = st.sidebar.selectbox(
            "Sort by", 
            ["Composite Score", "Sharpness", "Noise (low better)", "Brightness", "Contrast", "Saturation", "Composition"],
            index=0
        )

        # Custom weights for composite score
        st.sidebar.subheader("Adjust Weights for Composite Score")
        st.session_state.weights["sharpness"] = st.sidebar.slider(
            "Sharpness Weight", 0.0, 1.0, st.session_state.weights["sharpness"], step=0.05
        )
        st.session_state.weights["noise"] = st.sidebar.slider(
            "Noise Weight", -1.0, 0.0, st.session_state.weights["noise"], step=0.05
        )
        st.session_state.weights["brightness"] = st.sidebar.slider(
            "Brightness Weight", 0.0, 1.0, st.session_state.weights["brightness"], step=0.05
        )
        st.session_state.weights["contrast"] = st.sidebar.slider(
            "Contrast Weight", 0.0, 1.0, st.session_state.weights["contrast"], step=0.05
        )
        st.session_state.weights["saturation"] = st.sidebar.slider(
            "Saturation Weight", 0.0, 1.0, st.session_state.weights["saturation"], step=0.05
        )
        st.session_state.weights["composition"] = st.sidebar.slider(
            "Composition Weight", 0.0, 1.0, st.session_state.weights["composition"], step=0.05
        )

        # Calculate button
        if st.sidebar.button("Calculate Composite Score"):
            # Normalize positive weights
            total_positive = sum([w for k, w in st.session_state.weights.items() if k != "noise"])
            if total_positive > 0:
                normalized_weights = st.session_state.weights.copy()
                for k in normalized_weights:
                    if k != "noise":
                        normalized_weights[k] /= total_positive
                st.session_state.weights = normalized_weights
            else:
                st.session_state.weights = {
                    "sharpness": 0.25,
                    "noise": -0.2,
                    "brightness": 0.2,
                    "contrast": 0.2,
                    "saturation": 0.15,
                    "composition": 0.2
                }
                st.sidebar.warning("Positive weights sum to 0. Using default weights.")
            st.session_state.calculate_triggered = True
            logger.info(f"Composite score calculation triggered with weights: {st.session_state.weights}")

        # Progress bar
        progress = st.progress(0)
        results = []
        total = len(uploaded_files)
        logger.info(f"Starting processing for {total} images")

        weights = st.session_state.weights if st.session_state.calculate_triggered else None
        for i, file in enumerate(uploaded_files):
            result = process_image(file, weights, os.path.basename(file) if isinstance(file, str) else None)
            if result is not None:
                results.append(result)
            progress.progress((i + 1) / total)
            logger.info(f"Processed image {i + 1}/{total}")

        if results:
            # Map criterion label to key
            key_map = {
                "Composite Score": "composite",
                "Sharpness": "sharpness",
                "Noise (low better)": "noise",
                "Brightness": "brightness",
                "Contrast": "contrast",
                "Saturation": "saturation",
                "Composition": "composition"
            }
            key = key_map[criterion]

            # Check if sorting by composite score is valid
            if key == "composite" and not st.session_state.calculate_triggered:
                st.error("Please click 'Calculate Composite Score' before sorting by Composite Score.")
                logger.warning("Attempted to sort by composite score without calculation")
                st.stop()

            reverse = False if key == "noise" else True
            # Sort
            results.sort(key=lambda x: x["metrics"].get(key, 0), reverse=reverse)

            # Display ranking explanation
            st.markdown("**Metric ranges (0–100)**: Sharpness, Brightness, Contrast, Saturation, Composition; Noise inverted so lower noise → higher score.")

            # Define top_n before using it
            top_n = min(3, len(results))

            # Top dynamic
            st.subheader(f"🏆 Top {top_n} Shot{'s' if top_n > 1 else ''} by {criterion}")
            cols = st.columns(top_n)
            for idx in range(top_n):
                res = results[idx]
                with cols[idx]:
                    st.image(res["image"], width=300, caption=f"{idx + 1}. {res['name']}")
                    st.metric("Score", f"{res['metrics'].get(key, 0):.2f}")

            # Download buttons (CSV and ZIP)
            st.markdown("---")
            download_cols = st.columns(2)
            with download_cols[0]:
                csv = pd.DataFrame([
                    {**{"name": r["name"]}, **r["metrics"]} for r in results
                ]).to_csv(index=False)
                st.download_button(
                    label="Download Metrics as CSV",
                    data=csv,
                    file_name="image_metrics.csv",
                    mime="text/csv"
                )
            with download_cols[1]:
                if top_n > 0:
                    zip_buffer = create_zip(results[:top_n])
                    st.download_button(
                        label=f"Download Top {top_n} Images as ZIP",
                        data=zip_buffer,
                        file_name="top_images.zip",
                        mime="application/zip"
                    )

            st.markdown("---")
            st.subheader("All Results (expand for details)")
            for res in results:
                with st.expander(f"{res['name']} — {criterion}: {res['metrics'].get(key, 0):.2f}"):
                    st.image(res["image"], width=300)
                    m = res['metrics']
                    if "composite" in m:
                        st.markdown(f"**🏅 Composite Score: {m['composite']:.2f}**")
                    st.write(f"🔪 Sharpness: {m['sharpness']:.2f}")
                    st.write(f"🌙 Noise: {m['noise']:.2f}")
                    st.write(f"💡 Brightness: {m['brightness']:.2f}")
                    st.write(f"⚫ Contrast: {m['contrast']:.2f}")
                    st.write(f"🎨 Saturation: {m['saturation']:.2f}")
                    st.write(f"🖼️ Composition: {m['composition']:.2f}")
                    # Display EXIF data
                    if res["exif"]:
                        st.subheader("EXIF Metadata")
                        for tag, value in res["exif"].items():
                            if tag == "ExposureTime":
                                st.write(f"📷 Exposure Time: {value} s")
                            elif tag == "ISOSpeedRatings":
                                st.write(f"🔆 ISO: {value}")
                            elif tag == "FNumber":
                                st.write(f"🔲 Aperture: f/{value}")
                            elif tag == "FocalLength":
                                st.write(f"📏 Focal Length: {value} mm")
                    else:
                        st.write("ℹ️ No EXIF metadata available")
        else:
            st.error("No images were processed successfully. Check the console for errors or try different images.")

    # Clean up temp_uploaded folder
    if os.path.exists("temp_uploaded"):
        shutil.rmtree("temp_uploaded")
        os.makedirs("temp_uploaded")

elif mode == "About":
    st.title("About this Tool")
    st.markdown(
        """
        **Best Shot Finder** helps photographers pick the best photo using normalized metrics (0–100):
        
        - **Sharpness**: clarity of edges (higher better)
        - **Noise**: image grain (lower better, inverted)
        - **Brightness**: overall light level
        - **Contrast**: difference between dark & light
        - **Saturation**: color vividness
        - **Composition**: adherence to rule of thirds (higher better)
        - **Composite Score**: weighted sum of metrics
        
        **How ranking works:**
        1. Each metric normalized to 0–100.
        2. Noise is inverted so low noise → high score.
        3. Composite = weighted sum of metrics, scaled to 0–100.
        4. Sort by chosen metric.

        EXIF orientation is auto-corrected, and metadata like exposure time, ISO, aperture, and focal length are displayed.
        """
    )
    st.write("Created by Silvio Thomi, 2025")
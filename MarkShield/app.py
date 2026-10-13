"""
MarkShield - Hybrid Digital Watermarking and Steganography Web Application
-------------------------------------------------------------------------
Built with Python and Streamlit.

Tabs:
1. Protect & Embed: Hide AES-256 encrypted payload and DWT-SVD watermark logo into cover image.
2. Extract & Authenticate: Decrypt secret text payload and recover copyright watermark logo.
3. Robustness & Attack Test Suite: Live attack simulation with quantitative metrics (PSNR, SSIM, NC, BER).
"""

import os
import json
import base64
import pickle
import numpy as np
import cv2
from PIL import Image
import streamlit as st
import matplotlib.pyplot as plt

# Import MarkShield Core Modules
from core.stego_engine import hide_payload, extract_payload
from core.watermark_engine import embed_watermark, extract_watermark
from core.attack_simulator import apply_attack
from core.metrics import calculate_metrics, calculate_psnr, calculate_ssim, calculate_nc, calculate_ber

# Page Config
st.set_page_config(
    page_title="MarkShield - Hybrid Watermarking & Steganography",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 800;
        background: linear-gradient(90deg, #1E88E5 0%, #43A047 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #555555;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background-color: #f8f9fa;
        border-radius: 8px;
        padding: 12px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        border-left: 4px solid #1E88E5;
    }
    </style>
""", unsafe_allow_html=True)


def serialize_wm_key(wm_key: dict) -> str:
    """Serialize watermark key dictionary to base64 string for download."""
    # Convert numpy arrays to lists for JSON serialization
    serialized = {}
    for k, v in wm_key.items():
        if isinstance(v, np.ndarray):
            serialized[k] = {"__ndarray__": v.tolist(), "dtype": str(v.dtype)}
        elif isinstance(v, (np.generic, np.float64, np.float32, np.int64, np.int32)):
            serialized[k] = v.item()
        elif isinstance(v, tuple):
            serialized[k] = list(v)
        else:
            serialized[k] = v
    json_str = json.dumps(serialized)
    return base64.b64encode(json_str.encode("utf-8")).decode("utf-8")


def deserialize_wm_key(b64_str: str) -> dict:
    """Deserialize base64 string back to watermark key dictionary."""
    json_str = base64.b64decode(b64_str.encode("utf-8")).decode("utf-8")
    data = json.loads(json_str)
    wm_key = {}
    for k, v in data.items():
        if isinstance(v, dict) and "__ndarray__" in v:
            wm_key[k] = np.array(v["__ndarray__"], dtype=np.dtype(v["dtype"]))
        elif k in ("logo_orig_shape", "band_shape"):
            wm_key[k] = tuple(v)
        else:
            wm_key[k] = v
    return wm_key


def load_image_from_upload(uploaded_file) -> np.ndarray:
    """Read uploaded file into uint8 RGB numpy array."""
    file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
    bgr_img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
    return cv2.cvtColor(bgr_img, cv2.COLOR_BGR2RGB)


def load_sample_assets():
    """Load default sample cover and logo assets if available."""
    assets_dir = os.path.join(os.path.dirname(__file__), "assets")
    cover_path = os.path.join(assets_dir, "cover_sample.png")
    logo_path = os.path.join(assets_dir, "logo_sample.png")

    if not (os.path.exists(cover_path) and os.path.exists(logo_path)):
        from assets.generate_assets import generate_sample_cover, generate_sample_logo
        generate_sample_cover(cover_path)
        generate_sample_logo(logo_path)

    cover = cv2.cvtColor(cv2.imread(cover_path, cv2.IMREAD_COLOR), cv2.COLOR_BGR2RGB)
    logo = cv2.imread(logo_path, cv2.IMREAD_GRAYSCALE)
    return cover, logo


# --- Header ---
st.markdown('<div class="main-header">🛡️ MarkShield</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-header">Hybrid Digital Watermarking (DWT-SVD) & Steganography (AES-256 LSB) Platform</div>',
    unsafe_allow_html=True
)

# Initialize Session State
if "protected_img" not in st.session_state:
    st.session_state.protected_img = None
if "cover_img" not in st.session_state:
    st.session_state.cover_img = None
if "orig_logo" not in st.session_state:
    st.session_state.orig_logo = None
if "orig_text" not in st.session_state:
    st.session_state.orig_text = None
if "wm_key" not in st.session_state:
    st.session_state.wm_key = None
if "key_b64" not in st.session_state:
    st.session_state.key_b64 = None

# Tab Layout
tab1, tab2, tab3 = st.tabs([
    "🔒 Tab 1: Protect & Embed",
    "🔑 Tab 2: Extract & Authenticate",
    "⚡ Tab 3: Robustness & Attack Test Suite"
])

# ==========================================
# TAB 1: PROTECT & EMBED
# ==========================================
with tab1:
    st.header("Protect & Embed Hybrid Watermark")
    st.write(
        "Embed a visual copyright logo using **DWT-SVD** frequency-domain watermarking, "
        "and hide an **AES-256 encrypted payload** in pixel LSB space."
    )

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("1. Input Images")
        use_sample = st.checkbox("Use Sample Demo Assets", value=True)

        if use_sample:
            sample_cover, sample_logo = load_sample_assets()
            cover_img = sample_cover
            logo_img = sample_logo
            st.info("Loaded default demo cover (512x512) and copyright logo (128x128).")
        else:
            cover_file = st.file_uploader("Upload Cover Image (PNG/JPG)", type=["png", "jpg", "jpeg"], key="t1_cover")
            logo_file = st.file_uploader("Upload Copyright Logo Image (PNG/JPG)", type=["png", "jpg", "jpeg"], key="t1_logo")

            if cover_file is not None:
                cover_img = load_image_from_upload(cover_file)
            else:
                cover_img = None

            if logo_file is not None:
                logo_img = load_image_from_upload(logo_file)
                if len(logo_img.shape) == 3:
                    logo_img = cv2.cvtColor(logo_img, cv2.COLOR_RGB2GRAY)
            else:
                logo_img = None

        if cover_img is not None:
            st.image(cover_img, caption=f"Cover Image ({cover_img.shape[1]}x{cover_img.shape[0]})", use_container_width=True)
        if logo_img is not None:
            st.image(logo_img, caption=f"Copyright Logo ({logo_img.shape[1]}x{logo_img.shape[0]})", width=160)

    with col2:
        st.subheader("2. Secret Payload & Protection Settings")
        secret_payload = st.text_area(
            "Secret Text Payload (Steganography)",
            value="Confidential Copyright Data: Asset ID #982412-MS",
            height=100
        )
        password = st.text_input("AES-256 Encryption Password", value="MarkShield2026!", type="password")

        st.subheader("3. Watermark Parameters")
        alpha = st.slider("Watermark Strength (alpha)", min_value=0.01, max_value=0.25, value=0.05, step=0.01)
        subband = st.selectbox("DWT Subband", options=["HL", "LH", "LL", "HH"], index=0)

        embed_btn = st.button("🛡️ Embed Hybrid Protection", type="primary", use_container_width=True)

    if embed_btn:
        if cover_img is None or logo_img is None:
            st.error("Please provide both a Cover Image and a Copyright Logo Image.")
        elif not secret_payload:
            st.error("Secret text payload cannot be empty.")
        elif not password:
            st.error("AES-256 encryption password cannot be empty.")
        else:
            with st.spinner("Processing DWT-SVD Watermark & AES-256 LSB Steganography..."):
                try:
                    # Step 1: Embed DWT-SVD Watermark logo
                    wm_img, wm_key = embed_watermark(cover_img, logo_img, alpha=alpha, band=subband)

                    # Step 2: Embed AES-256 encrypted payload text into LSB
                    protected_img = hide_payload(wm_img, secret_payload, password)

                    # Store in session state
                    st.session_state.protected_img = protected_img
                    st.session_state.cover_img = cover_img
                    st.session_state.orig_logo = logo_img
                    st.session_state.orig_text = secret_payload
                    st.session_state.wm_key = wm_key
                    st.session_state.key_b64 = serialize_wm_key(wm_key)

                    st.success("✅ Hybrid Protection Embedded Successfully!")

                    res_col1, res_col2 = st.columns(2)
                    with res_col1:
                        st.image(cover_img, caption="Original Cover Image", use_container_width=True)
                    with res_col2:
                        st.image(protected_img, caption="Protected MarkShield Image", use_container_width=True)

                    # Quantitative Metrics
                    psnr_val = calculate_psnr(cover_img, protected_img)
                    ssim_val = calculate_ssim(cover_img, protected_img)

                    m1, m2 = st.columns(2)
                    m1.metric("PSNR (Peak Signal-to-Noise Ratio)", f"{psnr_val:.2f} dB", delta=">35 dB is Imperceptible")
                    m2.metric("SSIM (Structural Similarity Index)", f"{ssim_val:.4f}", delta="1.0 is Perfect")

                    # Downloads
                    st.subheader("📥 Downloads")
                    down_col1, down_col2 = st.columns(2)

                    # Convert protected image to PNG bytes
                    is_success, buffer = cv2.imencode(".png", cv2.cvtColor(protected_img, cv2.COLOR_RGB2BGR))
                    img_bytes = buffer.tobytes()

                    with down_col1:
                        st.download_button(
                            label="💾 Download Protected Image (.png)",
                            data=img_bytes,
                            file_name="markshield_protected.png",
                            mime="image/png",
                            use_container_width=True
                        )

                    with down_col2:
                        st.download_button(
                            label="🔑 Download Watermark Key File (.key)",
                            data=st.session_state.key_b64,
                            file_name="markshield_key.key",
                            mime="text/plain",
                            use_container_width=True
                        )

                except Exception as e:
                    st.error(f"Embedding failed: {str(e)}")


# ==========================================
# TAB 2: EXTRACT & AUTHENTICATE
# ==========================================
with tab2:
    st.header("Extract Secret Payload & Authenticate Copyright Logo")
    st.write("Upload a protected image, enter the AES-256 password, and load the watermark key file to extract data.")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("1. Protected Image Source")
        use_tab1_output = st.checkbox("Use Protected Image from Tab 1", value=st.session_state.protected_img is not None)

        if use_tab1_output and st.session_state.protected_img is not None:
            prot_input_img = st.session_state.protected_img
            st.info("Using protected image generated in Tab 1.")
        else:
            up_prot_file = st.file_uploader("Upload Protected Image (PNG)", type=["png"], key="t2_prot")
            if up_prot_file is not None:
                prot_input_img = load_image_from_upload(up_prot_file)
            else:
                prot_input_img = None

        if prot_input_img is not None:
            st.image(prot_input_img, caption="Protected Image", use_container_width=True)

    with col2:
        st.subheader("2. Authentication Credentials")
        decrypt_password = st.text_input("AES-256 Decryption Password", value="MarkShield2026!", type="password", key="t2_pass")

        key_source = st.radio("Watermark Key Source", options=["Key from Tab 1 Session", "Upload Key File"], index=0 if st.session_state.wm_key is not None else 1)

        key_to_use = None
        if key_source == "Key from Tab 1 Session" and st.session_state.wm_key is not None:
            key_to_use = st.session_state.wm_key
            st.success("Loaded watermark key from active session.")
        else:
            key_file = st.file_uploader("Upload Key File (.key)", type=["key", "txt"], key="t2_keyfile")
            if key_file is not None:
                try:
                    b64_content = key_file.read().decode("utf-8").strip()
                    key_to_use = deserialize_wm_key(b64_content)
                    st.success("Successfully loaded uploaded key file.")
                except Exception as ex:
                    st.error(f"Failed to parse key file: {str(ex)}")

        extract_btn = st.button("🔑 Extract & Authenticate", type="primary", use_container_width=True)

    if extract_btn:
        if prot_input_img is None:
            st.error("Please provide a Protected Image.")
        elif not decrypt_password:
            st.error("Please enter the decryption password.")
        else:
            st.markdown("---")
            st.subheader("🔍 Extraction Results")

            # 1. Steganography Extraction
            st.markdown("#### 1. AES-256 Secret Payload Extraction")
            try:
                extracted_text = extract_payload(prot_input_img, decrypt_password)
                st.success(f"**Extracted Secret Payload:**\n\n```\n{extracted_text}\n```")
            except Exception as e:
                st.error(f"Steganography Extraction Failed: {str(e)}")

            # 2. Watermark Logo Extraction
            st.markdown("#### 2. DWT-SVD Watermark Logo Extraction")
            if key_to_use is None:
                st.warning("No valid watermark key provided. Skipping watermark logo extraction.")
            else:
                try:
                    extracted_logo = extract_watermark(prot_input_img, key_to_use)

                    l_col1, l_col2 = st.columns(2)
                    with l_col1:
                        st.image(extracted_logo, caption="Extracted Copyright Logo", width=200)

                    if st.session_state.orig_logo is not None:
                        with l_col2:
                            st.image(st.session_state.orig_logo, caption="Original Reference Logo", width=200)

                        nc_score = calculate_nc(st.session_state.orig_logo, extracted_logo)
                        st.metric("Normalized Cross-Correlation (NC)", f"{nc_score:.4f}", delta=">0.70 indicates valid copyright verification")

                except Exception as e:
                    st.error(f"Watermark Extraction Failed: {str(e)}")


# ==========================================
# TAB 3: ROBUSTNESS & ATTACK TEST SUITE
# ==========================================
with tab3:
    st.header("Robustness & Attack Test Suite")
    st.write("Simulate real-world image attacks (JPEG, noise, crop, brightness) and evaluate live metrics (PSNR, SSIM, NC, BER).")

    if st.session_state.protected_img is None:
        st.warning("⚠️ Please first run **Tab 1 (Protect & Embed)** to generate a protected image for testing.")
    else:
        protected_img = st.session_state.protected_img
        orig_cover = st.session_state.cover_img
        orig_logo = st.session_state.orig_logo
        orig_text = st.session_state.orig_text
        wm_key = st.session_state.wm_key

        ctrl_col, view_col = st.columns([1, 2])

        with ctrl_col:
            st.subheader("1. Attack Simulation Controls")
            attack_type = st.selectbox(
                "Select Attack Type",
                options=["jpeg", "gaussian", "salt_pepper", "crop", "brightness"],
                format_func=lambda x: {
                    "jpeg": "JPEG Compression",
                    "gaussian": "Gaussian Noise",
                    "salt_pepper": "Salt & Pepper Noise",
                    "crop": "Center Cropping",
                    "brightness": "Brightness Shift"
                }[x]
            )

            params = {}
            if attack_type == "jpeg":
                params["quality"] = st.slider("JPEG Quality Factor", min_value=10, max_value=95, value=50, step=5)
            elif attack_type == "gaussian":
                params["var"] = st.slider("Noise Variance (sigma^2)", min_value=10.0, max_value=500.0, value=100.0, step=10.0)
            elif attack_type == "salt_pepper":
                params["amount"] = st.slider("Noise Amount", min_value=0.01, max_value=0.20, value=0.05, step=0.01)
            elif attack_type == "crop":
                params["crop_pct"] = st.slider("Center Crop Percentage", min_value=0.05, max_value=0.50, value=0.20, step=0.05)
            elif attack_type == "brightness":
                params["shift"] = st.slider("Brightness Offset", min_value=-100, max_value=100, value=40, step=10)

            test_pass = st.text_input("AES Password for Extraction", value="MarkShield2026!", type="password", key="t3_pass")

        # Apply Attack
        attacked_img = apply_attack(protected_img, attack_type, params)

        with view_col:
            st.subheader("2. Visual Comparison")
            vis_col1, vis_col2 = st.columns(2)
            with vis_col1:
                st.image(protected_img, caption="Protected Image", use_container_width=True)
            with vis_col2:
                st.image(attacked_img, caption=f"Attacked Image ({attack_type})", use_container_width=True)

        st.markdown("---")
        st.subheader("3. Quantitative Robustness Metrics")

        # Evaluate Extraction under Attack
        extracted_text_att = ""
        ber_score = 1.0
        try:
            extracted_text_att = extract_payload(attacked_img, test_pass)
            ber_score = calculate_ber(orig_text, extracted_text_att)
        except Exception:
            extracted_text_att = "❌ Payload Extraction Failed (Bits Corrupted)"
            ber_score = 1.0

        extracted_logo_att = None
        nc_score = 0.0
        try:
            extracted_logo_att = extract_watermark(attacked_img, wm_key)
            if orig_logo is not None:
                nc_score = calculate_nc(orig_logo, extracted_logo_att)
        except Exception:
            nc_score = 0.0

        psnr_att = calculate_psnr(orig_cover, attacked_img)
        ssim_att = calculate_ssim(orig_cover, attacked_img)

        # Metric Cards
        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
        col_m1.metric("PSNR (Image Quality)", f"{psnr_att:.2f} dB")
        col_m2.metric("SSIM (Structural)", f"{ssim_att:.4f}")
        col_m3.metric("Logo NC (Correlation)", f"{nc_score:.4f}")
        col_m4.metric("Payload BER (Bit Error)", f"{ber_score:.4f}")

        # Display extracted logo under attack
        st.markdown("#### Recovered Watermark & Payload Under Attack")
        rec_col1, rec_col2 = st.columns(2)
        with rec_col1:
            if extracted_logo_att is not None:
                st.image(extracted_logo_att, caption=f"Extracted Logo (NC = {nc_score:.4f})", width=180)
        with rec_col2:
            st.info(f"**Extracted Secret Text:**\n\n`{extracted_text_att}`\n\nBER: **{ber_score:.4f}**")

        # Render Metrics Bar Chart
        st.markdown("#### Metric Summary Chart")
        fig, ax = plt.subplots(figsize=(8, 3))
        metric_names = ["SSIM", "NC (Logo)", "1 - BER (Stego)"]
        metric_values = [ssim_att, nc_score, 1.0 - ber_score]
        colors = ["#1E88E5", "#43A047", "#FB8C00"]

        bars = ax.bar(metric_names, metric_values, color=colors, width=0.5)
        ax.set_ylim(0, 1.1)
        ax.set_ylabel("Score (0.0 to 1.0)")
        ax.set_title("Performance & Robustness Scores under Attack")

        for bar in bars:
            height = bar.get_height()
            ax.annotate(f"{height:.4f}",
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 3),  # 3 points vertical offset
                        textcoords="offset points",
                        ha='center', va='bottom')

        st.pyplot(fig)

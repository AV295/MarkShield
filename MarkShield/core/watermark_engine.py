"""
MarkShield Digital Watermarking Engine
--------------------------------------
DWT-SVD (Discrete Wavelet Transform & Singular Value Decomposition) domain
watermarking for embedding and extracting visual copyright logos into image frequency bands.

Mathematical Overview:
1. Cover image channel transformed using 2D DWT (Haar wavelet) into subbands (LL, LH, HL, HH).
2. SVD applied to target subband (HL): A = U_A * S_A * V_A^T.
3. Copyright logo embedded into singular values / domain matrix: M = diag(S_A) + alpha * W.
4. SVD applied to modified matrix M: M = U_M * S_M * V_M^T.
5. Watermarked subband formed: B_wm = U_A * diag(S_M) * V_A^T.
6. Inverse DWT yields watermarked image.
7. Extraction uses saved orthogonal matrices (U_M, V_M^T) and S_A to reconstruct extracted logo.
"""

import numpy as np
import cv2
import pywt
from typing import Tuple, Dict, Any


def preprocess_logo(logo_img: np.ndarray, target_shape: Tuple[int, int]) -> np.ndarray:
    """Resize and normalize logo image to match target subband shape."""
    if len(logo_img.shape) == 3:
        logo_gray = cv2.cvtColor(logo_img, cv2.COLOR_BGR2GRAY)
    else:
        logo_gray = logo_img.copy()

    resized_logo = cv2.resize(logo_gray, (target_shape[1], target_shape[0]), interpolation=cv2.INTER_AREA)
    # Normalize logo to range [0, 1]
    normalized_logo = resized_logo.astype(np.float64) / 255.0
    return normalized_logo


def embed_watermark(
    cover_image: np.ndarray,
    logo_image: np.ndarray,
    alpha: float = 0.05,
    wavelet: str = "haar",
    band: str = "HL"
) -> Tuple[np.ndarray, Dict[str, Any]]:
    """
    Embed visual logo into cover image using DWT-SVD watermarking.

    Args:
        cover_image: Input RGB cover image (uint8, HxWxC).
        logo_image: Input copyright logo image (uint8, HxW or HxWxC).
        alpha: Embedding strength factor (typically 0.01 to 0.2).
        wavelet: Wavelet family for 2D DWT (default 'haar').
        band: Subband choice ('LL', 'LH', 'HL', 'HH').

    Returns:
        Tuple containing:
        - Watermarked RGB image (uint8 array).
        - Watermark key dictionary required for extraction.
    """
    if cover_image is None or logo_image is None:
        raise ValueError("Cover image and logo image cannot be None.")

    # Convert cover image to YCrCb space for robust luminance processing
    has_color = len(cover_image.shape) == 3 and cover_image.shape[2] == 3
    if has_color:
        ycrcb = cv2.cvtColor(cover_image, cv2.COLOR_RGB2YCrCb)
        channel = ycrcb[:, :, 0].astype(np.float64)
    else:
        channel = cover_image.astype(np.float64)

    # 1. Apply 2D DWT
    coeffs = pywt.dwt2(channel, wavelet)
    LL, (LH, HL, HH) = coeffs

    subband_dict = {"LL": LL, "LH": LH, "HL": HL, "HH": HH}
    if band not in subband_dict:
        raise ValueError(f"Invalid subband '{band}'. Must be one of LL, LH, HL, HH.")

    target_band = subband_dict[band]
    band_shape = target_band.shape

    # 2. Preprocess logo
    norm_logo = preprocess_logo(logo_image, band_shape)

    # 3. Apply SVD on target subband
    U_A, S_A, V_A_T = np.linalg.svd(target_band, full_matrices=False)

    # 4. Form S_matrix and embed logo
    S_matrix = np.diag(S_A)
    M = S_matrix + alpha * norm_logo

    # 5. Apply SVD on modified matrix M
    U_M, S_M, V_M_T = np.linalg.svd(M, full_matrices=False)

    # 6. Reconstruct watermarked subband
    watermarked_subband = U_A @ np.diag(S_M) @ V_A_T

    # Update coefficients
    subband_dict[band] = watermarked_subband
    new_coeffs = (subband_dict["LL"], (subband_dict["LH"], subband_dict["HL"], subband_dict["HH"]))

    # 7. Apply Inverse 2D DWT
    watermarked_channel = pywt.idwt2(new_coeffs, wavelet)

    # Match original channel dimensions if pywt produced off-by-one padding
    h, w = channel.shape
    watermarked_channel = watermarked_channel[:h, :w]
    watermarked_channel = np.clip(watermarked_channel, 0, 255)

    if has_color:
        ycrcb[:, :, 0] = np.uint8(watermarked_channel)
        watermarked_img = cv2.cvtColor(ycrcb, cv2.COLOR_YCrCb2RGB)
    else:
        watermarked_img = np.uint8(watermarked_channel)

    # Key dictionary containing matrices needed for non-blind/semi-blind extraction
    wm_key = {
        "U_M": U_M,
        "V_M_T": V_M_T,
        "S_A": S_A,
        "alpha": alpha,
        "logo_orig_shape": logo_image.shape[:2],
        "band_shape": band_shape,
        "wavelet": wavelet,
        "band": band,
        "has_color": has_color,
    }

    return watermarked_img, wm_key


def extract_watermark(
    watermarked_image: np.ndarray,
    wm_key: Dict[str, Any]
) -> np.ndarray:
    """
    Extract copyright logo from watermarked (or attacked) image using DWT-SVD.

    Args:
        watermarked_image: Watermarked or attacked image array (uint8).
        wm_key: Key metadata dictionary generated during embedding.

    Returns:
        Extracted visual logo image (uint8 grayscale, range [0, 255]).
    """
    if watermarked_image is None or not wm_key:
        raise ValueError("Invalid input image or key dictionary.")

    U_M = wm_key["U_M"]
    V_M_T = wm_key["V_M_T"]
    S_A = wm_key["S_A"]
    alpha = wm_key["alpha"]
    wavelet = wm_key.get("wavelet", "haar")
    band = wm_key.get("band", "HL")
    logo_orig_shape = wm_key["logo_orig_shape"]

    has_color = len(watermarked_image.shape) == 3 and watermarked_image.shape[2] == 3
    if has_color:
        ycrcb = cv2.cvtColor(watermarked_image, cv2.COLOR_RGB2YCrCb)
        channel = ycrcb[:, :, 0].astype(np.float64)
    else:
        channel = watermarked_image.astype(np.float64)

    # 1. Apply 2D DWT on watermarked/attacked image
    coeffs = pywt.dwt2(channel, wavelet)
    LL, (LH, HL, HH) = coeffs

    subband_dict = {"LL": LL, "LH": LH, "HL": HL, "HH": HH}
    target_band = subband_dict[band]

    # Ensure shape matches expected band shape from key
    expected_shape = wm_key["band_shape"]
    if target_band.shape != expected_shape:
        target_band = cv2.resize(target_band, (expected_shape[1], expected_shape[0]))

    # 2. Apply SVD on attacked subband
    _, S_Y, _ = np.linalg.svd(target_band, full_matrices=False)

    # Reconstruct matrix S_Y matrix
    min_dim = min(len(S_Y), len(S_A))
    S_Y_matrix = np.diag(S_Y[:min_dim])

    # 3. Reconstruct M_ext = U_M @ S_Y_matrix @ V_M_T
    # Match matrix dimensions if needed
    if U_M.shape[1] != S_Y_matrix.shape[0]:
        U_M_sub = U_M[:S_Y_matrix.shape[0], :S_Y_matrix.shape[0]]
        V_M_T_sub = V_M_T[:S_Y_matrix.shape[0], :S_Y_matrix.shape[0]]
    else:
        U_M_sub = U_M
        V_M_T_sub = V_M_T

    M_ext = U_M_sub @ S_Y_matrix @ V_M_T_sub

    # 4. Extract raw normalized logo matrix: W_ext = (M_ext - diag(S_A)) / alpha
    S_A_matrix = np.diag(S_A[:min_dim])
    if M_ext.shape != S_A_matrix.shape:
        M_ext = cv2.resize(M_ext, (S_A_matrix.shape[1], S_A_matrix.shape[0]))

    raw_logo = (M_ext - S_A_matrix) / alpha

    # 5. Normalize extracted logo matrix to [0, 255] uint8
    raw_logo = np.clip(raw_logo * 255.0, 0, 255)
    extracted_logo = raw_logo.astype(np.uint8)

    # Resize back to original logo aspect ratio / resolution
    if extracted_logo.shape != logo_orig_shape:
        extracted_logo = cv2.resize(extracted_logo, (logo_orig_shape[1], logo_orig_shape[0]), interpolation=cv2.INTER_CUBIC)

    return extracted_logo

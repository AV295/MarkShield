"""
MarkShield Quantitative Metrics Module
--------------------------------------
Calculates image degradation and watermark/payload recovery quality metrics:
- PSNR: Peak Signal-to-Noise Ratio (dB)
- SSIM: Structural Similarity Index Measure (0.0 to 1.0)
- NC: Normalized Cross-Correlation for logo fidelity (0.0 to 1.0)
- BER: Bit Error Rate for stego message accuracy (0.0 to 1.0)
"""

import numpy as np
from skimage.metrics import peak_signal_noise_ratio, structural_similarity
from typing import Dict, Union, Tuple


def calculate_psnr(original: np.ndarray, modified: np.ndarray) -> float:
    """
    Calculate Peak Signal-to-Noise Ratio (PSNR) in decibels (dB).

    Args:
        original: Reference image numpy array (uint8).
        modified: Test/Modified image numpy array (uint8).

    Returns:
        PSNR value in dB (higher is better; >35 dB indicates imperceptible change).
    """
    if original.shape != modified.shape:
        raise ValueError(f"Shape mismatch for PSNR calculation: {original.shape} vs {modified.shape}")

    # Check for exact equality
    if np.array_equal(original, modified):
        return 100.0  # Perfect match convention

    mse = np.mean((original.astype(np.float64) - modified.astype(np.float64)) ** 2)
    if mse == 0:
        return 100.0

    psnr_val = peak_signal_noise_ratio(original, modified, data_range=255)
    return float(psnr_val)


def calculate_ssim(original: np.ndarray, modified: np.ndarray) -> float:
    """
    Calculate Structural Similarity Index Measure (SSIM).

    Args:
        original: Reference image numpy array (uint8).
        modified: Test/Modified image numpy array (uint8).

    Returns:
        SSIM index between 0.0 (no similarity) and 1.0 (identical).
    """
    if original.shape != modified.shape:
        raise ValueError(f"Shape mismatch for SSIM calculation: {original.shape} vs {modified.shape}")

    if np.array_equal(original, modified):
        return 1.0

    has_color = len(original.shape) == 3 and original.shape[2] == 3
    if has_color:
        ssim_val = structural_similarity(original, modified, channel_axis=2, data_range=255)
    else:
        ssim_val = structural_similarity(original, modified, data_range=255)

    return float(ssim_val)


def calculate_nc(original_logo: np.ndarray, extracted_logo: np.ndarray) -> float:
    """
    Calculate Normalized Cross-Correlation (NC) between original and extracted logos.

    Args:
        original_logo: Original watermark logo (uint8 or float).
        extracted_logo: Extracted watermark logo (uint8 or float).

    Returns:
        NC score between 0.0 and 1.0.
    """
    import cv2

    # Resize extracted logo to match original shape if needed
    if original_logo.shape != extracted_logo.shape:
        h, w = original_logo.shape[:2]
        extracted_logo = cv2.resize(extracted_logo, (w, h))

    orig_f = original_logo.astype(np.float64).ravel()
    extr_f = extracted_logo.astype(np.float64).ravel()

    numerator = np.sum(orig_f * extr_f)
    denominator = np.sqrt(np.sum(orig_f ** 2)) * np.sqrt(np.sum(extr_f ** 2))

    if denominator == 0:
        return 0.0

    nc_score = numerator / denominator
    return float(np.clip(nc_score, 0.0, 1.0))


def calculate_ber(original_text: str, extracted_text: str) -> float:
    """
    Calculate Bit Error Rate (BER) between original and extracted stego payload text.

    Args:
        original_text: Original secret payload text string.
        extracted_text: Extracted payload text string.

    Returns:
        BER ratio (0.0 = 0% bit errors / perfect match, 1.0 = 100% bit error).
    """
    orig_bytes = original_text.encode("utf-8")
    extr_bytes = extracted_text.encode("utf-8")

    orig_bits = np.unpackbits(np.frombuffer(orig_bytes, dtype=np.uint8))
    extr_bits = np.unpackbits(np.frombuffer(extr_bytes, dtype=np.uint8))

    max_len = max(len(orig_bits), len(extr_bits))
    if max_len == 0:
        return 0.0

    # Pad shorter bit vector with zeros for length mismatch
    if len(orig_bits) < max_len:
        orig_bits = np.pad(orig_bits, (0, max_len - len(orig_bits)), mode="constant")
    if len(extr_bits) < max_len:
        extr_bits = np.pad(extr_bits, (0, max_len - len(extr_bits)), mode="constant")

    error_bits = np.sum(orig_bits != extr_bits)
    return float(error_bits / max_len)


def calculate_metrics(
    cover_image: np.ndarray,
    protected_image: np.ndarray,
    orig_logo: np.ndarray = None,
    extr_logo: np.ndarray = None,
    orig_text: str = None,
    extr_text: str = None
) -> Dict[str, float]:
    """
    Calculate combined suite of metrics (PSNR, SSIM, NC, BER).

    Returns:
        Dictionary containing metric values.
    """
    results = {
        "PSNR": calculate_psnr(cover_image, protected_image),
        "SSIM": calculate_ssim(cover_image, protected_image),
    }

    if orig_logo is not None and extr_logo is not None:
        results["NC"] = calculate_nc(orig_logo, extr_logo)
    else:
        results["NC"] = 0.0

    if orig_text is not None and extr_text is not None:
        results["BER"] = calculate_ber(orig_text, extr_text)
    else:
        results["BER"] = 0.0

    return results

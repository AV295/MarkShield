"""
MarkShield Core Modules
-----------------------
Hybrid Digital Watermarking and Steganography Engine components:
- stego_engine: AES-256 encrypted payload hiding and extraction in LSB/image pixels.
- watermark_engine: DWT-SVD domain visual copyright logo embedding and extraction.
- attack_simulator: Simulated real-world attacks (JPEG, noise, crop, brightness).
- metrics: Quantitative quality and robustness metrics (PSNR, SSIM, NC, BER).
"""

from .stego_engine import hide_payload, extract_payload
from .watermark_engine import embed_watermark, extract_watermark
from .attack_simulator import apply_attack
from .metrics import calculate_metrics, calculate_psnr, calculate_ssim, calculate_nc, calculate_ber

__all__ = [
    "hide_payload",
    "extract_payload",
    "embed_watermark",
    "extract_watermark",
    "apply_attack",
    "calculate_metrics",
    "calculate_psnr",
    "calculate_ssim",
    "calculate_nc",
    "calculate_ber",
]

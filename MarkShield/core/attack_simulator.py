"""
MarkShield Attack Simulator Module
----------------------------------
Simulates common digital image attacks and degradation pipelines:
- JPEG Compression (variable quality factor)
- Gaussian Noise addition
- Salt & Pepper Noise
- Center Cropping (masking / occlusion)
- Brightness Adjustment / Shift
"""

import cv2
import numpy as np
from typing import Dict, Any


def attack_jpeg_compression(image: np.ndarray, quality: int = 50) -> np.ndarray:
    """
    Apply lossy JPEG compression attack.

    Args:
        image: RGB or grayscale image array (uint8).
        quality: JPEG compression quality factor (1-100). Lower means heavier compression.
    """
    quality = max(1, min(100, int(quality)))
    # Convert RGB to BGR for OpenCV encoding
    if len(image.shape) == 3 and image.shape[2] == 3:
        bgr = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), quality]
        result, encimg = cv2.imencode(".jpg", bgr, encode_param)
        decoded_bgr = cv2.imdecode(encimg, cv2.IMREAD_COLOR)
        return cv2.cvtColor(decoded_bgr, cv2.COLOR_BGR2RGB)
    else:
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), quality]
        result, encimg = cv2.imencode(".jpg", image, encode_param)
        return cv2.imdecode(encimg, cv2.IMREAD_GRAYSCALE)


def attack_gaussian_noise(image: np.ndarray, mean: float = 0.0, var: float = 100.0) -> np.ndarray:
    """
    Add zero-mean Gaussian noise.

    Args:
        image: Input image array (uint8).
        mean: Gaussian noise mean.
        var: Variance of Gaussian noise (std = sqrt(var)).
    """
    sigma = np.sqrt(max(0.1, var))
    gauss = np.random.normal(mean, sigma, image.shape)
    noisy = image.astype(np.float64) + gauss
    return np.clip(noisy, 0, 255).astype(np.uint8)


def attack_salt_and_pepper(image: np.ndarray, amount: float = 0.05) -> np.ndarray:
    """
    Add Salt-and-Pepper impulsive noise.

    Args:
        image: Input image array (uint8).
        amount: Proportion of image pixels affected (0.0 to 1.0).
    """
    amount = max(0.0, min(1.0, float(amount)))
    noisy = image.copy()
    num_salt = np.ceil(amount * image.size * 0.5)
    num_pepper = np.ceil(amount * image.size * 0.5)

    # Add Salt noise (255)
    coords = [np.random.randint(0, i - 1, int(num_salt)) for i in image.shape]
    noisy[tuple(coords)] = 255

    # Add Pepper noise (0)
    coords = [np.random.randint(0, i - 1, int(num_pepper)) for i in image.shape]
    noisy[tuple(coords)] = 0

    return noisy


def attack_center_crop(image: np.ndarray, crop_pct: float = 0.25) -> np.ndarray:
    """
    Apply center cropping / central region occlusion attack.

    Args:
        image: Input image array (uint8).
        crop_pct: Percentage of dimensions to zero out in center (0.0 to 0.9).
    """
    crop_pct = max(0.0, min(0.9, float(crop_pct)))
    if crop_pct == 0.0:
        return image.copy()

    h, w = image.shape[:2]
    ch = int(h * crop_pct)
    cw = int(w * crop_pct)

    start_h = (h - ch) // 2
    start_w = (w - cw) // 2

    attacked = image.copy()
    if len(image.shape) == 3:
        attacked[start_h:start_h + ch, start_w:start_w + cw, :] = 0
    else:
        attacked[start_h:start_h + ch, start_w:start_w + cw] = 0

    return attacked


def attack_brightness(image: np.ndarray, shift: int = 30) -> np.ndarray:
    """
    Shift image brightness.

    Args:
        image: Input image array (uint8).
        shift: Brightness offset (-255 to +255).
    """
    shifted = image.astype(np.float64) + shift
    return np.clip(shifted, 0, 255).astype(np.uint8)


def apply_attack(image: np.ndarray, attack_type: str, params: Dict[str, Any] = None) -> np.ndarray:
    """
    General entrypoint to apply a simulated attack to an image.

    Supported attack_type values:
    - 'jpeg': JPEG compression (params: 'quality' int 1-100)
    - 'gaussian': Gaussian noise (params: 'var' float > 0)
    - 'salt_pepper': Salt & Pepper noise (params: 'amount' float 0-1)
    - 'crop': Center crop (params: 'crop_pct' float 0-0.9)
    - 'brightness': Brightness shift (params: 'shift' int -255 to 255)
    - 'none': Returns copy of image unaltered.
    """
    if params is None:
        params = {}

    if attack_type == "jpeg":
        return attack_jpeg_compression(image, quality=params.get("quality", 50))
    elif attack_type == "gaussian":
        return attack_gaussian_noise(image, mean=params.get("mean", 0.0), var=params.get("var", 100.0))
    elif attack_type == "salt_pepper":
        return attack_salt_and_pepper(image, amount=params.get("amount", 0.05))
    elif attack_type == "crop":
        return attack_center_crop(image, crop_pct=params.get("crop_pct", 0.25))
    elif attack_type == "brightness":
        return attack_brightness(image, shift=params.get("shift", 30))
    elif attack_type in ("none", "", None):
        return image.copy()
    else:
        raise ValueError(f"Unknown attack type: '{attack_type}'")

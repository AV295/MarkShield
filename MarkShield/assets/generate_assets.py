"""
MarkShield Sample Asset Generator
---------------------------------
Generates sample cover images and copyright logo assets for quick demo and testing.
"""

import os
import cv2
import numpy as np


def generate_sample_cover(filepath: str, width: int = 512, height: int = 512):
    """Generate a vibrant multi-color gradient & geometric test cover image."""
    x = np.linspace(0, 1, width)
    y = np.linspace(0, 1, height)
    xx, yy = np.meshgrid(x, y)

    # Vibrant color channels
    r = np.uint8(255 * (0.5 + 0.5 * np.sin(2 * np.pi * xx + 0)))
    g = np.uint8(255 * (0.5 + 0.5 * np.cos(2 * np.pi * yy + 2)))
    b = np.uint8(255 * (0.5 + 0.5 * np.sin(2 * np.pi * (xx + yy) + 4)))

    img = np.dstack((r, g, b))

    # Add geometric overlay shapes
    cv2.circle(img, (width // 2, height // 2), 120, (255, 255, 255), 4)
    cv2.rectangle(img, (60, 60), (width - 60, height - 60), (0, 255, 200), 3)
    cv2.putText(
        img, "MARKSHIELD COVER", (width // 2 - 140, height // 2 + 10),
        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2, cv2.LINE_AA
    )

    # Save as PNG
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    cv2.imwrite(filepath, cv2.cvtColor(img, cv2.COLOR_RGB2BGR))
    print(f"Generated sample cover image at: {filepath}")


def generate_sample_logo(filepath: str, width: int = 128, height: int = 128):
    """Generate a clear copyright logo graphic."""
    logo = np.zeros((height, width), dtype=np.uint8)

    # Shield polygon outline
    points = np.array([
        [width // 2, 10],
        [width - 15, 30],
        [width - 25, height - 35],
        [width // 2, height - 10],
        [25, height - 35],
        [15, 30]
    ], np.int32)

    cv2.fillPoly(logo, [points], 200)
    cv2.polylines(logo, [points], True, 255, 3)

    # Copyright symbol & text
    cv2.putText(
        logo, "COPYRIGHT", (18, height // 2 - 5),
        cv2.FONT_HERSHEY_SIMPLEX, 0.35, 255, 1, cv2.LINE_AA
    )
    cv2.putText(
        logo, "(C) 2026", (32, height // 2 + 18),
        cv2.FONT_HERSHEY_SIMPLEX, 0.35, 255, 1, cv2.LINE_AA
    )

    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    cv2.imwrite(filepath, logo)
    print(f"Generated sample logo image at: {filepath}")


if __name__ == "__main__":
    assets_dir = os.path.dirname(os.path.abspath(__file__))
    generate_sample_cover(os.path.join(assets_dir, "cover_sample.png"))
    generate_sample_logo(os.path.join(assets_dir, "logo_sample.png"))

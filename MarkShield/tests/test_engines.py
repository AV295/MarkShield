"""
MarkShield Test Suite
---------------------
Standard Python unittest suite verifying core steganography, digital watermarking,
attack simulator, and quantitative metric evaluation engines.
"""

import unittest
import numpy as np
import cv2

from core.stego_engine import hide_payload, extract_payload, encrypt_payload, decrypt_payload
from core.watermark_engine import embed_watermark, extract_watermark
from core.attack_simulator import (
    apply_attack,
    attack_jpeg_compression,
    attack_gaussian_noise,
    attack_salt_and_pepper,
    attack_center_crop,
    attack_brightness
)
from core.metrics import (
    calculate_psnr,
    calculate_ssim,
    calculate_nc,
    calculate_ber,
    calculate_metrics
)


class TestStegoEngine(unittest.TestCase):
    """Test cases for AES-256 LSB steganography engine."""

    def setUp(self):
        # Create synthetic RGB image (128x128x3)
        np.random.seed(42)
        self.cover_img = np.random.randint(0, 256, (128, 128, 3), dtype=np.uint8)
        self.secret_text = "MarkShield Top Secret Payload 2026! @#$"
        self.password = "SecurePassword123!"

    def test_encrypt_decrypt_payload(self):
        """Test AES-256 encryption and decryption functions directly."""
        encrypted_packet = encrypt_payload(self.secret_text, self.password)
        decrypted_text = decrypt_payload(encrypted_packet, self.password)
        self.assertEqual(decrypted_text, self.secret_text)

    def test_encrypt_decrypt_wrong_password(self):
        """Test AES-256 decryption failure with incorrect password."""
        encrypted_packet = encrypt_payload(self.secret_text, self.password)
        with self.assertRaises(ValueError):
            decrypt_payload(encrypted_packet, "WrongPassword")

    def test_stego_embed_and_extract(self):
        """Test embedding secret text into image and successful extraction."""
        stego_img = hide_payload(self.cover_img, self.secret_text, self.password)
        self.assertEqual(stego_img.shape, self.cover_img.shape)
        self.assertEqual(stego_img.dtype, np.uint8)

        extracted_text = extract_payload(stego_img, self.password)
        self.assertEqual(extracted_text, self.secret_text)

    def test_stego_wrong_password(self):
        """Test stego extraction failure when user supplies incorrect password."""
        stego_img = hide_payload(self.cover_img, self.secret_text, self.password)
        with self.assertRaises(ValueError):
            extract_payload(stego_img, "WrongPassword999")

    def test_stego_non_stego_image(self):
        """Test stego extraction failure on clean image without payload."""
        with self.assertRaises(ValueError):
            extract_payload(self.cover_img, self.password)


class TestWatermarkEngine(unittest.TestCase):
    """Test cases for DWT-SVD digital watermarking engine."""

    def setUp(self):
        np.random.seed(42)
        # Cover image (256x256 RGB)
        self.cover_img = np.random.randint(50, 200, (256, 256, 3), dtype=np.uint8)
        # Logo image (64x64 Grayscale)
        self.logo_img = np.zeros((64, 64), dtype=np.uint8)
        cv2.circle(self.logo_img, (32, 32), 20, 255, -1)

    def test_embed_and_extract_watermark(self):
        """Test DWT-SVD watermark embedding and extraction fidelity."""
        watermarked_img, wm_key = embed_watermark(
            self.cover_img, self.logo_img, alpha=0.08, wavelet="haar", band="HL"
        )
        self.assertEqual(watermarked_img.shape, self.cover_img.shape)

        # High PSNR indicates imperceptible visual change
        psnr_val = calculate_psnr(self.cover_img, watermarked_img)
        self.assertGreater(psnr_val, 30.0)

        # Extract logo
        extracted_logo = extract_watermark(watermarked_img, wm_key)
        self.assertEqual(extracted_logo.shape, self.logo_img.shape)

        # High NC score indicates faithful logo recovery
        nc_val = calculate_nc(self.logo_img, extracted_logo)
        self.assertGreater(nc_val, 0.70)


class TestAttackSimulator(unittest.TestCase):
    """Test cases for image attack simulation pipeline."""

    def setUp(self):
        self.img = np.full((128, 128, 3), 128, dtype=np.uint8)

    def test_jpeg_attack(self):
        att_img = attack_jpeg_compression(self.img, quality=30)
        self.assertEqual(att_img.shape, self.img.shape)

    def test_gaussian_noise(self):
        att_img = attack_gaussian_noise(self.img, mean=0, var=50)
        self.assertEqual(att_img.shape, self.img.shape)

    def test_salt_and_pepper(self):
        att_img = attack_salt_and_pepper(self.img, amount=0.05)
        self.assertEqual(att_img.shape, self.img.shape)

    def test_center_crop(self):
        att_img = attack_center_crop(self.img, crop_pct=0.3)
        self.assertEqual(att_img.shape, self.img.shape)

    def test_brightness(self):
        att_img = attack_brightness(self.img, shift=20)
        self.assertEqual(att_img.shape, self.img.shape)

    def test_apply_attack_wrapper(self):
        att_img = apply_attack(self.img, "jpeg", {"quality": 40})
        self.assertEqual(att_img.shape, self.img.shape)


class TestMetricsModule(unittest.TestCase):
    """Test cases for quantitative metrics calculations."""

    def setUp(self):
        self.img1 = np.full((100, 100, 3), 100, dtype=np.uint8)
        self.img2 = np.full((100, 100, 3), 105, dtype=np.uint8)

    def test_psnr_identical(self):
        self.assertEqual(calculate_psnr(self.img1, self.img1), 100.0)

    def test_ssim_identical(self):
        self.assertEqual(calculate_ssim(self.img1, self.img1), 1.0)

    def test_nc_identical(self):
        logo = np.eye(50, dtype=np.uint8) * 255
        self.assertAlmostEqual(calculate_nc(logo, logo), 1.0, places=2)

    def test_ber(self):
        text1 = "Hello World"
        text2 = "Hello World"
        text3 = "Hello Vorld"  # 1 character difference
        self.assertEqual(calculate_ber(text1, text2), 0.0)
        self.assertGreater(calculate_ber(text1, text3), 0.0)

    def test_combined_metrics(self):
        metrics = calculate_metrics(self.img1, self.img2)
        self.assertIn("PSNR", metrics)
        self.assertIn("SSIM", metrics)


if __name__ == "__main__":
    unittest.main()

"""
MarkShield Steganography Engine
-------------------------------
AES-256 encrypted text payload embedding and extraction in image LSB (Least Significant Bit) space.

Security Features:
- PBKDF2HMAC (SHA-256, 100,000 iterations) key derivation from user password.
- AES-256-CBC encryption with PKCS7 padding and random 16-byte IV & 16-byte Salt.
- Magic header validation ('MSST') and payload length metadata.
"""

import os
import struct
import numpy as np
from typing import Tuple
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes, padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

MAGIC_HEADER = b"MSST"  # MarkShield Stego Header
SALT_SIZE = 16
IV_SIZE = 16
PBKDF2_ITERATIONS = 100_000


def derive_key(password: str, salt: bytes) -> bytes:
    """Derive 256-bit key from password using PBKDF2HMAC-SHA256."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,  # 256 bits
        salt=salt,
        iterations=PBKDF2_ITERATIONS,
        backend=default_backend()
    )
    return kdf.derive(password.encode("utf-8"))


def encrypt_payload(payload_text: str, password: str) -> bytes:
    """
    Encrypt plaintext secret payload using AES-256-CBC.
    Packet format: SALT (16B) + IV (16B) + CIPHERTEXT
    """
    salt = os.urandom(SALT_SIZE)
    iv = os.urandom(IV_SIZE)
    key = derive_key(password, salt)

    # Pad payload to AES block size (128 bits / 16 bytes)
    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(payload_text.encode("utf-8")) + padder.finalize()

    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(padded_data) + encryptor.finalize()

    return salt + iv + ciphertext


def decrypt_payload(encrypted_packet: bytes, password: str) -> str:
    """
    Decrypt packet containing SALT + IV + CIPHERTEXT using AES-256-CBC.
    """
    if len(encrypted_packet) < SALT_SIZE + IV_SIZE + 16:
        raise ValueError("Payload packet is too short or corrupted.")

    salt = encrypted_packet[:SALT_SIZE]
    iv = encrypted_packet[SALT_SIZE:SALT_SIZE + IV_SIZE]
    ciphertext = encrypted_packet[SALT_SIZE + IV_SIZE:]

    key = derive_key(password, salt)

    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()

    try:
        padded_data = decryptor.update(ciphertext) + decryptor.finalize()
        unpadder = padding.PKCS7(128).unpadder()
        plaintext_bytes = unpadder.update(padded_data) + unpadder.finalize()
        return plaintext_bytes.decode("utf-8")
    except Exception as e:
        raise ValueError("Decryption failed. Incorrect password or corrupted payload.") from e


def hide_payload(image: np.ndarray, payload_text: str, password: str) -> np.ndarray:
    """
    Embed AES-256 encrypted payload into image LSB.

    Args:
        image: Input image numpy array (uint8, shape HxWxC or HxW).
        payload_text: Secret text message to hide.
        password: Password for AES-256 encryption.

    Returns:
        Stego image with embedded payload as uint8 numpy array.
    """
    if not payload_text:
        raise ValueError("Payload text cannot be empty.")
    if not password:
        raise ValueError("Password cannot be empty.")

    encrypted_packet = encrypt_payload(payload_text, password)
    
    # Format bitstream: MAGIC (4B) + LENGTH (4B) + ENCRYPTED_PACKET
    packet_len = len(encrypted_packet)
    full_data = MAGIC_HEADER + struct.pack(">I", packet_len) + encrypted_packet

    # Convert full data bytes to bits
    bits = np.unpackbits(np.frombuffer(full_data, dtype=np.uint8))
    total_bits = len(bits)

    # Check capacity
    stego_img = image.copy()
    flat = stego_img.ravel()
    
    if total_bits > len(flat):
        raise ValueError(
            f"Image capacity exceeded. Payload requires {total_bits} bits, "
            f"but image only holds {len(flat)} bits."
        )

    # Embed bits into LSB of flat array
    flat[:total_bits] = (flat[:total_bits] & np.uint8(254)) | bits.astype(np.uint8)

    return stego_img.reshape(image.shape)


def extract_payload(image: np.ndarray, password: str) -> str:
    """
    Extract and decrypt secret payload from image LSB.

    Args:
        image: Stego image numpy array (uint8).
        password: Password for AES-256 decryption.

    Returns:
        Extracted secret text message.
    """
    if not password:
        raise ValueError("Password cannot be empty.")

    flat = image.ravel()
    
    # Header requires 4 bytes magic + 4 bytes length = 8 bytes = 64 bits
    if len(flat) < 64:
        raise ValueError("Image is too small to contain a valid payload.")

    # Extract first 64 bits (Header: Magic + Length)
    header_bits = flat[:64] & 1
    header_bytes = np.packbits(header_bits).tobytes()

    magic = header_bytes[:4]
    if magic != MAGIC_HEADER:
        raise ValueError("No valid MarkShield steganography payload detected in this image.")

    (packet_len,) = struct.unpack(">I", header_bytes[4:8])
    total_payload_bits = packet_len * 8
    total_needed_bits = 64 + total_payload_bits

    if total_needed_bits > len(flat):
        raise ValueError("Corrupted stego header: reported payload size exceeds image capacity.")

    # Extract payload bits
    payload_bits = flat[64:total_needed_bits] & 1
    encrypted_packet = np.packbits(payload_bits).tobytes()

    # Decrypt
    return decrypt_payload(encrypted_packet, password)

"""
MediTrust Encryption Module - AES-256-GCM
Handles encryption/decryption of patient medical data.
No audit or blockchain logic here - encryption only.
"""

import os
import base64
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from dotenv import load_dotenv


load_dotenv()


class EncryptionError(Exception):
    """Raised when encryption/decryption fails."""
    pass


class MasterKeyManager:
    """Loads and manages the master encryption key from environment."""

    @staticmethod
    def get_master_key() -> bytes:
        """
        Load master key from .env as base64-encoded string.
        Must be exactly 32 bytes (256 bits) for AES-256.
        
        Returns:
            bytes: 32-byte master key
            
        Raises:
            EncryptionError: If key is missing or invalid format
        """
        key_b64 = os.getenv("MASTER_KEY")
        
        if not key_b64:
            raise EncryptionError(
                "MASTER_KEY not found in .env. "
                "Generate with: python -c \"import base64, os; "
                "print(base64.b64encode(os.urandom(32)).decode())\""
            )
        
        try:
            key = base64.b64decode(key_b64)
        except Exception as e:
            raise EncryptionError(f"MASTER_KEY is not valid base64: {e}")
        
        if len(key) != 32:
            raise EncryptionError(
                f"MASTER_KEY must be exactly 32 bytes (256 bits), got {len(key)} bytes"
            )
        
        return key


class FileEncryption:
    """
    AES-256-GCM encryption/decryption for patient medical reports.
    
    Design:
    - Each report is encrypted with a unique data key
    - The data key is encrypted with the master key
    - Nonce (12 bytes) is generated randomly per encryption
    - GCM provides authenticated encryption (integrity checking)
    - Decryption occurs in-memory only
    """

    @staticmethod
    def encrypt_file(file_bytes: bytes) -> tuple[bytes, bytes]:
        """
        Encrypt a medical report file.
        
        Process:
        1. Generate random 12-byte nonce
        2. Generate random 32-byte data key
        3. Encrypt file with data key using AES-256-GCM
        4. Encrypt data key with master key
        5. Return (encrypted_blob, encrypted_data_key)
        
        Args:
            file_bytes: Raw bytes of medical report
            
        Returns:
            tuple: (encrypted_blob, encrypted_data_key)
                - encrypted_blob: nonce (12) + ciphertext + tag (16)
                - encrypted_data_key: encrypted data encryption key
                
        Raises:
            EncryptionError: If encryption fails
        """
        try:
            # Generate random nonce (12 bytes recommended for GCM)
            nonce = os.urandom(12)
            
            # Generate random data key (32 bytes for AES-256)
            data_key = os.urandom(32)
            
            # Encrypt file with data key
            cipher = AESGCM(data_key)
            ciphertext = cipher.encrypt(nonce, file_bytes, None)
            
            # Build encrypted blob: nonce + ciphertext (which includes GCM tag)
            encrypted_blob = nonce + ciphertext
            
            # Encrypt data key with master key
            master_key = MasterKeyManager.get_master_key()
            master_cipher = AESGCM(master_key)
            master_nonce = os.urandom(12)
            encrypted_data_key = master_nonce + master_cipher.encrypt(
                master_nonce, data_key, None
            )
            
            return encrypted_blob, encrypted_data_key
            
        except EncryptionError:
            raise
        except Exception as e:
            raise EncryptionError(f"Encryption failed: {e}")

    @staticmethod
    def decrypt_file(encrypted_blob: bytes, encrypted_data_key: bytes) -> bytes:
        """
        Decrypt a medical report file.
        
        Process:
        1. Decrypt data key using master key
        2. Extract nonce from encrypted_blob (first 12 bytes)
        3. Extract ciphertext from encrypted_blob (remaining)
        4. Decrypt using data key and nonce
        5. Return plaintext (in-memory only)
        
        Args:
            encrypted_blob: nonce (12) + ciphertext + tag (16)
            encrypted_data_key: encrypted data encryption key
            
        Returns:
            bytes: Decrypted file content (in-memory)
            
        Raises:
            EncryptionError: If decryption fails or authentication fails
        """
        try:
            # Decrypt data key using master key
            master_key = MasterKeyManager.get_master_key()
            master_cipher = AESGCM(master_key)
            master_nonce = encrypted_data_key[:12]
            encrypted_key_ciphertext = encrypted_data_key[12:]
            data_key = master_cipher.decrypt(master_nonce, encrypted_key_ciphertext, None)
            
            # Extract nonce and ciphertext from encrypted blob
            nonce = encrypted_blob[:12]
            ciphertext = encrypted_blob[12:]
            
            # Decrypt file
            cipher = AESGCM(data_key)
            plaintext = cipher.decrypt(nonce, ciphertext, None)
            
            return plaintext
            
        except EncryptionError:
            raise
        except Exception as e:
            raise EncryptionError(f"Decryption failed: {e}")

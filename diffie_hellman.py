from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, padding, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from secrets import token_bytes
import os
from datetime import datetime, timedelta
import logging

from smart_contract import contract, CONTRACT_ADDRESS


PRIVATE_KEY_PATH = "/Users/korn-m/Documents/diplom/"  # "/etc/client/keys/private_key.pem" TODO: change to correct path


class ProxyReencryption:
    def __init__(self, client_name):
        self.diffieHellman = None
        self.client_name = client_name

        if os.path.exists(os.path.join(PRIVATE_KEY_PATH, client_name)):
            self.check_private_key_path()

        if not self.diffieHellman:
            self.diffieHellman = ec.generate_private_key(ec.SECP384R1(), default_backend())

            pem = self.diffieHellman.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            )

            with open(os.path.join(PRIVATE_KEY_PATH, client_name), 'w') as key_file:
                key_file.write(pem.decode('utf-8'))

            self.public_key = self.diffieHellman.public_key()
            contract.addPublicKey(CONTRACT_ADDRESS, self.client_name, self.public_key)

        self.IV = token_bytes(16)

    def check_private_key_path(self):
        last_modified_time = os.path.getmtime(os.path.join(PRIVATE_KEY_PATH, self.client_name))
        last_modified_date = datetime.fromtimestamp(last_modified_time)
        now = datetime.now()
        time_difference = now - last_modified_date

        # refresh private key every 2 days
        if time_difference < timedelta(days=2):
            with open(os.path.join(PRIVATE_KEY_PATH, self.client_name), 'rb') as key_file:  # TODO key change path in all PRIVATE_KEY_PATH
                try:
                    private_key = serialization.load_pem_private_key(
                        key_file.read(),
                        password=None,
                        backend=default_backend()
                    )

                    if isinstance(private_key, ec.EllipticCurvePrivateKey):
                        self.diffieHellman = private_key
                        self.public_key = private_key.public_key()
                        contract.addPublicKey(CONTRACT_ADDRESS, self.client_name, self.public_key)
                    else:
                        print("Loaded key is not ECDSA")
                except ValueError as e:
                    print(f"Failed to load private key {e}")
                    os.remove(os.path.join(PRIVATE_KEY_PATH, self.client_name))

    def get_derived_key(self, public_key):
        shared_key = self.diffieHellman.exchange(ec.ECDH(), public_key)
        derived_key = HKDF(
            algorithm=hashes.SHA256(),
            length=32,
            salt=None,
            info=None,
            backend=default_backend()
        ).derive(shared_key)

        return derived_key

    def encrypt(self, public_key, secret):
        derived_key = self.get_derived_key(public_key)

        aes = Cipher(algorithms.AES(derived_key), modes.CBC(self.IV), backend=default_backend())
        encryptor = aes.encryptor()

        padder = padding.PKCS7(128).padder()
        padded_data = padder.update(secret.encode()) + padder.finalize()
        return self.IV + encryptor.update(padded_data) + encryptor.finalize()

    def decrypt(self, public_key, secret):
        iv = secret[:16]
        secret = secret[16:]

        derived_key = self.get_derived_key(public_key)

        aes = Cipher(algorithms.AES(derived_key), modes.CBC(iv), backend=default_backend())
        decryptor = aes.decryptor()
        decrypted_data = decryptor.update(secret) + decryptor.finalize()

        unpadder = padding.PKCS7(128).unpadder()
        return unpadder.update(decrypted_data) + unpadder.finalize()

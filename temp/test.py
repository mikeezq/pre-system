from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
import time

from statistics import mean

time_gen = []
time_encrypt = []
time_decrypt = []

for i in range(100):
    # Генерация ключей
    start_time = time.time()
    key = RSA.generate(1024)
    public_key = key.publickey()
    encryptor = PKCS1_OAEP.new(public_key)
    time_gen.append(time.time() - start_time)

    # Шифрование
    start_time = time.time()
    encrypted_message = encryptor.encrypt(b'This is a test message.')
    time_encrypt.append(time.time() - start_time)

    # Расшифрование
    decryptor = PKCS1_OAEP.new(key)
    start_time = time.time()
    decrypted_message = decryptor.decrypt(encrypted_message)
    time_decrypt.append(time.time() - start_time)

print(f"Время генерации ключей: {mean(time_gen)}")
print(f"Время шифрования: {mean(time_encrypt)} секунды")
print(f"Время расшифрования: {mean(time_decrypt)} секунды")

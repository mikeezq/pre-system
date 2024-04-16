import binascii
import os
import json
import zlib

import requests

from datetime import datetime, timedelta
from charm.core.engine.util import objectToBytes, bytesToObject
from charm.toolbox.pairinggroup import PairingGroup
from charm.schemes.pre_mg07 import PreGA
from charm.toolbox.conversion import Conversion


def serialize_data(group, data):
    if isinstance(data, dict):
        serialized_data = {}
        for key, value in data.items():
            serialized_data[key] = serialize_data(group, value)
        return serialized_data
    else:
        try:
            return objectToBytes(data, group).hex()
        except TypeError:
            return Conversion.IP2OS(data).hex()


def deserialize_data(group, serialized_data):
    if isinstance(serialized_data, dict):
        data = {}
        for key, value in serialized_data.items():
            data[key] = deserialize_data(group, value)  # Рекурсивная обработка для словарей
        return data
    else:
        try:
            return bytesToObject(bytes.fromhex(serialized_data), group)
        except (zlib.error, binascii.Error):
            return Conversion.OS2IP(bytes.fromhex(serialized_data), element=True)


def convert_object_to_hex_str(group, message=None, rekey=None, params=None, id_secret_key=None):
    id_secret_key_hex_str = None
    if id_secret_key:
        id_secret_key_bytes = objectToBytes(id_secret_key, group)
        id_secret_key_hex_str = id_secret_key_bytes.hex()

    params_hex_str = None
    if params:
        params_hex_str = {k: objectToBytes(v, group).hex() for k, v in params.items()}

    message_hex_str = None
    if message:
        message_hex_str = serialize_data(group, message)

    rekey_hex_str = None
    if rekey:
        rekey_hex_str = serialize_data(group, rekey)

    return message_hex_str, rekey_hex_str, params_hex_str, id_secret_key_hex_str


def convert_hex_str_to_object(group, message_hex_str=None, rekey_hex_str=None,
                              params_hex_str=None, id_secret_key_hex_str=None):
    id_secret_key = None
    if id_secret_key_hex_str:
        id_secret_key_bytes = bytes.fromhex(id_secret_key_hex_str)
        id_secret_key = bytesToObject(id_secret_key_bytes, group)

    params = None
    if params_hex_str:
        params = {k: bytesToObject(bytes.fromhex(v), group) for k, v in params_hex_str.items()}

    message = None
    if message_hex_str:
        message = deserialize_data(group, message_hex_str)

    rekey = None
    if rekey_hex_str:
        rekey = deserialize_data(group, rekey_hex_str)

    return message, rekey, params, id_secret_key


def get_key_params(url, id, group):
    message_data = json.dumps({
        'sender_id': id,
    })
    response = requests.post(url, data=message_data)
    id_secret_key_hex_str = json.loads(response.text).get("id_secret_key_hex_str")
    params_hex_str = json.loads(response.text).get("params_hex_str")

    _, _, params, id_secret_key = convert_hex_str_to_object(group, id_secret_key_hex_str=id_secret_key_hex_str,
                                                            params_hex_str=params_hex_str)

    return id_secret_key, params


def setup_pre():
    group = PairingGroup('SS512', secparam=1024)
    pre = PreGA(group)
    return pre, group


def check_private_key_path():
    last_modified_time = os.path.getmtime(os.path.join())
    last_modified_date = datetime.fromtimestamp(last_modified_time)
    now = datetime.now()
    time_difference = now - last_modified_date

    # refresh private key every 2 days
    if time_difference < timedelta(days=2):
        pass
    # TBD add logic


def send_large_message(socket, message_data, chunk_size=4096):
    # Конвертируем данные в байты
    message_bytes = message_data.encode('utf-8')

    # Отправляем размер сообщения перед самим сообщением
    total_size = len(message_bytes)
    socket.sendall(total_size.to_bytes(4, 'big'))

    # Разбиваем сообщение на части и отправляем каждую часть
    for i in range(0, total_size, chunk_size):
        chunk = message_bytes[i:i + chunk_size]
        socket.sendall(chunk)


def receive_large_message(socket, chunk_size=4096):
    # Сначала получаем размер сообщения
    total_size_bytes = socket.recv(4)
    total_size = int.from_bytes(total_size_bytes, 'big')

    # Теперь читаем данные до тех пор, пока не получим полное сообщение
    chunks = []
    bytes_recd = 0
    while bytes_recd < total_size:
        chunk = socket.recv(min(total_size - bytes_recd, chunk_size))
        if chunk == b'':
            raise RuntimeError("Socket connection broken")
        chunks.append(chunk)
        bytes_recd += len(chunk)

    # Собираем все части в одно сообщение
    return b''.join(chunks).decode('utf-8')



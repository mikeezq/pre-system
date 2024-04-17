import socket
import argparse
import json
import logging

from util import get_key_params, setup_pre, convert_object_to_hex_str, send_large_message
from constants import CA_URL
from smart_contract import contract

logging.basicConfig(level=logging.INFO)
pre, group = setup_pre()
ID = "client-a"
ID2 = "client-b"


def main(host_ip, host_port):
    id_secret_key, params = get_key_params(CA_URL, ID, group)

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    client_socket.connect((host_ip, host_port))

    message = "<confidential message>"
    encrypted_message = pre.encrypt(params, ID, message)
    rekey = pre.rkGen(params, id_secret_key, ID, ID2)
    print(f"PARAMS: {params}")
    print(f"MESSAGE: {encrypted_message}")
    print(f"REKEY: {rekey}")
    encrypted_message_hex_str, rekey_hex_str, _, _ = convert_object_to_hex_str(
        group,
        message=encrypted_message,
        rekey=rekey,
    )

    rekey = json.dumps(rekey_hex_str)
    contract.addReKey(ID, rekey)

    print(encrypted_message_hex_str)

    message_data = json.dumps({
        'sender_id': ID,
        'encrypted_message_hex_str': encrypted_message_hex_str,
        'rekey_hex_str': rekey_hex_str,
    })

    print(type(message_data))

    send_large_message(client_socket, message_data)

    response = client_socket.recv(1024)
    logging.info("Get response from client: %s", response.decode('utf-8'))

    client_socket.close()


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host-ip", type=str, default="0.0.0.0")
    parser.add_argument("--host-port", type=int, default=1024)
    parser.add_argument("--client-name", type=str, default="client-a")

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    main(args.host_ip, args.host_port)

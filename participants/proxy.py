import requests
import socket
import argparse
import logging
import json

from constants import CA_URL
from util import receive_large_message, convert_hex_str_to_object, setup_pre, get_key_params, convert_object_to_hex_str
from smart_contract import contract

logging.basicConfig(level=logging.INFO)
pre, group = setup_pre()


def main(args):
    server_host = '0.0.0.0'
    server_port = 1024

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((server_host, server_port))
    server_socket.listen(5)
    _, params = get_key_params(CA_URL, "proxy", group) # TODO: check it

    logging.info(f"Server listen {server_host}:{server_port}")

    while True:
        client_socket, client_address = server_socket.accept()

        message_data = receive_large_message(client_socket)
        # if not data:
        #     break

        data = json.loads(message_data)
        sender_id = data.get('sender_id')
        encrypted_message_hex_str = data.get('encrypted_message_hex_str')

        logging.info(f"Got encrypted message from client: {sender_id}")

        rekey_hex_str = json.loads(contract.getReKey(sender_id, "receiver"))

        encrypted_message, rekey, _, _ = convert_hex_str_to_object(
            group,
            message_hex_str=encrypted_message_hex_str,
            rekey_hex_str=rekey_hex_str
        )

        encrypted_message = pre.reEncrypt(params, sender_id, rekey, encrypted_message)
        encrypted_message_hex_str, _, _, _ = convert_object_to_hex_str(
            group,
            message=encrypted_message
        )

        data['encrypted_message_hex_str'] = encrypted_message_hex_str
        data = json.dumps(data)

        url = args.client_url
        response = requests.post(url, data=data.encode('utf-8'))  # TODO: verify=args.client_cert

        client_socket.send(response.text.encode('utf-8'))
        client_socket.close()


def parse_args():
    parser = argparse.ArgumentParser()
    # TODO: change to client-b.test-zone.ru
    parser.add_argument("--client-url", type=str, default="http://127.0.0.1:1028/secure")
    parser.add_argument("--client-cert", type=str, metavar="PATH",
                        default="/usr/local/share/ca-certificates/client-b.crt")

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    main(args)

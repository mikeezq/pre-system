import socket
import argparse
import json
import logging

from diffie_hellman import ProxyReencryption
from smart_contract import contract, convert_to_ec


def encrypt_message(message, client_name):
    sender = ProxyReencryption("client-a")
    receiver_pub = contract.getPublicKey(client_name)

    receiver_pub = convert_to_ec(receiver_pub)
    encrypted_message = sender.encrypt(receiver_pub, message)

    return encrypted_message


def main(host_ip, host_port, client_name):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    client_socket.connect((host_ip, host_port))

    message = "<confidential message>"
    encrypted_message = encrypt_message(message, client_name)

    message_data = json.dumps({
        'sender_name': "client-a",
        'message': encrypted_message.hex()
    })

    client_socket.send(message_data.encode('utf-8'))

    response = client_socket.recv(1024)
    logging.info("Get response from client: %s", response.decode('utf-8'))

    client_socket.close()


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host-ip", type=str, default="0.0.0.0")
    parser.add_argument("--host-port", type=int, default=1024)
    parser.add_argument("--client-name", type=str, default="client-b")

    return parser.parse_args()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    args = parse_args()
    main(args.host_ip, args.host_port, args.client_name)

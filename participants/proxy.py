import requests
import socket
import argparse
import logging


from util import receive_large_message


logging.basicConfig(level=logging.INFO)


def main(args):
    server_host = '0.0.0.0'
    server_port = 1024

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((server_host, server_port))
    server_socket.listen(5)

    print(f"Server listen {server_host}:{server_port}")

    while True:
        client_socket, client_address = server_socket.accept()

        message_data = receive_large_message(client_socket)
        # if not data:
        #     break
        print(f"Got encrypted message from client: {message_data}")  # TODO change to sender id

        url = args.client_url
        response = requests.post(url, data=message_data)  # TODO: verify=args.client_cert

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










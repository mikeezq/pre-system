import requests
import socket
import argparse
import logging


def main(args):
    server_host = '0.0.0.0'
    server_port = 1024

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((server_host, server_port))
    server_socket.listen(5)

    print(f"Server listen {server_host}:{server_port}")

    while True:
        client_socket, client_address = server_socket.accept()

        data = client_socket.recv(1024)
        # if not data:
        #     break
        print(f"Get encrypted message from client: {data.decode('utf-8')}")

        url = args.client_url
        response = requests.post(url, data=data.decode('utf-8'))  # TODO: verify=args.client_cert

        client_socket.send(response.text.encode('utf-8'))
        client_socket.close()


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--client-url", type=str, default="http://127.0.0.1:1025/secure") # TODO: change to client-b.test-zone.ru
    parser.add_argument("--client-cert", type=str, metavar="PATH",
                        default="/usr/local/share/ca-certificates/client-b.crt")

    return parser.parse_args()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    args = parse_args()
    main(args)










import http.server
import ssl
import json
import logging

from diffie_hellman import ProxyReencryption
from smart_contract import contract, convert_to_ec


logging.basicConfig(level=logging.INFO)
client = ProxyReencryption("client-b")


def decrypt_message(encrypted_message, sender_name):
    sender_pub = contract.getPublicKey(sender_name)

    sender_pub = convert_to_ec(sender_pub)
    decrypted_message = client.decrypt(sender_pub, encrypted_message)

    return decrypted_message


class Handler(http.server.SimpleHTTPRequestHandler):
    def do_POST(self):
        if self.path == '/secure':
            content_length = int(self.headers['Content-Length'])  # Получаем размер данных
            post_data = self.rfile.read(content_length)  # Читаем данные

            try:
                data = json.loads(post_data.decode('utf-8'))

                sender_name = data.get('sender_name')
                encrypted_message = data.get('message')

                decrypted_message = decrypt_message(bytes.fromhex(encrypted_message), sender_name)
                logging.info("Decrypted message: %s, from client: %s", decrypted_message.decode('utf-8'), sender_name)

                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                response_message = "Data received".encode()
                self.wfile.write(response_message)

            except json.JSONDecodeError:
                self.send_response(400)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(b'Invalid JSON received')

            return

        return super().do_GET()


def main():
    server_address = ('0.0.0.0', 1025)  # TODO change to 443
    httpd = http.server.HTTPServer(server_address, Handler)
    # httpd.socket = ssl.wrap_socket(  TODO: uncomment
    #     httpd.socket,
    #     server_side=True,
    #     certfile='/etc/nginx/ssl/cert.pem',
    #     keyfile='/etc/nginx/ssl/key.pem',
    #     ssl_version=ssl.PROTOCOL_TLS
    # )
    httpd.serve_forever()


if __name__ == "__main__":
    main()

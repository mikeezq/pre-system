import http.server
import json
import logging

from util import get_key_params, setup_pre, convert_hex_str_to_object, receive_large_message
from constants import CA_URL


logging.basicConfig(level=logging.INFO)
pre, group = setup_pre()
ID = "client-b"

# REKEY: {'N': "<class 'integer.Element'>", 'R': "<class 'pairing.Element'>"}
# {
# MESSAGE 'S': "<class 'pairing.Element'>", 'C': {
#   'A': "<class 'pairing.Element'>",
#   'B': "<class 'pairing.Element'>",
#   'C': "<class 'integer.Element'>"
#   }
# }


class Handler(http.server.SimpleHTTPRequestHandler):
    def do_POST(self):
        if self.path == '/secure':
            content_length = int(self.headers['Content-Length'])  # Получаем размер данных
            post_data = self.rfile.read(content_length)  # Читаем данные

            try:
                # TODO add logic to check key lifecycle
                id_secret_key, params = get_key_params(CA_URL, ID, group)

                logging.info("Got data: %r", post_data)
                data = json.loads(post_data.decode('utf-8'))

                sender_id = data.get('sender_id')
                encrypted_message_hex_str = data.get('encrypted_message_hex_str')
                encrypted_message, _, _, _ = convert_hex_str_to_object(
                    group,
                    message_hex_str=encrypted_message_hex_str,
                )

                logging.info(f"PARAMS: {params}")
                logging.info(f"MESSAGE: {encrypted_message}")

                # TODO: add correct id params
                decrypted_message = pre.decryptSecondLevel(params, id_secret_key, "client-a", ID, encrypted_message)
                logging.info("Decrypted message: %s, from client: %s", decrypted_message, sender_id)

                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                response_message = "Data received".encode()
                self.wfile.write(response_message)

            except json.JSONDecodeError as e:
                logging.info("Got error %s", e)
                self.send_response(400)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(b'Invalid JSON received')

            return

        return super().do_GET()


def main():
    server_address = ('0.0.0.0', 1028)  # TODO change to 443
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

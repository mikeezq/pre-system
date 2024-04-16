import http.server
import ssl
import json
import logging

from util import convert_object_to_hex_str, setup_pre


logging.basicConfig(level=logging.INFO)

pre, group = setup_pre()
(master_secret_key, params) = pre.setup()


class Handler(http.server.SimpleHTTPRequestHandler):
    def do_POST(self):
        if self.path == '/key':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)

            try:
                data = json.loads(post_data.decode('utf-8'))

                sender_id = data.get('sender_id')
                logging.info("Got key request from: %s", sender_id)

                id_secret_key = pre.keyGen(master_secret_key, sender_id)

                _, _, params_hex_str, id_secret_key_hex_str = convert_object_to_hex_str(
                    group,
                    id_secret_key=id_secret_key,
                    params=params
                )

                response_message = json.dumps({
                    'id_secret_key_hex_str': id_secret_key_hex_str,
                    'params_hex_str': params_hex_str,
                })

                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(response_message.encode('utf-8'))

            except json.JSONDecodeError:
                self.send_response(400)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(b'Invalid JSON received')

            return

        return super().do_GET()


def main():
    server_address = ('0.0.0.0', 1026)  # TODO change to 443
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

from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
import socket
import json
import pathlib
import mimetypes
import threading
from datetime import datetime

class HttpHandler(BaseHTTPRequestHandler):

    def send_static(self):
        self.send_response(200)
        mt = mimetypes.guess_type(self.path)
        if mt:
            self.send_header("Content-type", mt[0])
        else:
            self.send_header("Content-type", 'text/plain')
        self.end_headers()
        with open(f'.{self.path}', 'rb') as file:
            self.wfile.write(file.read())

    def do_GET(self):
        pr_url = urllib.parse.urlparse(self.path)

        if pr_url.path == '/':
            self.send_html_file('index.html')
        elif pr_url.path == '/contact':
            self.send_html_file('contact.html')
        else:
            if pathlib.Path().joinpath(pr_url.path[1:]).exists():
                self.send_static()
            else:
                self.send_html_file('error.html', 404)

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)

        print(f"Received data from form: {post_data.decode()}")
        self.send_data_to_udp(post_data)

        self.send_response(302)
        self.send_header('Location', '/')
        self.end_headers()

    def send_data_to_udp(self, data):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            udp_server_address = ('localhost', 5000)
            sock.sendto(data, udp_server_address)

    def send_html_file(self, filename, status=200):
        self.send_response(status)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        with open(filename, 'rb') as fd:
            self.wfile.write(fd.read())


def run(server_class=HTTPServer, handler_class=HttpHandler):
    server_address = ('', 3000)
    http = server_class(server_address, handler_class)
    try:
        http.serve_forever()
    except KeyboardInterrupt:
        http.server_close()


def run_udp_server():
    udp_server_address = ('localhost', 5000)
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_socket:
        udp_socket.bind(udp_server_address)
        try:
            print(f"Starting UDP server on port {udp_server_address[1]}")
            while True:
                data, addr = udp_socket.recvfrom(1024)
                print(f'Received data: {data.decode()} from: {addr}')
                try:
                    data_dict = json.loads(data.decode())
                    process_and_save_data(data_dict)
                except Exception as e:
                    print(f"Error while processing data: {e}")
        except KeyboardInterrupt:
            print("Stopping UDP server")

def process_and_save_data(data_dict):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    print(f"Received data at {timestamp}: {data_dict}")

    new_entry = {timestamp: {"username": data_dict.get("username", ""),
                             "message": data_dict.get("message", "")}}

    try:
        if not data:
            data = {}

        data_dict = json.loads(data.decode())

        data.update(new_entry)

        with open('storage/data.json', 'w') as json_file:
            json.dump(data, json_file)
    except Exception as e:
        print(f"Error while saving data: {e}")


if __name__ == '__main__':

    http_thread = threading.Thread(target=run)
    http_thread.start()

    udp_thread = threading.Thread(target=run_udp_server)
    udp_thread.start()

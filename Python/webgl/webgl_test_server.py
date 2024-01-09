from argparse import ArgumentParser
from http.server import HTTPServer, SimpleHTTPRequestHandler


class WebGLTestServer(SimpleHTTPRequestHandler):
    """
    A system HTTP local test server for hosting TDW WebGL builds.

    Usage:

    python3 webgl_test_server.py --directory [DIRECTORY] --port [PORT]

    DO NOT USE THIS SCRIPT TO HOST A PUBLIC-FACING PROJECT.
    This script implements only basic security checks.
    It is meant only for testing purposes.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=parsed_args.directory, **kwargs)

    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        return super(WebGLTestServer, self).end_headers()


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--directory",
                        type=str,
                        default="../../../TDWBase/bin/webgl",
                        help="The directory of the TDW WebGL Build")
    parser.add_argument("--port",
                        type=int,
                        default=8000,
                        help="The network port")
    parsed_args = parser.parse_args()
    httpd = HTTPServer(('localhost', parsed_args.port), WebGLTestServer)
    httpd.serve_forever()

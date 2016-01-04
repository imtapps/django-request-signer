#!/usr/bin/env python
import six
import os
import sys


def monkey_patch_for_multi_threaded():
    if six.PY3:
        from http.server import HTTPServer
        from socketserver import ThreadingMixIn
    else:
        from BaseHTTPServer import HTTPServer
        from SocketServer import ThreadingMixIn
    OriginalHTTPServer = HTTPServer

    class ThreadedHTTPServer(ThreadingMixIn, OriginalHTTPServer):
        def __init__(self, server_address, RequestHandlerClass=None):
            OriginalHTTPServer.__init__(self, server_address, RequestHandlerClass)

    HTTPServer = ThreadedHTTPServer


if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "example.settings")

    from django.core.management import execute_from_command_line
    monkey_patch_for_multi_threaded()

    execute_from_command_line(sys.argv)

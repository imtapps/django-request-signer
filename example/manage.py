#!/usr/bin/env python
import os
import sys


def monkey_patch_for_multi_threaded():
    import BaseHTTPServer
    import SocketServer
    OriginalHTTPServer = BaseHTTPServer.HTTPServer

    class ThreadedHTTPServer(SocketServer.ThreadingMixIn, OriginalHTTPServer):
        def __init__(self, server_address, RequestHandlerClass=None):
            OriginalHTTPServer.__init__(self, server_address, RequestHandlerClass)

    BaseHTTPServer.HTTPServer = ThreadedHTTPServer


if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")

    from django.core.management import execute_from_command_line
    monkey_patch_for_multi_threaded()

    execute_from_command_line(sys.argv)

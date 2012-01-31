
***************************
About Django Request Signer
***************************

About
=====

Django Request Signer provides both a client and a server component to
assist in verifying that both the sending and receiving ends of a web
service call can trust one another. This trust is established by allowing
clients to register with the server and receive a unique public client id
and a private key.

How it Works
============

#. A client will have an id and a private key which is issued by the server.
#. The server will store all client ids and corresponding private keys.
#. When a client needs to request something from the server the following will happen:
    I.   The request URL, querystring, post data, and client id will be combined with
            the private key to create a unique signature.
    II.  The url, post data (if any exists), querystring, plus the client id and
            signature will be passed to the server in an http request.
    III. The server will receive the request, and use the client id to look up the
            corresponding private key.
    IV.  The server will then use the request (minus the signature) along with the
            private key to try to recreate the exact same signature as the one passed
            from the client.
    V.   If the server is able to calculate the same signature that was provided by the
            client, the server knows it can trust the request, if not the server will
            respond with a Bad Request (400).

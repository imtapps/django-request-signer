Feature: Server rejects all requests that do not have a valid signature

    Scenario: Server accepts valid signature from client
        Given a client with the client id "me" and the private key "bWU="
            And that client is registered with the server
        When the client makes a request to the server at "/sample/" with the correct signature
        Then the server should reply with a "200"

    Scenario: Server rejects incorrect signature from client
        Given a client with the client id "me" and the private key "bWU="
            And that client is registered with the server
        When the client makes a request to the server at "/sample/" with an invalid signature
        Then the server should reply with a "400"

    Scenario: Server rejects unsigned request
        Given a client with the client id "me" and the private key "bWU="
            And that client is registered with the server
        When the client makes a request to the server at "/sample/" with no signature
        Then the server should reply with a "400"

    Scenario: Server accepts valid signature from client with post data
        Given a client with the client id "me" and the private key "bWU="
            And that client is registered with the server
        When the client posts a request to the server at "/sample/" with the correct signature and the following data:
            | arg1 | arg2 | arg3 | arg4 |
            | val1 | val2 | val3 | val4 |
        Then the server should reply with a "200"

    Scenario: Server accepts valid signature from client that posts with no data
        Given a client with the client id "me" and the private key "bWU="
            And that client is registered with the server
        When the client posts a request to the server at "/sample/" with the correct signature and no data
        Then the server should reply with a "200"

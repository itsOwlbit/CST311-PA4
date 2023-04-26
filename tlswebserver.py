#!/usr/bin/env python3

# Names: Kevin Mcnulty, Nadia Rahbany, Juli Shinozuka, and Andrew Shiraki
# Date: June 16, 2022
# Title: Create TLS Webserver Certificate
# Description: This program creates the tls webserver certificate

import http.server
import ssl
#Get path of this script need os to do it
import os
PATH=os.path.abspath(os.path.dirname(__file__))
## Variables you can modify
server_address = ""
server_port = 4443
ssl_key_file = PATH+"/server-cert/otterbots.private-key.pem"
ssl_certificate_file = PATH+"/server-cert/cacert.pem"
 
 
## Don't modify anything below
httpd = http.server.HTTPServer((server_address, server_port), http.server.SimpleHTTPRequestHandler)
httpd.socket = ssl.wrap_socket (httpd.socket,
                server_side=True,
                                keyfile=ssl_key_file,
                                certfile=ssl_certificate_file,
                ssl_version=ssl.PROTOCOL_TLSv1_2)
 
print("Listening on port", server_port)                                
httpd.serve_forever()

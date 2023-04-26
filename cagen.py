# Names: Kevin Mcnulty, Nadia Rahbany, Juli Shinozuka, and Andrew Shiraki
# Date: June 16, 2022
# Title: CA generator
# Description: This program creates the Certificate Authority for PA4.

import subprocess as sp

#get path
import os
PATH=os.path.abspath(os.path.dirname(__file__))

sp.run(["mkdir", PATH+"/server-cert"])

open (PATH+"/server-cert/ssl.cnf", "w").write(
"""
[req]
default_bits = 2048
prompt = no
default_md = sha256
encrypt_key = no
distinguished_name = dn

[dn]
C = US
O = OtterBots, Inc.
OU = Team13
CN = 10.0.1.200
"""
)

#Generate private key/root ca
sp.run(['openssl', 'genrsa', '-out', PATH+'/server-cert/otterbots.private-key.pem', '2048'])

#csr 
sp.run(['openssl', 'req', '-new', '-key', PATH+'/server-cert/otterbots.private-key.pem', '-out', PATH+'/server-cert/otterbots.private.csr', '-config', PATH+'/server-cert/ssl.cnf'])

#self signed server cert out in pem 
sp.run(['openssl', 'x509', '-req', '-days', '365', '-in', PATH+'/server-cert/otterbots.private.csr', '-signkey', PATH+'/server-cert/otterbots.private-key.pem', '-out', PATH+'/server-cert/cacert.pem'])

print('Server Certificate Issued')

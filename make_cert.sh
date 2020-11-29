#!/bin/bash

openssl req -x509 -sha256 -newkey rsa:2048 -keyout certificate.key -out certificate.crt -days 1024 -nodes -subj '/CN=my.domain.tld'


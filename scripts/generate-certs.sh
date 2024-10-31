#!/bin/bash
mkdir -p ./nginx/certs

# Generate CA private key and certificate
openssl req -x509 \
    -newkey rsa:4096 \
    -days 365 \
    -nodes \
    -keyout nginx/certs/ca-key.pem \
    -out nginx/certs/ca-cert.pem \
    -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"

# Generate server private key and CSR
openssl req -newkey rsa:4096 \
    -nodes \
    -keyout nginx/certs/server-key.pem \
    -out nginx/certs/server-req.pem \
    -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"

# Generate server certificate
openssl x509 -req \
    -in nginx/certs/server-req.pem \
    -days 365 \
    -CA nginx/certs/ca-cert.pem \
    -CAkey nginx/certs/ca-key.pem \
    -CAcreateserial \
    -out nginx/certs/server-cert.pem

# Set proper permissions
chmod 600 nginx/certs/*.pem 
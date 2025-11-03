#!/bin/bash

# Generate self-signed SSL certificate for HTTPS
# This script creates a certificate valid for the VM IP and localhost

SSL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VM_IP="210.79.129.25"

echo "Generating self-signed SSL certificate..."
echo "Certificate will be valid for:"
echo "  - localhost"
echo "  - $VM_IP"
echo "  - 127.0.0.1"

# Create OpenSSL config
cat > "$SSL_DIR/openssl.cnf" <<EOF
[req]
default_bits = 2048
prompt = no
default_md = sha256
distinguished_name = dn
req_extensions = v3_req

[dn]
C=US
ST=State
L=City
O=Organization
CN=$VM_IP

[v3_req]
basicConstraints = CA:FALSE
keyUsage = nonRepudiation, digitalSignature, keyEncipherment
subjectAltName = @alt_names

[alt_names]
DNS.1 = localhost
DNS.2 = $VM_IP
IP.1 = 127.0.0.1
IP.2 = $VM_IP
EOF

# Generate private key
openssl genrsa -out "$SSL_DIR/server.key" 2048

# Generate certificate signing request
openssl req -new -key "$SSL_DIR/server.key" -out "$SSL_DIR/server.csr" -config "$SSL_DIR/openssl.cnf"

# Generate self-signed certificate (valid for 365 days)
openssl x509 -req -in "$SSL_DIR/server.csr" -signkey "$SSL_DIR/server.key" \
    -out "$SSL_DIR/server.crt" -days 365 -extensions v3_req -extfile "$SSL_DIR/openssl.cnf"

# Set proper permissions
chmod 600 "$SSL_DIR/server.key"
chmod 644 "$SSL_DIR/server.crt"

# Clean up
rm "$SSL_DIR/server.csr" "$SSL_DIR/openssl.cnf"

echo "SSL certificate generated successfully!"
echo "Certificate: $SSL_DIR/server.crt"
echo "Private Key: $SSL_DIR/server.key"
echo ""
echo "Note: Browsers will show a security warning for self-signed certificates."
echo "This is normal and expected. Click 'Advanced' -> 'Proceed' to continue."


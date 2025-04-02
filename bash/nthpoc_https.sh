#!/bin/bash

# cd to venv directory
cd /home/pocadmin/poc/POC2025-app

# activate venv
. .venv/bin/activate

# run streamlit
streamlit run Nth_Private_AI.py \
  --server.enableCORS=false \
  --server.sslKeyFile certs/key.pem \
  --server.sslCertFile certs/cert.pem \
  --server.port 443
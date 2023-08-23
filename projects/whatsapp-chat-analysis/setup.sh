#!/bin/bash

mkdir -p ~/.streamlit/

cat <<EOT >> ~/.streamlit/config.toml
[server]
port = \$PORT
enableCORS = false
headless = true
EOT
mkdir ../certs
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout ../certs/key.pem -out ../certs/cert.pem
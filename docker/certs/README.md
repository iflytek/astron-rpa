# TLS certificates

Place the certificate chain and its matching private key in this directory.
The default file names are `tls.crt` and `tls.key`; both can be changed in
`.env` with `TLS_CERTIFICATE_FILE` and `TLS_CERTIFICATE_KEY_FILE`.

The certificate must cover both `RPA_SERVER_NAME` and
`CASDOOR_SERVER_NAME`. Never commit a real certificate or private key.

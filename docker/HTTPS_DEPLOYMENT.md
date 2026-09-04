# HTTPS deployment, migration, and rollback

AstronRPA terminates public TLS in OpenResty. Communication between containers
continues to use the existing private Docker network and HTTP service names.
The default deployment mode is `https`; `legacy-http` is an explicit,
unencrypted compatibility mode.

## 1. Prepare public names and a certificate

Use a certificate whose Subject Alternative Name covers both the AstronRPA and
Casdoor public names. Copy the full certificate chain and matching private key
to `docker/certs/`. Real certificates and private keys are ignored by Git.

Default names:

```text
docker/certs/tls.crt
docker/certs/tls.key
```

The container refuses to start in HTTPS mode when either file is missing,
empty, or configured as a path outside `/etc/nginx/certs`.

## 2. Configure HTTPS

Copy `.env.example` to `.env`, then set at least:

```env
DEPLOYMENT_MODE="https"
RPA_SERVER_NAME="rpa.example.com"
CASDOOR_SERVER_NAME="auth.example.com"

# Include the port when it is not the standard HTTPS port.
RPA_HTTPS_REDIRECT_AUTHORITY="rpa.example.com"
CASDOOR_HTTPS_REDIRECT_AUTHORITY="auth.example.com:8443"

RPA_HTTPS_PORT=443
CASDOOR_HTTPS_PORT=8443
CASDOOR_EXTERNAL_ENDPOINT="https://auth.example.com:8443"

TLS_CERTIFICATE_FILE="tls.crt"
TLS_CERTIFICATE_KEY_FILE="tls.key"
SESSION_COOKIE_SECURE=true
```

`CASDOOR_ENDPOINT` must remain the internal HTTP address:

```env
CASDOOR_ENDPOINT="http://rpa-opensource-casdoor:8000"
```

The old HTTP ports are loopback-only by default and return `308` redirects.
They can be exposed temporarily during migration by changing their bind
addresses, but no credential should be sent to an HTTP URL.

## 3. Validate and start

```bash
docker compose config
docker compose up -d
docker compose ps
docker compose logs openresty-nginx

curl -I http://127.0.0.1:32742/health
curl https://rpa.example.com/health
```

The first request must return a `308` redirect. The second must return
`healthy` with a valid, trusted certificate.

Configure an installed client with the HTTPS gateway URL, for example:

```yaml
remote_addr: https://rpa.example.com/
```

The existing scheduler derives `https` and `wss` from this value; no client
source change or rebuild is required.

## 4. Migrate an existing HTTP deployment

1. Back up `.env` and the current Compose configuration. Database changes are
   not required.
2. Prepare and validate the certificate names before changing public URLs.
3. Update the HTTPS variables and `CASDOOR_EXTERNAL_ENDPOINT`.
4. Start the default HTTPS mode and verify `/health`, login, MCP Streamable
   HTTP, and WebSocket routes.
5. Update callers to the HTTPS gateway address.
6. Keep the old HTTP ports only for redirects, then return their bind address
   to `127.0.0.1` after migration.

## 5. Explicit legacy HTTP compatibility

`legacy-http` restores the old gateway and Casdoor protocols through
OpenResty. It also disables the Secure flag for the legacy session cookie.
This mode is unencrypted and intended only for a controlled migration or local
development. The override uses the Compose `!override` tag and therefore
requires Docker Compose 2.24.4 or newer. It removes the unused HTTPS port
mappings so that legacy rollback does not reserve ports `443` or `8443`.

For loopback-only HTTP:

```bash
docker compose -f docker-compose.yml -f docker-compose.legacy-http.yml up -d
```

An existing remote deployment must make the insecure exposure explicit:

```env
RPA_HTTP_BIND_ADDRESS="0.0.0.0"
CASDOOR_HTTP_BIND_ADDRESS="0.0.0.0"
LEGACY_CASDOOR_EXTERNAL_ENDPOINT="http://YOUR_SERVER:8000"
```

Then start with the same two Compose files. Do not use this configuration for
a new public installation.

## 6. Roll back HTTPS configuration

If a deployment-specific certificate or name issue requires a temporary
rollback:

```bash
docker compose down
docker compose -f docker-compose.yml -f docker-compose.legacy-http.yml up -d
```

Restore callers to their previous HTTP gateway URL and set
`LEGACY_CASDOOR_EXTERNAL_ENDPOINT` to the previous Casdoor URL. This rollback
does not require database restoration and does not remove Docker volumes.

Return to HTTPS as soon as the certificate or name issue is corrected.

# AstronRPA HTTPS quick start

Public AstronRPA deployments use HTTPS by default. Docker-internal services
continue to communicate over the private Compose network with HTTP.

## 1. Prepare the environment

```bash
cd docker
cp .env.example .env
```

Set the public names in `.env`:

```env
DEPLOYMENT_MODE="https"
RPA_SERVER_NAME="rpa.example.com"
CASDOOR_SERVER_NAME="auth.example.com"
RPA_HTTPS_REDIRECT_AUTHORITY="rpa.example.com"
CASDOOR_HTTPS_REDIRECT_AUTHORITY="auth.example.com:8443"
CASDOOR_EXTERNAL_ENDPOINT="https://auth.example.com:8443"
```

Copy a trusted certificate chain and matching private key to:

```text
docker/certs/tls.crt
docker/certs/tls.key
```

The certificate must cover both public names. OpenResty fails closed when the
certificate or key is missing or empty.

## 2. Validate and start

```bash
docker compose config
docker compose up -d
docker compose ps
```

Verify the HTTPS endpoints:

```bash
curl https://rpa.example.com/health
curl -I http://127.0.0.1:32742/health
```

The HTTPS health endpoint returns `healthy`; the loopback HTTP endpoint returns
a `308` redirect to HTTPS. Casdoor is available at
`https://auth.example.com:8443` by default and is no longer published directly.

Configure the installed client with the HTTPS gateway URL:

```yaml
remote_addr: https://rpa.example.com/
```

## Common commands

```bash
# View service status
docker compose ps

# View gateway logs
docker compose logs -f openresty-nginx

# Restart the gateway after certificate replacement
docker compose restart openresty-nginx

# Stop services without removing data volumes
docker compose down
```

## Legacy HTTP compatibility

Existing deployments can explicitly select the unencrypted compatibility mode:

```bash
docker compose -f docker-compose.yml -f docker-compose.legacy-http.yml up -d
```

This compatibility file requires Docker Compose 2.24.4 or newer.
HTTP remains bound to loopback by default. Remote HTTP exposure requires an
explicit bind-address change and is intended only for controlled migration or
local development. It sends credentials and workflow data without TLS.

See [HTTPS_DEPLOYMENT.md](./HTTPS_DEPLOYMENT.md) for certificate variables,
custom ports, migration steps, validation, and rollback.

# AstronRPA HTTPS quick start

Public AstronRPA deployments use HTTPS by default. Docker-internal services
continue to communicate over the private Compose network with HTTP.

## 1. Prepare the environment

Prepare a server and domain you control. At the domain's authoritative DNS
provider, point `rpa.example.com` and `auth.example.com` to your public ingress
with A records (or CNAME records for an ingress hostname). NS settings select
the DNS provider; application records must still be added there. Replace all
example names with your own.

The deployer manages DNS, public ports, certificate issuance/private keys, and
renewal. Follow the [HTTPS deployment guide](./HTTPS_DEPLOYMENT.md) for DNS
verification, ACME DNS-01/HTTP-01 validation, and custom-port configuration
before starting the stack.

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
docker compose config --quiet
docker compose up -d mysql casdoor
# After Casdoor initialization (see HTTPS_DEPLOYMENT.md section 1.3):
python3 scripts/sync-casdoor-credentials.py
docker compose up -d
docker compose ps
```

Keep ingress restricted until the default Casdoor administrator password and
unused sample accounts have been secured. The signing keys and application
secrets are generated per deployment; do not publish `.env`. Existing deployments
must follow the rotation steps in [section 1.3](./HTTPS_DEPLOYMENT.md#13-initialize-and-rotate-authentication-credentials).

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

# Validate a replacement certificate before reloading this project's gateway
docker compose exec -T openresty-nginx openresty -t
# Run only if validation succeeds
docker compose exec -T openresty-nginx openresty -s reload

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

See [HTTPS_DEPLOYMENT.md](./HTTPS_DEPLOYMENT.md) for DNS setup, certificate
issuance/renewal, custom ports, migration steps, validation, and rollback.

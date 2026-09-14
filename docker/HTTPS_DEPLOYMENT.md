# HTTPS deployment, migration, and rollback

AstronRPA terminates public TLS in OpenResty. Communication between containers
continues to use the existing private Docker network and HTTP service names.
The default deployment mode is `https`; `legacy-http` is an explicit,
unencrypted compatibility mode.

This is a self-hosted deployment. The deployer provides and maintains the
server, domain registration, DNS records, certificates/private keys, exposed
ports, and certificate renewals. The project supplies the application and
configuration, not a shared hosted endpoint or shared TLS credentials.
Application names and server IP addresses below are documentation examples;
replace them with values you control. Run Compose commands from the deployment's
`docker/` directory, using the same project name, environment, and overrides
throughout.

## 1. Prepare public names and a certificate

### 1.1 Configure DNS

Choose public names for the gateway and authentication service, such as
`rpa.example.com` and `auth.example.com`.

1. Check which authoritative name servers (NS) are assigned to your domain at
   its registrar. Keeping the registrar's default DNS service is sufficient;
   change NS only when moving DNS hosting to another provider. An NS assignment
   selects the DNS provider; it does not point an application name at a server.
2. Open DNS record management at that authoritative DNS provider. Add records
   for both names. For a server with a public IPv4 address, a typical setup is:

   | Record name in the `example.com` zone | Type | Value | TTL |
   | --- | --- | --- | --- |
   | `rpa` | A | `203.0.113.10` | Provider default |
   | `auth` | A | `203.0.113.10` | Provider default |

   `203.0.113.10` is a reserved example address. Use your server's reachable
   public IP, or the address of the ingress you operate. Some DNS consoles ask
   for the full name instead of the relative name. A CNAME can be used instead
   of an A record when pointing a subdomain to an existing ingress hostname;
   do not create both at the same name. Publish AAAA records only when the
   ingress, listener, and network route have been configured and verified for
   IPv6. A stale AAAA record can cause failures even when the A record is correct.
3. Verify both names from the client and n8n networks before configuring TLS:

   ```bash
   nslookup -type=NS example.com
   nslookup rpa.example.com
   nslookup auth.example.com
   ```

   If a lookup returns `NXDOMAIN` or an old address, verify the record name and
   active NS delegation. Compare your normal resolver with an authoritative
   server returned by the NS lookup, or an accessible public resolver:

   ```bash
   nslookup rpa.example.com ns1.dns-provider.example
   nslookup rpa.example.com 1.1.1.1
   ```

   Replace `ns1.dns-provider.example` with your actual authoritative server.
   If that server returns the correct record but a recursive resolver does not,
   allow its cached answer (including a cached negative answer) to expire.
   Corporate DNS policies or split DNS may also require the network
   administrator's help; changing the record repeatedly does not clear those
   caches. Repeat the checks for the authentication name.

DNS records contain an IP address or hostname, **not** `https://`, a port, or a
URL path. Ports are configured separately in Compose and in the public URLs
below. DNS resolution alone does not establish that a port is reachable or
that HTTPS is working.

### 1.2 Obtain and install a certificate

Obtain a certificate from a CA trusted by the intended clients, for example
through an ACME client or a certificate provider's enrollment process. Follow
that provider's instructions to prove control of both names:

- **DNS-01:** publish the provider's TXT challenge values under
  `_acme-challenge.rpa.example.com` and `_acme-challenge.auth.example.com`.
  These temporary TXT records are additional to the application A/CNAME
  records. This method works when public ports 80/443 are unavailable or the
  application uses custom HTTPS ports. Check authoritative TXT resolution
  before submitting validation, and remove obsolete challenge values afterward.
- **HTTP-01:** the CA must reach the specified challenge path over public TCP
  port 80. The default Compose HTTP mapping is loopback-only on host port
  32742 and does not provide an ACME challenge handler. Use HTTP-01 only when
  you control the required public ingress and have configured challenge routing;
  do not replace another application's port-80 listener to make it work.

Use a certificate whose Subject Alternative Name covers both the AstronRPA and
Casdoor public names. Copy the full certificate chain and matching private key
to `docker/certs/`. Real certificates and private keys are ignored by Git.
The supplied gateway configuration uses the same certificate/key pair for both
listeners. Generate and keep the private key within your deployment's secret
management; restrict its filesystem access and ensure the gateway can read it.
Domain names go in the certificate SAN; port numbers do not.

Default names:

```text
docker/certs/tls.crt
docker/certs/tls.key
```

The container refuses to start in HTTPS mode when either file is missing,
empty, or configured as a path outside `/etc/nginx/certs`.

### 1.3 Initialize and rotate authentication credentials

Gateway TLS certificates and Casdoor token-signing certificates have separate
purposes. The bootstrap JSON supplies certificate metadata with empty key
material and empty application secrets. Casdoor generates independent signing
key pairs and application secrets in its own database. `initDataNewOnly=true`
keeps existing keys, users and application settings across restarts; importing
the JSON is not a database migration. Do not turn this setting off to apply
configuration changes.

For a **new deployment**, configure `.env` as described in section 2, then
initialize the private services
before starting RPA (Python 3.6+ is required for the synchronization command):

```bash
docker compose up -d mysql casdoor
# Wait for Casdoor to finish initialization, then copy this deployment's values.
python3 scripts/sync-casdoor-credentials.py
docker compose up -d
```

Run these commands from `docker/`. The script reads the configured application's
Client ID, generated Secret and selected **public** signing certificate from
this project's MySQL container and atomically updates `.env` with mode `0600`.
It does not export signing private keys or print credentials. If initialization
is incomplete, it exits without changing `.env`; retry after Casdoor is ready.
Use `--project-name <existing-project>` when your Compose invocation sets it.
The script targets `docker/.env`, which the supplied services load through
`x-env-file`; a CLI `--env-file` alone does not change that service setting.
Use the same Compose overrides for all commands (for example, `COMPOSE_FILE`
in `.env`). On Windows, also restrict the
file's ACL to the deployment operator; POSIX mode bits do not replace Windows
access control.

Keep public ingress restricted during initial setup. In Casdoor administration,
replace the default administrator password and remove or secure unused sample
users **before** allowing public access. Generated signing keys do not protect
an administrator account that still has a public default password. Protect the
Casdoor database and its backups as private-key stores. Do not publish `.env`,
database exports, or output from `docker compose config`.

For an **existing deployment upgraded from the old bootstrap**:

1. Back up this project's Casdoor database and `.env` with restricted access.
   Apply the sanitized bootstrap JSON and `initDataNewOnly=true` configuration;
   recreate only Casdoor. This preserves existing data but does **not** rotate
   the already imported public keys or secrets.
2. Through Casdoor's authenticated administration API, regenerate both
   `certificate` and `privateKey` for each affected signing certificate,
   including `cert-built-in` and `example-cert`. Casdoor's `update-cert` generates
   a pair when those fields are empty. Keep the certificate names and signing
   algorithm consistent so application bindings and the default-certificate
   fallback select the replacement keys. Do not retain the old public key as a
   trusted fallback. Review custom applications/certificates separately.
3. Rotate affected application Client Secrets, including the built-in application,
   and replace any still-default administrator password. This is part of the same
   repair: a known application Secret can authorize Casdoor API access to signing
   material. Keep application/user IDs stable. Revoke affected OAuth tokens and
   refresh tokens; signing-key rotation does not by itself revoke all stored
   sessions or refresh-token records.
4. Synchronize RPA with the selected application's credentials, then recreate it:

   ```bash
   python3 scripts/sync-casdoor-credentials.py
   docker compose up -d --no-deps --force-recreate rpa-auth
   ```

   The SDK's `casdoor.certificate` now comes from `CASDOOR_CERTIFICATE`, with no
   shared public-key fallback. The current desktop login uses Casdoor sessions;
   offline JWT consumers must also replace their trusted public certificate.
   The synchronization command does not itself rotate credentials or restart
   services. It also supports deployments using internal HTTP/legacy mode.
5. Verify the application binding and exported public certificate, new-token
   acceptance, old-signature and old-Secret rejection, client login/WSS, and n8n
   MCP access. Repeat after restarting Casdoor to prove persistence. Existing
   RPA sessions and n8n API Keys are separate credentials; do not claim that this
   signing-key rotation invalidates them.

Keep all generated credentials in deployment storage, outside tracked source
files. Restoring a pre-rotation database backup restores compromised signing
material too: use such a backup only in isolated recovery and rotate again
before reopening ingress.

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

`RPA_SERVER_NAME` and `CASDOOR_SERVER_NAME` contain hostnames only. The
`*_HTTPS_REDIRECT_AUTHORITY` values contain the external hostname and any
nonstandard port, without a scheme or path. `CASDOOR_EXTERNAL_ENDPOINT` is the
full public HTTPS origin, including a nonstandard port.

For direct access to the supplied Compose gateway, make the selected HTTPS
host ports reachable in the deployment's cloud security group/firewall and,
if needed, NAT rules. If 443/8443 are occupied, select available ports and
update all related values together. For example:

| Setting | Custom-port example |
| --- | --- |
| `RPA_HTTPS_PORT` | `9443` |
| `CASDOOR_HTTPS_PORT` | `9444` |
| `RPA_HTTPS_REDIRECT_AUTHORITY` | `rpa.example.com:9443` |
| `CASDOOR_HTTPS_REDIRECT_AUTHORITY` | `auth.example.com:9444` |
| `CASDOOR_EXTERNAL_ENDPOINT` | `https://auth.example.com:9444` |
| Client `remote_addr` | `https://rpa.example.com:9443/` |
| n8n MCP endpoint | `https://rpa.example.com:9443/api/rpa-openapi/mcp/` |

Keep backend/database ports private. On shared hosts, modify only the
deployment's assigned ports and files. If using a separate ingress, configure
its external URLs and port forwarding consistently, with support for WSS and
MCP streaming; DNS does not configure that ingress automatically.

`CASDOOR_ENDPOINT` must remain the internal HTTP address:

```env
CASDOOR_ENDPOINT="http://rpa-opensource-casdoor:8000"
```

The old HTTP ports are loopback-only by default and return `308` redirects.
They can be exposed temporarily during migration by changing their bind
addresses, but no credential should be sent to an HTTP URL.

## 3. Validate and start

For the first installation, complete the Casdoor initialization and credential
synchronization in section 1.3 before starting the full stack below.

```bash
docker compose config --quiet
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

Configure the n8n MCP Client's Streamable HTTP endpoint as
`https://rpa.example.com/api/rpa-openapi/mcp/`, using an API key in its Bearer
Credential. Keep the key in the credential store rather than the URL or
workflow parameters. With custom ports, update the client, n8n, and validation
URLs as shown above. Use normal certificate validation; an SSH tunnel is not
a deployment requirement.

Install the updated client/Scheduler. Its remote transport derives `https` and
`wss` from this value and validates certificates on the actual connections.
The bundled binary retains local module routing and connects to this transport
over loopback. Older clients that connect that binary directly to HTTPS skip
certificate verification and must be upgraded. Chromium must also run without
the historical `ignore-certificate-errors` switch.

The remote transport uses the standard Python TLS trust context, including the
system roots and an explicitly configured `SSL_CERT_FILE` when a deployment
uses a private CA. Configure Chromium's trust store as appropriate for that CA;
do not disable verification. Session cookies are stored per origin in the
client working directory's `.remote-cookies` directory, with migration of only
the configured origin's existing `.cookie.json` session.

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

## 7. Renew and replace certificates

The supplied Compose stack does not issue or automatically renew certificates.
The deployer must monitor expiry and arrange renewal before the CA's deadline.
Installing an ACME client or adding a gateway reload hook alone does not prove
that unattended renewal works.

For manual DNS-01, complete the TXT challenge again whenever the CA requires
revalidation. For automated DNS-01, use a DNS provider supported by the chosen
ACME client, keep its API credentials outside source control with the minimum
needed DNS permissions, and configure a renewal schedule owned by the
deployment. Do not assume a manual TXT setup can renew unattended.

After a successful renewal:

1. Keep a protected backup of the current certificate and key. Install the new
   full chain and matching key at the configured paths under `docker/certs/`,
   preserving their permissions. A certificate issued into the ACME client's
   own directory is not installed in the gateway until this copy/install step
   has completed.
2. Validate the gateway configuration and reload only this deployment's gateway
   if validation succeeds:

   ```bash
   docker compose exec -T openresty-nginx openresty -t
   # Run only after the preceding command succeeds.
   docker compose exec -T openresty-nginx openresty -s reload
   ```

3. Establish fresh HTTPS connections to both public names and verify the served
   certificate's SAN, chain, and expiry. Recheck client login/WSS and n8n MCP
   initialization/discovery without starting an RPA task. A successful local
   certificate-file check alone does not prove the new certificate is served.
4. If validation fails, retain the running gateway, restore the saved files,
   and correct the certificate/key configuration. Do not work around renewal
   failures by disabling TLS verification or sending credentials over HTTP.

Keep ACME account keys, DNS API tokens, renewal state, and private-key backups
within the deployment's protected storage. Document the renewal owner and
schedule so future operators can maintain the installation.

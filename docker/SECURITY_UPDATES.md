# OpenResty / NGINX security updates

## November 18, 2026 advisories

NGINX published security fixes in **1.30.7 (stable)** and **1.31.9 (mainline)**:

- [Official advisories](https://nginx.org/en/security_advisories.html)
- [Stable release changes](https://nginx.org/en/CHANGES-1.30)
- [OpenResty release changes](https://openresty.org/en/changes.html)

The Compose compatibility default, `openresty/openresty:1.27.1.1-alpine`, is
**not a verified fix for these advisories**. Adding `OPENRESTY_IMAGE` does not
patch existing containers or certify the default. A newer OpenResty version
number alone is also insufficient: check the vendor's security/backport notes
and the actual image digest. The upstream NGINX version thresholds do not
automatically certify an OpenResty build with a different version scheme.

The shipped templates do not enable HTTP/2 or HTTP/3, so their presence as
compiled modules is not proof of exposure to CVE-2026-123007 / CVE-2026-123633
or the HTTP/3 CVE. HTTPS does enable TLS 1.3; review CVE-2026-118899 as well.
The resolver, mail, stream, and alias advisories each have additional
configuration conditions. Inspect the effective configuration, including
external ingress and any custom includes; these defaults do not establish
the state of a deployed service.

This gateway uses Lua for authentication and routing. **Do not replace it
with plain `nginx`**: that removes the required OpenResty modules. Do not
treat `legacy-http` as a security fix or weaken authentication to restore
service. Until a patched compatible image is verified, restrict access to
the affected origin using deployment-level controls and arrange the vendor
update. A patched edge does not protect an origin that remains reachable
directly, and disabling HTTP/2 alone does not address all ten advisories.

## Verify and install a compatible patched image

Run these commands from this deployment's `docker/` directory. Keep the same
Compose project name, `.env`, and overrides used to create the service.

1. Obtain an OpenResty image with vendor-confirmed fixes/backports for the
   applicable advisories and the required architecture. Record its release
   notes, tag and digest; do not guess an unreleased tag. Supply the same value
   to tests and Compose through the shell (or set it in Compose's `.env`):

   ```sh
   export OPENRESTY_IMAGE='registry.example.com/team/openresty@sha256:REPLACE_WITH_VERIFIED_DIGEST'
   docker pull "$OPENRESTY_IMAGE"
   docker run --rm --entrypoint openresty "$OPENRESTY_IMAGE" -V
   docker compose config --images
   ```

   The registry and digest above are placeholders. A service-level `env_file`
   does not supply Compose interpolation values. Use the shell, the project
   `.env`, or the same explicit `--env-file` on every Compose command. Do not
   print a full rendered Compose file into public logs: it can contain secrets.

2. In an isolated test environment with Docker, OpenSSL, curl and Python 3,
   test the candidate image's TLS, proxy and authentication behavior:

   ```sh
   sh tests/test-nginx-config.sh
   sh tests/test-auth-handler.sh
   python3 tests/test-semantic-choice-gateway.py
   ```

   These checks use `OPENRESTY_IMAGE`, create temporary containers/networks and
   remove their own fixtures. They test compatibility, not absence of a CVE;
   retain vendor patch evidence separately. A pass against the old default
   cannot establish that the vulnerability is fixed.

3. During the deployment's maintenance window, recreate only the gateway:

   ```sh
   docker compose up -d --no-deps --force-recreate openresty-nginx
   docker compose exec -T openresty-nginx openresty -t
   docker compose exec -T openresty-nginx openresty -V
   docker inspect --format '{{.Image}}' "$(docker compose ps -q openresty-nginx)"
   ```

   Re-read the container image ID/digest, effective configuration, HTTPS
   certificate, login, valid and invalid authentication, WebSocket/SSE and
   API behavior from the actual client network. Preserve the pre-update image
   and configuration for diagnosis, but do not silently roll back to a known
   affected image and declare the incident resolved. No database or volume
   deletion is needed for this proxy update. A configuration reload alone
   does not replace the running NGINX/OpenResty executable.

The project cannot promise a one-minute outage for every self-hosted deployment;
download and compatibility-test the image before the agreed maintenance window.

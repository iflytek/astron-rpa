#!/bin/sh
set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
DOCKER_DIR=$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd)
TEST_ROOT=$(mktemp -d)
CONTAINER_NAME="astron-rpa-nginx-test-$$"

mkdir -p "$TEST_ROOT/compose" "$TEST_ROOT/logs"
cp "$DOCKER_DIR/docker-compose.yml" "$TEST_ROOT/compose/"
cp "$DOCKER_DIR/docker-compose.legacy-http.yml" "$TEST_ROOT/compose/"
cp "$DOCKER_DIR/.env.example" "$TEST_ROOT/compose/.env"

cleanup() {
    docker rm -f "$CONTAINER_NAME" >/dev/null 2>&1 || true
    rm -rf "$TEST_ROOT"
}
trap cleanup EXIT HUP INT TERM

openssl req -x509 -newkey rsa:2048 -nodes -days 1 \
    -subj '/CN=localhost' \
    -addext 'subjectAltName=DNS:localhost' \
    -keyout "$TEST_ROOT/tls.key" \
    -out "$TEST_ROOT/tls.crt" >/dev/null 2>&1

docker compose --project-directory "$TEST_ROOT/compose" \
    -f "$TEST_ROOT/compose/docker-compose.yml" \
    config --format json > "$TEST_ROOT/compose-https.json"
docker compose --project-directory "$TEST_ROOT/compose" \
    -f "$TEST_ROOT/compose/docker-compose.yml" \
    -f "$TEST_ROOT/compose/docker-compose.legacy-http.yml" \
    config --format json > "$TEST_ROOT/compose-legacy-http.json"

python3 - "$TEST_ROOT/compose-https.json" "$TEST_ROOT/compose-legacy-http.json" <<'PY'
import json
import sys


def load(path):
    with open(path, encoding="utf-8") as config_file:
        return json.load(config_file)


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def assert_port(service, target, published, host_ip):
    matches = [port for port in service.get("ports", []) if port.get("target") == target]
    require(len(matches) == 1, f"expected exactly one mapping for container port {target}")
    mapping = matches[0]
    require(str(mapping.get("published")) == str(published), f"unexpected published port for {target}: {mapping}")
    require(mapping.get("host_ip") == host_ip, f"unexpected bind address for {target}: {mapping}")


https_config = load(sys.argv[1])
legacy_config = load(sys.argv[2])

gateway = https_config["services"]["openresty-nginx"]
require(gateway["environment"]["DEPLOYMENT_MODE"] == "https", "HTTPS must be the default deployment mode")
require(gateway["environment"]["RPA_SERVER_NAME"] == "localhost", "RPA server name default is missing")
require(gateway["environment"]["CASDOOR_SERVER_NAME"] == "localhost", "Casdoor server name default is missing")
require(gateway["environment"]["TLS_CERTIFICATE_FILE"] == "tls.crt", "TLS certificate default is missing")
require(gateway["environment"]["TLS_CERTIFICATE_KEY_FILE"] == "tls.key", "TLS private-key default is missing")
assert_port(gateway, 80, 32742, "127.0.0.1")
assert_port(gateway, 8080, 8000, "127.0.0.1")
assert_port(gateway, 443, 443, "0.0.0.0")
assert_port(gateway, 8443, 8443, "0.0.0.0")
require(gateway["entrypoint"] == ["/bin/sh", "/etc/nginx/render-config.sh"], "renderer entrypoint is missing")
require("8090/health" in " ".join(gateway["healthcheck"]["test"]), "internal health check is not configured")
require(
    any(volume.get("target") == "/etc/nginx/certs" and volume.get("read_only") for volume in gateway["volumes"]),
    "certificate directory must be mounted read-only",
)

casdoor = https_config["services"]["casdoor"]
require(not casdoor.get("ports"), "Casdoor must not be published directly")
auth = https_config["services"]["rpa-auth"]
require(auth["environment"]["SESSION_COOKIE_SECURE"] == "true", "HTTPS session cookie must default to Secure")
require(
    auth["environment"]["CASDOOR_EXTERNAL_ENDPOINT"] == "https://localhost:8443",
    "Casdoor external endpoint must default to HTTPS",
)
require(
    auth["environment"]["CASDOOR_ENDPOINT"] == "http://rpa-opensource-casdoor:8000",
    "Docker-internal Casdoor endpoint must remain HTTP",
)

legacy_gateway = legacy_config["services"]["openresty-nginx"]
require(legacy_gateway["environment"]["DEPLOYMENT_MODE"] == "legacy-http", "legacy mode override is missing")
assert_port(legacy_gateway, 80, 32742, "127.0.0.1")
assert_port(legacy_gateway, 8080, 8000, "127.0.0.1")
require(
    not any(port.get("target") in (443, 8443) for port in legacy_gateway.get("ports", [])),
    "legacy mode must not publish unused HTTPS ports",
)
legacy_auth = legacy_config["services"]["rpa-auth"]
require(legacy_auth["environment"]["SESSION_COOKIE_SECURE"] == "false", "legacy mode must disable Secure cookies")
require(
    legacy_auth["environment"]["CASDOOR_EXTERNAL_ENDPOINT"] == "http://127.0.0.1:8000",
    "legacy Casdoor endpoint override is missing",
)
PY

run_nginx_test() {
    mode="$1"
    docker run --rm \
        --add-host resource-service:127.0.0.1 \
        --add-host robot-service:127.0.0.1 \
        --add-host ai-service:127.0.0.1 \
        --add-host openapi-service:127.0.0.1 \
        --add-host rpa-auth:127.0.0.1 \
        --add-host casdoor:127.0.0.1 \
        -e DEPLOYMENT_MODE="$mode" \
        -v "$DOCKER_DIR/volumes/nginx/render-config.sh:/etc/nginx/render-config.sh:ro" \
        -v "$DOCKER_DIR/volumes/nginx/templates:/etc/nginx/templates:ro" \
        -v "$DOCKER_DIR/volumes/nginx/includes:/etc/nginx/includes:ro" \
        -v "$DOCKER_DIR/volumes/nginx/lua:/usr/local/openresty/nginx/lua:ro" \
        -v "$TEST_ROOT:/etc/nginx/certs:ro" \
        --entrypoint /bin/sh \
        openresty/openresty:1.27.1.1-alpine \
        /etc/nginx/render-config.sh /usr/local/openresty/bin/openresty -t
}

run_nginx_test https
run_nginx_test legacy-http

docker run -d --name "$CONTAINER_NAME" \
    --add-host resource-service:127.0.0.1 \
    --add-host robot-service:127.0.0.1 \
    --add-host ai-service:127.0.0.1 \
    --add-host openapi-service:127.0.0.1 \
    --add-host rpa-auth:127.0.0.1 \
    --add-host casdoor:127.0.0.1 \
    -e DEPLOYMENT_MODE=https \
    -p 127.0.0.1::80 \
    -p 127.0.0.1::443 \
    -p 127.0.0.1::8443 \
    -v "$DOCKER_DIR/volumes/nginx/render-config.sh:/etc/nginx/render-config.sh:ro" \
    -v "$DOCKER_DIR/volumes/nginx/templates:/etc/nginx/templates:ro" \
    -v "$DOCKER_DIR/volumes/nginx/includes:/etc/nginx/includes:ro" \
    -v "$DOCKER_DIR/volumes/nginx/lua:/usr/local/openresty/nginx/lua:ro" \
    -v "$TEST_ROOT:/etc/nginx/certs:ro" \
    -v "$TEST_ROOT/logs:/usr/local/openresty/nginx/logs" \
    --entrypoint /bin/sh \
    openresty/openresty:1.27.1.1-alpine \
    /etc/nginx/render-config.sh /usr/local/openresty/bin/openresty -g 'daemon off;' >/dev/null

HTTP_PORT=$(docker port "$CONTAINER_NAME" 80/tcp | sed 's/.*://')
HTTPS_PORT=$(docker port "$CONTAINER_NAME" 443/tcp | sed 's/.*://')
CASDOOR_HTTPS_PORT=$(docker port "$CONTAINER_NAME" 8443/tcp | sed 's/.*://')

attempt=0
until curl --silent --fail --insecure "https://127.0.0.1:$HTTPS_PORT/health" | grep -q healthy; do
    attempt=$((attempt + 1))
    if [ "$attempt" -ge 20 ]; then
        echo 'HTTPS health endpoint did not become ready' >&2
        docker logs "$CONTAINER_NAME" >&2
        exit 1
    fi
    sleep 1
done

headers=$(curl --silent --dump-header - --output /dev/null "http://127.0.0.1:$HTTP_PORT/health?key=do-not-log")
printf '%s' "$headers" | grep -q '^HTTP/1.1 308'
printf '%s' "$headers" | grep -qi '^Location: https://localhost/health?key=do-not-log'

# A 502 response is expected without the Casdoor upstream; a completed HTTPS
# exchange proves that the dedicated TLS listener is active.
curl --silent --insecure --output /dev/null "https://127.0.0.1:$CASDOOR_HTTPS_PORT/?key=casdoor-do-not-log"

if grep -Eq 'do-not-log|casdoor-do-not-log' "$TEST_ROOT/logs/access.log"; then
    echo 'sanitized access log contains a query parameter' >&2
    exit 1
fi

docker rm -f "$CONTAINER_NAME" >/dev/null

docker run -d --name "$CONTAINER_NAME" \
    --add-host resource-service:127.0.0.1 \
    --add-host robot-service:127.0.0.1 \
    --add-host ai-service:127.0.0.1 \
    --add-host openapi-service:127.0.0.1 \
    --add-host rpa-auth:127.0.0.1 \
    --add-host casdoor:127.0.0.1 \
    -e DEPLOYMENT_MODE=legacy-http \
    -p 127.0.0.1::80 \
    -p 127.0.0.1::8080 \
    -v "$DOCKER_DIR/volumes/nginx/render-config.sh:/etc/nginx/render-config.sh:ro" \
    -v "$DOCKER_DIR/volumes/nginx/templates:/etc/nginx/templates:ro" \
    -v "$DOCKER_DIR/volumes/nginx/includes:/etc/nginx/includes:ro" \
    -v "$DOCKER_DIR/volumes/nginx/lua:/usr/local/openresty/nginx/lua:ro" \
    -v "$TEST_ROOT:/etc/nginx/certs:ro" \
    -v "$TEST_ROOT/logs:/usr/local/openresty/nginx/logs" \
    --entrypoint /bin/sh \
    openresty/openresty:1.27.1.1-alpine \
    /etc/nginx/render-config.sh /usr/local/openresty/bin/openresty -g 'daemon off;' >/dev/null

LEGACY_HTTP_PORT=$(docker port "$CONTAINER_NAME" 80/tcp | sed 's/.*://')
LEGACY_CASDOOR_PORT=$(docker port "$CONTAINER_NAME" 8080/tcp | sed 's/.*://')

attempt=0
until curl --silent --fail "http://127.0.0.1:$LEGACY_HTTP_PORT/health" | grep -q healthy; do
    attempt=$((attempt + 1))
    if [ "$attempt" -ge 20 ]; then
        echo 'legacy-http health endpoint did not become ready' >&2
        docker logs "$CONTAINER_NAME" >&2
        exit 1
    fi
    sleep 1
done

# A 502 response is expected without the Casdoor upstream; a completed HTTP
# exchange proves that the legacy compatibility proxy is active.
curl --silent --output /dev/null "http://127.0.0.1:$LEGACY_CASDOOR_PORT/"

echo 'OpenResty HTTPS and legacy configuration tests passed.'

#!/bin/sh
set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
DOCKER_DIR=$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd)
TEST_ROOT=$(mktemp -d)
trap 'rm -rf "$TEST_ROOT"' EXIT HUP INT TERM

mkdir -p "$TEST_ROOT/certs" "$TEST_ROOT/conf.d" "$TEST_ROOT/templates"
cp "$DOCKER_DIR/volumes/nginx/templates/https.conf.template" "$TEST_ROOT/templates/"
cp "$DOCKER_DIR/volumes/nginx/templates/legacy-http.conf.template" "$TEST_ROOT/templates/"
printf 'test certificate\n' > "$TEST_ROOT/certs/test.crt"
printf 'test private key\n' > "$TEST_ROOT/certs/test.key"
: > "$TEST_ROOT/certs/empty.crt"
: > "$TEST_ROOT/certs/empty.key"

run_renderer() {
    NGINX_CONFIG_ROOT="$TEST_ROOT" \
    TLS_CERTIFICATE_FILE=test.crt \
    TLS_CERTIFICATE_KEY_FILE=test.key \
    RPA_SERVER_NAME=rpa.example.test \
    CASDOOR_SERVER_NAME=auth.example.test \
    RPA_HTTPS_REDIRECT_AUTHORITY=rpa.example.test \
    CASDOOR_HTTPS_REDIRECT_AUTHORITY=auth.example.test:8443 \
        sh "$DOCKER_DIR/volumes/nginx/render-config.sh" true
}

unset DEPLOYMENT_MODE
run_renderer
grep -q 'listen 443 ssl;' "$TEST_ROOT/conf.d/default.conf"
grep -q 'listen 8443 ssl;' "$TEST_ROOT/conf.d/default.conf"
grep -q 'server_name rpa.example.test;' "$TEST_ROOT/conf.d/default.conf"
grep -q 'server_name auth.example.test;' "$TEST_ROOT/conf.d/default.conf"
grep -q 'https://rpa.example.test$request_uri' "$TEST_ROOT/conf.d/default.conf"
grep -q 'https://auth.example.test:8443$request_uri' "$TEST_ROOT/conf.d/default.conf"
grep -q '/etc/nginx/certs/test.crt' "$TEST_ROOT/conf.d/default.conf"
grep -q '/etc/nginx/certs/test.key' "$TEST_ROOT/conf.d/default.conf"
grep -q 'include /etc/nginx/includes/gateway-routes.conf;' "$TEST_ROOT/conf.d/default.conf"
grep -q 'include /etc/nginx/includes/casdoor-proxy.conf;' "$TEST_ROOT/conf.d/default.conf"
[ "$(grep -c 'sanitized_access;' "$TEST_ROOT/conf.d/default.conf")" -eq 4 ]
if grep -q '@@' "$TEST_ROOT/conf.d/default.conf"; then
    echo 'HTTPS rendering left unresolved placeholders' >&2
    exit 1
fi

DEPLOYMENT_MODE=legacy-http run_renderer 2> "$TEST_ROOT/legacy-warning.log"
grep -q 'WARNING: legacy-http' "$TEST_ROOT/legacy-warning.log"
grep -q 'listen 80;' "$TEST_ROOT/conf.d/default.conf"
grep -q 'include /etc/nginx/includes/gateway-routes.conf;' "$TEST_ROOT/conf.d/default.conf"
grep -q 'include /etc/nginx/includes/casdoor-proxy.conf;' "$TEST_ROOT/conf.d/default.conf"
[ "$(grep -c 'sanitized_access;' "$TEST_ROOT/conf.d/default.conf")" -eq 2 ]
if grep -q 'listen 443 ssl;' "$TEST_ROOT/conf.d/default.conf"; then
    echo 'legacy-http unexpectedly enables TLS listeners' >&2
    exit 1
fi
if grep -q '@@' "$TEST_ROOT/conf.d/default.conf"; then
    echo 'legacy-http rendering left unresolved placeholders' >&2
    exit 1
fi

grep -q '\$request_method \$uri \$server_protocol' "$DOCKER_DIR/volumes/nginx/includes/http-common.conf"
if grep -Eq '\$request_uri|\$http_referer' "$DOCKER_DIR/volumes/nginx/includes/http-common.conf"; then
    echo 'sanitized access log includes query parameters or Referer' >&2
    exit 1
fi

while IFS= read -r route; do
    grep -Fq "$route" "$DOCKER_DIR/volumes/nginx/includes/gateway-routes.conf" || {
        echo "gateway route missing: $route" >&2
        exit 1
    }
done <<'ROUTES'
location /api/resource/ {
location /api/robot/ {
location /api/rpa-ai-service/ {
location ~ ^/api/rpa-openapi/mcp/?$ {
location /api/rpa-openapi/ws {
location /api/rpa-openapi/ {
location /api/rpa-auth/ {
location /api/casdoor/ {
location /health {
location /favicon.ico {
location / {
ROUTES

grep -Fq 'proxy_set_header Connection "upgrade";' "$DOCKER_DIR/volumes/nginx/includes/gateway-routes.conf"
if grep -Rq 'proxy_pass https://' "$DOCKER_DIR/volumes/nginx/includes"; then
    echo 'Docker-internal upstream traffic was unexpectedly changed to HTTPS' >&2
    exit 1
fi

if DEPLOYMENT_MODE=invalid run_renderer > /dev/null 2>&1; then
    echo 'invalid deployment mode was accepted' >&2
    exit 1
fi

if RPA_SERVER_NAME='bad/name' NGINX_CONFIG_ROOT="$TEST_ROOT" \
    DEPLOYMENT_MODE=legacy-http sh "$DOCKER_DIR/volumes/nginx/render-config.sh" true > /dev/null 2>&1; then
    echo 'unsafe server name was accepted' >&2
    exit 1
fi

if NGINX_CONFIG_ROOT="$TEST_ROOT" DEPLOYMENT_MODE=https \
    TLS_CERTIFICATE_FILE=missing.crt TLS_CERTIFICATE_KEY_FILE=test.key \
    sh "$DOCKER_DIR/volumes/nginx/render-config.sh" true > /dev/null 2>&1; then
    echo 'missing TLS certificate was accepted' >&2
    exit 1
fi

if NGINX_CONFIG_ROOT="$TEST_ROOT" DEPLOYMENT_MODE=https \
    TLS_CERTIFICATE_FILE=test.crt TLS_CERTIFICATE_KEY_FILE=missing.key \
    sh "$DOCKER_DIR/volumes/nginx/render-config.sh" true > /dev/null 2>&1; then
    echo 'missing TLS private key was accepted' >&2
    exit 1
fi

if NGINX_CONFIG_ROOT="$TEST_ROOT" DEPLOYMENT_MODE=https \
    TLS_CERTIFICATE_FILE=empty.crt TLS_CERTIFICATE_KEY_FILE=test.key \
    sh "$DOCKER_DIR/volumes/nginx/render-config.sh" true > /dev/null 2>&1; then
    echo 'empty TLS certificate was accepted' >&2
    exit 1
fi

if NGINX_CONFIG_ROOT="$TEST_ROOT" DEPLOYMENT_MODE=https \
    TLS_CERTIFICATE_FILE=test.crt TLS_CERTIFICATE_KEY_FILE=empty.key \
    sh "$DOCKER_DIR/volumes/nginx/render-config.sh" true > /dev/null 2>&1; then
    echo 'empty TLS private key was accepted' >&2
    exit 1
fi

if RPA_HTTPS_REDIRECT_AUTHORITY='bad/authority' NGINX_CONFIG_ROOT="$TEST_ROOT" \
    DEPLOYMENT_MODE=https TLS_CERTIFICATE_FILE=test.crt TLS_CERTIFICATE_KEY_FILE=test.key \
    sh "$DOCKER_DIR/volumes/nginx/render-config.sh" true > /dev/null 2>&1; then
    echo 'unsafe redirect authority was accepted' >&2
    exit 1
fi

if NGINX_CONFIG_ROOT="$TEST_ROOT" DEPLOYMENT_MODE=https \
    TLS_CERTIFICATE_FILE='../outside.crt' TLS_CERTIFICATE_KEY_FILE=test.key \
    sh "$DOCKER_DIR/volumes/nginx/render-config.sh" true > /dev/null 2>&1; then
    echo 'unsafe certificate path was accepted' >&2
    exit 1
fi

echo 'OpenResty configuration renderer tests passed.'

#!/bin/sh
set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
DOCKER_DIR=$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd)
TEST_ROOT=$(mktemp -d)
NETWORK_NAME="astron-rpa-auth-test-$$"
MOCK_NAME="astron-rpa-auth-mock-$$"
GATEWAY_NAME="astron-rpa-auth-gateway-$$"

cleanup() {
    docker rm -f "$GATEWAY_NAME" "$MOCK_NAME" >/dev/null 2>&1 || true
    docker network rm "$NETWORK_NAME" >/dev/null 2>&1 || true
    rm -rf "$TEST_ROOT"
}
trap cleanup EXIT HUP INT TERM

cat > "$TEST_ROOT/mock.conf" <<'EOF'
worker_processes 1;
events { worker_connections 32; }
http {
    server {
        listen 8040;

        location = /api/robot/user/info {
            default_type application/json;
            content_by_lua_block {
                local cookie = ngx.var.http_cookie or ""
                if cookie:find("valid-token", 1, true) then
                    ngx.say('{"code":"000000","data":{"id":"user-123"}}')
                elseif cookie:find("scalar-token", 1, true) then
                    ngx.say('{"code":"000000","data":"not-an-object"}')
                elseif cookie:find("malformed-token", 1, true) then
                    ngx.say('{invalid-json')
                else
                    ngx.say('{"code":"000000","data":null}')
                end
            }
        }
    }
}
EOF

cat > "$TEST_ROOT/gateway.conf" <<'EOF'
worker_processes 1;
events { worker_connections 32; }
http {
    lua_package_path "/usr/local/openresty/nginx/lua/?.lua;;";
    resolver 127.0.0.11 ipv6=off;

    server {
        listen 8080;
        set $context_type "HTTP";

        location = /protected {
            access_by_lua_file /usr/local/openresty/nginx/lua/auth_handler.lua;
            content_by_lua_block {
                ngx.say(ngx.req.get_headers()["user_id"] or "missing")
            }
        }
    }
}
EOF

docker network create "$NETWORK_NAME" >/dev/null

docker run -d --name "$MOCK_NAME" \
    --network "$NETWORK_NAME" \
    --network-alias robot-service \
    -v "$TEST_ROOT/mock.conf:/usr/local/openresty/nginx/conf/nginx.conf:ro" \
    openresty/openresty:1.27.1.1-alpine >/dev/null

docker run -d --name "$GATEWAY_NAME" \
    --network "$NETWORK_NAME" \
    -p 127.0.0.1::8080 \
    -v "$TEST_ROOT/gateway.conf:/usr/local/openresty/nginx/conf/nginx.conf:ro" \
    -v "$DOCKER_DIR/volumes/nginx/lua:/usr/local/openresty/nginx/lua:ro" \
    openresty/openresty:1.27.1.1-alpine >/dev/null

GATEWAY_PORT=$(docker port "$GATEWAY_NAME" 8080/tcp | sed 's/.*://')
attempt=0
until curl --silent --fail --header 'Token: valid-token' "http://127.0.0.1:$GATEWAY_PORT/protected" | grep -q '^user-123$'; do
    attempt=$((attempt + 1))
    if [ "$attempt" -ge 20 ]; then
        echo 'authentication test gateway did not become ready' >&2
        docker logs "$MOCK_NAME" >&2
        docker logs "$GATEWAY_NAME" >&2
        exit 1
    fi
    sleep 1
done

assert_status_and_body() {
    token="$1"
    expected_status="$2"
    expected_body="$3"
    response_file="$TEST_ROOT/$token-response"

    status=$(curl --silent --output "$response_file" --write-out '%{http_code}' \
        --header "Token: $token" "http://127.0.0.1:$GATEWAY_PORT/protected")
    if [ "$status" != "$expected_status" ]; then
        echo "unexpected status for $token: $status" >&2
        cat "$response_file" >&2
        exit 1
    fi
    if ! grep -q "$expected_body" "$response_file"; then
        echo "unexpected response for $token" >&2
        cat "$response_file" >&2
        exit 1
    fi
}

assert_status_and_body null-token 401 'invalid or expired'
assert_status_and_body scalar-token 401 'invalid or expired'
assert_status_and_body malformed-token 500 'Invalid auth service response'

echo 'OpenResty authentication response validation tests passed.'

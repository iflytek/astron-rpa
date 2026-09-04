#!/bin/sh
set -eu

fail() {
    echo "OpenResty configuration error: $*" >&2
    exit 1
}

validate_name() {
    variable_name="$1"
    variable_value="$2"
    printf '%s' "$variable_value" | grep -Eq '^[A-Za-z0-9._-]+$' ||
        fail "$variable_name must be one DNS name, IPv4 address, or underscore"
}

validate_authority() {
    variable_name="$1"
    variable_value="$2"
    printf '%s' "$variable_value" | grep -Eq '^[A-Za-z0-9._:-]+$' ||
        fail "$variable_name must contain only a host and optional port"
}

validate_file_name() {
    variable_name="$1"
    variable_value="$2"
    printf '%s' "$variable_value" | grep -Eq '^[A-Za-z0-9._-]+$' ||
        fail "$variable_name must be a file name inside /etc/nginx/certs"
}

render_template() {
    source_file="$1"
    destination_file="$2"
    sed \
        -e "s|@@RPA_SERVER_NAME@@|$RPA_SERVER_NAME|g" \
        -e "s|@@CASDOOR_SERVER_NAME@@|$CASDOOR_SERVER_NAME|g" \
        -e "s|@@RPA_HTTPS_REDIRECT_AUTHORITY@@|$RPA_HTTPS_REDIRECT_AUTHORITY|g" \
        -e "s|@@CASDOOR_HTTPS_REDIRECT_AUTHORITY@@|$CASDOOR_HTTPS_REDIRECT_AUTHORITY|g" \
        -e "s|@@TLS_CERTIFICATE_FILE@@|$TLS_CERTIFICATE_FILE|g" \
        -e "s|@@TLS_CERTIFICATE_KEY_FILE@@|$TLS_CERTIFICATE_KEY_FILE|g" \
        "$source_file" > "$destination_file"
}

DEPLOYMENT_MODE="${DEPLOYMENT_MODE:-https}"
NGINX_CONFIG_ROOT="${NGINX_CONFIG_ROOT:-/etc/nginx}"
RPA_SERVER_NAME="${RPA_SERVER_NAME:-localhost}"
CASDOOR_SERVER_NAME="${CASDOOR_SERVER_NAME:-localhost}"
RPA_HTTPS_REDIRECT_AUTHORITY="${RPA_HTTPS_REDIRECT_AUTHORITY:-localhost}"
CASDOOR_HTTPS_REDIRECT_AUTHORITY="${CASDOOR_HTTPS_REDIRECT_AUTHORITY:-localhost:8443}"
TLS_CERTIFICATE_FILE="${TLS_CERTIFICATE_FILE:-tls.crt}"
TLS_CERTIFICATE_KEY_FILE="${TLS_CERTIFICATE_KEY_FILE:-tls.key}"

validate_name RPA_SERVER_NAME "$RPA_SERVER_NAME"
validate_name CASDOOR_SERVER_NAME "$CASDOOR_SERVER_NAME"

case "$DEPLOYMENT_MODE" in
    https)
        validate_authority RPA_HTTPS_REDIRECT_AUTHORITY "$RPA_HTTPS_REDIRECT_AUTHORITY"
        validate_authority CASDOOR_HTTPS_REDIRECT_AUTHORITY "$CASDOOR_HTTPS_REDIRECT_AUTHORITY"
        validate_file_name TLS_CERTIFICATE_FILE "$TLS_CERTIFICATE_FILE"
        validate_file_name TLS_CERTIFICATE_KEY_FILE "$TLS_CERTIFICATE_KEY_FILE"

        certificate_path="$NGINX_CONFIG_ROOT/certs/$TLS_CERTIFICATE_FILE"
        certificate_key_path="$NGINX_CONFIG_ROOT/certs/$TLS_CERTIFICATE_KEY_FILE"
        [ -s "$certificate_path" ] || fail "TLS certificate not found or empty: $certificate_path"
        [ -s "$certificate_key_path" ] || fail "TLS private key not found or empty: $certificate_key_path"

        template="$NGINX_CONFIG_ROOT/templates/https.conf.template"
        ;;
    legacy-http)
        template="$NGINX_CONFIG_ROOT/templates/legacy-http.conf.template"
        echo "WARNING: legacy-http sends credentials and workflow data without TLS." >&2
        ;;
    *)
        fail "DEPLOYMENT_MODE must be https or legacy-http"
        ;;
esac

temporary_config="$NGINX_CONFIG_ROOT/conf.d/default.conf.tmp"
render_template "$template" "$temporary_config"
mv "$temporary_config" "$NGINX_CONFIG_ROOT/conf.d/default.conf"

exec "$@"

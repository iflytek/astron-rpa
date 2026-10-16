-- OpenAPI has two identity sources: external API keys and authenticated
-- desktop sessions. Never let a public caller supply the gateway identity.
local json = require("cjson")
local headers = ngx.req.get_headers()
local diagnostic_user = headers["user_id"]
ngx.req.clear_header("user_id")
ngx.req.clear_header("X-User-Id")
ngx.req.clear_header("user-info")

-- rewrite has already removed /api/rpa-openapi; use the normalized URI.
local path = ngx.var.uri
local external = path == "/workflows/execute"
    or path == "/workflows/execute-async"
    or path == "/workflows/integration"
    or path == "/workflows/stop-current"
    or path == "/workflows/copy-workflow"
    or path == "/health/local-check"
    or path == "/health/remote-check"
    or path == "/executions/get"
    or path:match("^/executions/[^/]+$")
    or path:match("^/executions/[^/]+/cancel$")
local hybrid = path == "/workflows/get" or path:match("^/workflows/get/[^/]+$")
local credentials = headers["authorization"] ~= nil or headers["x-api-key"] ~= nil
    or ngx.req.get_uri_args().key ~= nil

if external or (hybrid and credentials) then
    -- The service validates missing, duplicate, malformed, conflicting and
    -- revoked credentials. No fallback to desktop identity is permitted.
    if path == "/health/local-check" and diagnostic_user then
        -- Diagnostic comparison only; this value never selects a resource.
        ngx.req.set_header("user_id", diagnostic_user)
    end
    return
end

if credentials then
    ngx.status = 401
    ngx.header["Content-Type"] = "application/json"
    ngx.say(json.encode({detail = "Session authentication required"}))
    return ngx.exit(401)
end

-- Execute on every request. Separate loading/calling permits cosocket yields;
-- dofile introduces a C-call boundary and require caches the script's first call.
local authenticate = assert(loadfile("/usr/local/openresty/nginx/lua/auth_handler.lua"))
authenticate()

-- Paid semantic decisions accept verified desktop sessions, not provider keys.
local headers = ngx.req.get_headers()
ngx.req.clear_header("user_id")
ngx.req.clear_header("X-User-Id")
ngx.req.clear_header("user-info")

if headers["authorization"] or headers["x-api-key"] or ngx.req.get_uri_args().key then
    ngx.status = 401
    ngx.header["Content-Type"] = "application/json"
    ngx.say(require("cjson").encode({detail = "Session authentication required"}))
    return ngx.exit(401)
end

-- As in openapi_auth.lua, load/call per request rather than caching with require.
local authenticate = assert(loadfile("/usr/local/openresty/nginx/lua/auth_handler.lua"))
authenticate()

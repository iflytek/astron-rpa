-- Run from the repository root with LuaJIT; only ngx and the auth service are mocked.
local original_loadfile = loadfile
local handler = (arg and arg[1]) or "docker/volumes/nginx/lua/decision_auth.lua"
loadfile = function(path)
    if path == "/usr/local/openresty/nginx/lua/auth_handler.lua" then
        path = "docker/volumes/nginx/lua/auth_handler.lua"
    end
    return original_loadfile(path)
end

local function check(name, extra, cookie, query, expected_status, expected_user)
    local headers = {user_id = "attacker", ["x-user-id"] = "attacker"}
    for key, value in pairs(extra) do headers[key] = value end
    local auth_calls = 0
    local valid = false
    package.loaded["resty.http"] = {
        new = function()
            return {request_uri = function(_, url, options)
                auth_calls = auth_calls + 1
                assert(url == "http://robot-service:8040/api/robot/user/info")
                valid = options.headers.Cookie:find("=valid-token", 1, true) ~= nil
                return {status = 200, body = "mock-auth-response"}, nil
            end}
        end
    }
    package.loaded["cjson"] = {
        encode = function() return "{}" end,
        decode = function()
            return {code = "000000", data = valid and {id = "real-user"} or nil}
        end
    }
    ngx = {
        var = {uri = "/v1/decision/choice", http_cookie = cookie},
        DEBUG = 0, ERR = 1, WARN = 2, HTTP_OK = 200,
        HTTP_UNAUTHORIZED = 401, HTTP_INTERNAL_SERVER_ERROR = 500,
        status = 200, header = {},
        log = function() end, say = function() end,
        exit = function(code) error({status = code}, 0) end,
        req = {
            get_headers = function() return headers end,
            get_uri_args = function() return query or {} end,
            clear_header = function(key) headers[key:lower()] = nil end,
            set_header = function(key, value) headers[key:lower()] = value end,
        }
    }
    local ok, result = pcall(assert(original_loadfile(handler)))
    if not ok and (type(result) ~= "table" or not result.status) then error(result) end
    local status = ok and ngx.status or result.status
    assert(status == expected_status, name .. ": expected " .. expected_status .. ", got " .. status)
    assert(headers["x-user-id"] == nil, name .. ": untrusted identity survived")
    assert(headers.user_id == expected_user, name .. ": incorrect authenticated identity")
    if expected_user then assert(auth_calls == 1, name .. ": session was not verified") end
end

check("arbitrary bearer", {authorization = "Bearer arbitrary"}, nil, nil, 401)
check("missing session", {}, nil, nil, 401)
check("API key", {["x-api-key"] = "arbitrary"}, nil, nil, 401)
check("query credential", {}, nil, {key = "arbitrary"}, 401)
check("verified token", {token = "valid-token"}, nil, nil, 200, "real-user")
check("verified cookie", {}, "SESSION=valid-token", nil, 200, "real-user")
check("expired token", {token = "expired-token"}, nil, nil, 401)
check("mixed bearer and cookie", {authorization = "Bearer arbitrary"}, "SESSION=valid-token", nil, 401)
print("8 semantic choice gateway identity checks passed")

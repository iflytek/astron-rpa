package main

import (
	"flag"
	"fmt"
	"io"
	"local-route/proxy"
	"net"
	"net/http"
	"os"
	"path"
	"strings"
	"time"

	"github.com/gin-contrib/cors"
	"github.com/gin-gonic/gin"
	"github.com/sirupsen/logrus"
)

// httpRegister and wxRegister hold module-name to proxy config mappings.
var (
	httpRegister = make(map[string]proxy.ConfigMap)
	wxRegister   = make(map[string]proxy.ConfigMap)
)

var lanTerminalRoutes = map[string]bool{
	"start":       true,
	"end":         true,
	"ping":        true,
	"terminal_id": true,
}

var lanExecutorRoutes = map[string]bool{
	"run_list":     true,
	"run_sync":     true,
	"run":          true,
	"status":       true,
	"stop":         true,
	"stop_current": true,
	"stop_list":    true,
}

func isLocalRequest(r *http.Request) bool {
	host, _, err := net.SplitHostPort(r.RemoteAddr)
	if err != nil {
		host = r.RemoteAddr
	}
	ip := net.ParseIP(host)
	return ip != nil && ip.IsLoopback()
}

func isAllowedRoute(segs []string, index int, allowed map[string]bool) bool {
	return len(segs) == index+1 && allowed[segs[index]]
}

func isLanAccessiblePath(urlPath string) bool {
	segs := strings.Split(strings.Trim(urlPath, "/"), "/")
	if len(segs) == 0 || segs[0] == "" {
		return false
	}
	switch segs[0] {
	case "executor":
		return isAllowedRoute(segs, 1, lanExecutorRoutes)
	case "terminal":
		return isAllowedRoute(segs, 1, lanTerminalRoutes)
	case "scheduler":
		if len(segs) <= 1 {
			return false
		}
		switch segs[1] {
		case "terminal":
			return isAllowedRoute(segs, 2, lanTerminalRoutes)
		case "executor":
			return isAllowedRoute(segs, 2, lanExecutorRoutes)
		default:
			return false
		}
	default:
		return false
	}
}

// RegistryReq is the request body for local route registry.
type RegistryReq struct {
	ModuleName string `json:"module_name"`
	Port       string `json:"port"`
}

// main is the entry point of the local router service.
func main() {
	var (
		port         int64
		remoteHost   string
		httpProtocol string
		wsProtocol   string
		language     string
	)
	flag.Int64Var(&port, "port", 8003, "listen port")
	flag.StringVar(&remoteHost, "remoteHost", "", "remote host")
	flag.StringVar(&httpProtocol, "httpProtocol", "http", "HTTP scheme: http or https")
	flag.StringVar(&wsProtocol, "wsProtocol", "ws", "WebSocket scheme: ws or wss")
	flag.StringVar(&language, "language", "", "language code to inject into request headers")
	flag.Parse()

	// Parse flags and environment, set port and protocols for this service
	// This section initializes global config based on CLI flags
	log := logrus.New()
	_ = os.MkdirAll("logs", 0755)
	log.SetFormatter(&logrus.JSONFormatter{})
	file, _ := os.OpenFile(path.Join("logs", "route.log"), os.O_CREATE|os.O_WRONLY|os.O_TRUNC, 0666)
	log.SetOutput(io.MultiWriter(file))

	// Create HTTP and WebSocket reverse proxies
	httpProxy := proxy.NewSimpleRpaHttpProxy(
		proxy.WithTargetConfigMap(httpRegister),
		proxy.WithLogger(log),
	)
	wxProxy := proxy.NewSimpleRpaWsProxy(
		proxy.WithTargetConfigMap(wxRegister),
		proxy.WithLogger(log),
	)

	// Register routes and middlewares
	router := gin.Default()
	router.Use(gin.Recovery())
	router.Use(gin.LoggerWithConfig(gin.LoggerConfig{
		Output: log.Out,
	}))
	router.Use(func(c *gin.Context) {
		if !isLocalRequest(c.Request) && !isLanAccessiblePath(c.Request.URL.Path) {
			log.Warnf("deny non-local request remote=%s path=%s", c.Request.RemoteAddr, c.Request.URL.Path)
			c.AbortWithStatusJSON(http.StatusForbidden, gin.H{"msg": "forbidden"})
			return
		}
		c.Next()
	})
	router.Use(cors.New(cors.Config{
		AllowAllOrigins:  true,
		AllowMethods:     []string{"*"},
		AllowHeaders:     []string{"*"},
		ExposeHeaders:    []string{"*"},
		AllowCredentials: true,
		MaxAge:           12 * time.Hour,
	}))
	router.Use(proxy.CookieMiddleware(log))
	if language != "" {
		router.Use(func(c *gin.Context) {
			c.Request.Header.Set("Accept-Language", language)
			c.Next()
		})
	}

	// Register core HTTP and WebSocket proxies for incoming requests
	router.Any("/*path", func(c *gin.Context) {
		if strings.HasPrefix(c.Request.URL.Path, "/rpa-local-route/health") {
			// Health check endpoint
			c.JSON(http.StatusOK, gin.H{"status": "OK"})
			return
		} else if strings.HasPrefix(c.Request.URL.Path, "/rpa-local-route/registry") {
			// Management endpoint for service registry
			var res RegistryReq
			if err := c.ShouldBindJSON(&res); err != nil {
				c.JSON(400, gin.H{
					"msg": err.Error(),
				})
				return
			}
			httpRegister[res.ModuleName] = proxy.ConfigMap{
				ProxyUrl: fmt.Sprintf("http://127.0.0.1:%s", res.Port),
			}
			wxRegister[res.ModuleName] = proxy.ConfigMap{
				ProxyUrl: fmt.Sprintf("ws://127.0.0.1:%s", res.Port),
			}
			c.JSON(http.StatusOK, gin.H{"status": "OK"})
			return
		} else {
			// Proxy endpoint
			if strings.ToLower(c.GetHeader("Upgrade")) == "websocket" {
				wxProxy.ServeHTTP(c.Writer, c.Request)
			} else {
				httpProxy.ServeHTTP(c.Writer, c.Request)
			}
			return
		}
	})

	// Default remote targets; local services can register via /rpa-local-route/registry
	httpRegister["api"] = proxy.ConfigMap{
		ProxyUrl: fmt.Sprintf("%s://%s", httpProtocol, remoteHost),
	}
	wxRegister["api"] = proxy.ConfigMap{
		ProxyUrl: fmt.Sprintf("%s://%s", wsProtocol, remoteHost),
	}

	// Start HTTP server
	_ = router.Run(fmt.Sprintf(":%d", port))
}

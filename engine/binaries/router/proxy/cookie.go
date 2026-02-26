package proxy

import (
	"encoding/json"
	"net/http"
	"net/url"
	"os"
	"path/filepath"
	"regexp"
	"strings"

	"github.com/gin-gonic/gin"
)

// CookieItem describes a persisted cookie entry.
type CookieItem struct {
	KeyValue  string `json:"key_value"`
	CookieKey string `json:"cookie_key"`
	Domain    string `json:"domain"`
	Path      string `json:"path"`
}

var (
	cookieFile  = ".cookie.json"
	cookieStore map[string]map[string]CookieItem
)

// init loads cookies from local file on process start.
func init() {
	if data, err := os.ReadFile(cookieFile); err == nil {
		_ = json.Unmarshal(data, &cookieStore)
	}
	if cookieStore == nil {
		cookieStore = make(map[string]map[string]CookieItem)
	}
}

// AddCookie attaches stored cookies to the outgoing request based on target URL.
func AddCookie(targetUrl string, rw http.ResponseWriter, r *http.Request) {
	parsedUrl, err := url.Parse(targetUrl)
	if err != nil {
		http.Error(rw, "Invalid URL", http.StatusBadRequest)
		return
	}
	domain := parsedUrl.Host
	rw.Header().Set("Cookie-Domain", domain)
	if cookies, ok := cookieStore[domain]; ok {
		var cookieStr string
		for _, cookie := range cookies {
			if cookie.KeyValue == "" {
				continue
			}
			cookieStr += "; " + cookie.KeyValue
		}
		if cookieStr != "" {
			r.Header.Add("Cookie", cookieStr[2:])
		}
	}
}

// CookieMiddleware captures Set-Cookie headers and persists them locally.
func CookieMiddleware(logger Logger) gin.HandlerFunc {
	return func(c *gin.Context) {

		c.Next()

		header := c.Writer.Header()
		// Handle Set-Cookie headers in the response
		cookies := header["Set-Cookie"]
		if len(cookies) == 0 {
			return
		}

		domain := header["Cookie-Domain"][0]
		// Parse and store new cookies for this domain
		for _, cookieStr := range cookies {
			cookie := parseCookie(cookieStr, domain)
			if cookie.Domain == "" {
				continue
			}
			if cookie.CookieKey == "" {
				continue
			}

			// Initialize cookie map for this domain if needed
			if cookieStore[cookie.Domain] == nil {
				cookieStore[cookie.Domain] = make(map[string]CookieItem)
			}
			// Store or update cookie in memory
			cookieStore[cookie.Domain][cookie.CookieKey] = cookie
		}

		logger.Infof("cookie: domain=%s, set=%d", domain, len(cookies))

		// Persist cookie store to file
		if data, err := json.MarshalIndent(cookieStore, "", "  "); err == nil {
			_ = os.MkdirAll(filepath.Dir(cookieFile), 0755)
			_ = os.WriteFile(cookieFile, data, 0644)
		}
	}
}

// parseCookie parses a Set-Cookie string into CookieItem.
func parseCookie(cookieStr string, domain string) CookieItem {
	cookie := CookieItem{Domain: domain}
	parts := strings.Split(cookieStr, ";")

	// Use regexp to match key-value pair
	pattern := regexp.MustCompile(`([^;\s]+)=([^;\s]+)`)
	matches := pattern.FindAllStringSubmatch(parts[0], -1)

	if len(matches) > 0 {
		key := matches[0][1]
		value := matches[0][2]
		cookie.CookieKey = key
		cookie.KeyValue = key + "=" + value
	}

	// Parse other attributes such as domain and path
	for _, part := range parts[1:] {
		part = strings.TrimSpace(part)
		attr := strings.SplitN(part, "=", 2)
		if len(attr) != 2 {
			continue
		}
		key := attr[0]
		value := attr[1]

		switch key {
		case "domain":
			cookie.Domain = value
		case "path":
			cookie.Path = value
		}
	}

	return cookie
}

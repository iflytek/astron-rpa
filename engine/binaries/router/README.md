### Overview

This module provides a lightweight HTTP and WebSocket reverse proxy used by the local RPA route service.

### Manual build

```bash
set GOOS=windows
set GOARCH=amd64
set CGO_ENABLED=0
go build -ldflags="-s -w" -o astron_router.exe .
```

### Compatibility

- ✅ Go 1.20
- ✅ Windows 7 SP1
- ✅ Windows 8/8.1
- ✅ Windows 10/11
- ✅ 32-bit and 64-bit architectures
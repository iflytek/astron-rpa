# RISC-V (`linux/riscv64`) support

## Current scope

RISC-V support is incremental and currently applies only to the server-side
`resource-service` image. It does not add RISC-V support for the Astron RPA
Windows desktop client or automation engine, and it does not make the complete
Docker Compose stack supported on RISC-V.

| Component | `linux/riscv64` status | Notes |
| --- | --- | --- |
| `resource-service` | Supported image path | The architecture-neutral Java 21 JAR is built on the Buildx host and copied into a target-architecture Eclipse Temurin runtime. |
| `ai-service` and `openapi-service` | Not yet verified | Python 3.13 native dependencies and the bundled wheel require an architecture audit. |
| `robot-service` and `rpa-auth` | Not yet verified | Their Java 8 build/runtime images require a separate RISC-V compatibility path. |
| MySQL, Redis, MinIO, Casdoor, Atlas, and OpenResty | Not yet verified as a stack | Each external image and its runtime behavior must be checked on the target system. |
| Windows desktop client and automation engine | Unsupported | These components depend on Windows desktop and UI automation capabilities and are outside this server-image adaptation. |
| Complete Compose deployment | Unsupported | Do not deploy `docker/docker-compose.yml` unchanged as a supported RISC-V stack. |

## Build the supported image

Run the build from the repository root. Register a RISC-V QEMU handler first
when the Buildx host is not RISC-V:

```bash
docker run --privileged --rm tonistiigi/binfmt --install riscv64
docker buildx create --use --name astron-rpa-riscv64

docker buildx build \
  --platform linux/riscv64 \
  --file backend/resource-service/Dockerfile \
  --tag astron-rpa/resource-service:riscv64 \
  --load \
  .
```

The backend publishing workflow produces `resource-service` for
`linux/amd64`, `linux/arm64`, and `linux/riscv64`. The other backend service
jobs retain the existing AMD64/ARM64 platform list.

## Build design

The Maven stage runs on `$BUILDPLATFORM` because the Spring Boot JAR is
architecture-neutral. Only the Eclipse Temurin Java 21 runtime stage targets
`linux/riscv64`. This avoids emulating dependency resolution and compilation
while preserving the existing application entry point and JVM options.

## Verification boundary

The pull-request workflow builds and loads the target image, checks its OCI
architecture metadata, and executes the Java runtime under RISC-V emulation.
This is a component-image guardrail, not a full application integration test.

A native RISC-V smoke test with the database, cache, object storage,
authentication service, reverse proxy, and an RPA client remains required
before claiming end-to-end or production support.

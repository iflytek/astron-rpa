# @rpa/cli

CLI tool for Astron RPA development.

## Installation

You can install this package globally or locally in your project.

```bash
# Global installation
npm install -g @rpa/cli
# or
pnpm add -g @rpa/cli

# Local installation
npm install @rpa/cli --save-dev
# or
pnpm add @rpa/cli -D
```

## Usage

### Commands

#### `rpa dev`

Start the development server.

```bash
rpa dev
```

#### `rpa build`

Build the library for production.

**Options:**
- `-w, --watch`: Turn on watch mode, watch for changes and rebuild.

```bash
rpa build
# Build with watch mode
rpa build --watch
```

#### `rpa create`

Create a new plugin template.

**Options:**
- `-n, --name [name]`: Plugin name.
- `-t, --target [dir]`: Target directory to scaffold into.

If options are not provided, an interactive prompt will guide you.

```bash
rpa create
# or specify arguments
rpa create --name my-plugin --target ./packages/my-plugin
```

### Global Options

- `--debug [feat]`: Show debug logs.
- `--help`: Show help information.
- `--version`: Show version number.

## Development

If you are developing this CLI package itself:

```bash
# Install dependencies
pnpm install

# Build the CLI
pnpm build

# Run type check
pnpm typecheck

# Watch mode for development
pnpm dev
```

## License

ISC
